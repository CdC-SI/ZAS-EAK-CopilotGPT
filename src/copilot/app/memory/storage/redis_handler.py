import ast
import json
from typing import Optional
import datetime
from redis import Redis, RedisError
import logging
from sqlalchemy.orm import Session
from .postgres_handler import PostgresMemoryHandler

from ..interfaces.storage import BaseStorage
from ..exceptions import RedisStorageError
from ..models import MessageData, ConversationData, ConversationTurn
from ..config import RedisConfig
from ..enums import MessageRole

from database.models import UserPreferences

logger = logging.getLogger(__name__)


class RedisMemoryHandler(BaseStorage):
    def __init__(
        self,
        k_memory: int = 1,
        config: Optional[RedisConfig] = None,
        postgres_handler: Optional[PostgresMemoryHandler] = None,
    ):
        self.k_memory = k_memory
        self.postgres_handler = postgres_handler or PostgresMemoryHandler()
        self.config = config or RedisConfig()

        try:
            self.redis_client = Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                decode_responses=self.config.decode_responses,
            )
        except RedisError as e:
            raise RedisStorageError(
                f"Failed to initialize Redis connection: {e}"
            )

    def store_message(self, message: MessageData) -> None:
        message_data = message.dict()
        key = f"user:{message.user_uuid}:conversation:{message.conversation_uuid}:{message.message_uuid}"

        # Convert all fields to appropriate string representations
        for k, v in message_data.items():
            if v is None:
                message_data[k] = ""
            elif isinstance(v, MessageRole):
                message_data[k] = v.value
            elif isinstance(v, datetime.datetime):
                message_data[k] = v.isoformat()
            elif isinstance(v, (list, dict)):
                message_data[k] = str(v)
            else:
                message_data[k] = str(v)

        try:
            self.redis_client.hset(key, mapping=message_data)
            # Set TTL for the message using config
            self.redis_client.expire(key, self.config.cache_ttl_seconds)
        except RedisError as e:
            logger.error(f"Redis storage error with data: {message_data}")
            raise RedisStorageError(f"Failed to store message in Redis: {e}")

    def get_conversation(
        self,
        db: Session,
        user_uuid: str,
        conversation_uuid: str,
        k_memory: int,
    ) -> ConversationData:
        pattern = f"user:{user_uuid}:conversation:{conversation_uuid}:*"
        keys = self.redis_client.keys(pattern)

        messages = []
        if not keys and db is not None:
            # Fallback to postgres if no messages in Redis
            try:
                messages = self.postgres_handler.get_conversation_history(
                    db, user_uuid, conversation_uuid
                )
                # Store retrieved messages in Redis for future access
                for message in messages:
                    self.store_message(message)
            except Exception as e:
                logger.error(f"Failed to retrieve from postgres: {e}")
                raise
        else:
            # Existing Redis retrieval logic
            for key in keys:
                message_data = self.redis_client.hgetall(key)

                # Convert empty strings to None for optional fields
                if message_data.get("faq_id") == "":
                    message_data["faq_id"] = None
                elif message_data.get("faq_id"):
                    message_data["faq_id"] = int(message_data["faq_id"])

                # Handle sources
                if message_data.get("sources") == "":
                    message_data["sources"] = []
                elif message_data.get("sources"):
                    try:
                        sources_str = message_data["sources"].strip()
                        message_data["sources"] = ast.literal_eval(sources_str)
                    except (ValueError, AttributeError):
                        message_data["sources"] = []

                # Handle retrieved_doc_ids
                if message_data.get("retrieved_doc_ids") == "":
                    message_data["retrieved_doc_ids"] = None
                elif message_data.get("retrieved_doc_ids"):
                    # Convert string representation of list back to list of integers
                    try:
                        doc_ids_str = message_data["retrieved_doc_ids"].strip(
                            "[]"
                        )
                        message_data["retrieved_doc_ids"] = [
                            int(id.strip())
                            for id in doc_ids_str.split(",")
                            if id.strip()
                        ]
                    except (ValueError, AttributeError):
                        message_data["retrieved_doc_ids"] = None

                # Convert timestamp string back to datetime
                if message_data.get("timestamp"):
                    message_data["timestamp"] = (
                        datetime.datetime.fromisoformat(
                            message_data["timestamp"]
                        )
                    )

                messages.append(MessageData(**message_data))

        # Sort by timestamp
        messages.sort(key=lambda msg: msg.timestamp)

        # Group into turns
        turns = []
        current_turn = None

        for message in messages:
            if message.role == MessageRole.USER:
                # If there's an existing turn with only a user message, add it to turns
                if (
                    current_turn
                    and current_turn.user_message
                    and not current_turn.assistant_message
                ):
                    turns.append(current_turn)
                current_turn = ConversationTurn(user_message=message)
            elif message.role == MessageRole.ASSISTANT and current_turn:
                current_turn.assistant_message = message
                turns.append(current_turn)
                current_turn = None

        # Add the last turn if it only contains a user message
        if current_turn and current_turn.user_message:
            turns.append(current_turn)

        # Apply k_memory limit
        if k_memory != -1:
            turns = turns[-k_memory:]

        return ConversationData(
            conversation_uuid=conversation_uuid, turns=turns
        )

    def get_all_user_conversations(
        self, db: Session, user_uuid: str
    ) -> list[ConversationData]:
        """
        Retrieve all conversations for a given user from Redis or fallback to Postgres.

        Args:
            db: Database session
            user_uuid: UUID of the user

        Returns:
            List of ConversationData objects containing structured conversations

        Raises:
            RedisStorageError: If Redis query fails
        """
        pattern = f"user:{user_uuid}:conversation:*"
        keys = self.redis_client.keys(pattern)
        messages = []

        if not keys and db is not None:
            # Fallback to postgres if no messages in Redis
            try:
                messages = self.postgres_handler.get_all_user_conversations(
                    db, user_uuid
                )
                # Store retrieved messages in Redis for future access
                for message in messages:
                    self.store_message(message)
            except Exception as e:
                logger.error(f"Failed to retrieve from postgres: {e}")
                raise
        else:
            try:
                for key in keys:
                    message_data = self.redis_client.hgetall(key)
                    if not message_data:
                        continue

                    # Handle data conversion as before
                    if message_data.get("faq_id") == "":
                        message_data["faq_id"] = None
                    elif message_data.get("faq_id"):
                        message_data["faq_id"] = int(message_data["faq_id"])

                    # Convert sources
                    if message_data.get("sources") == "":
                        message_data["sources"] = []
                    elif message_data.get("sources"):
                        try:
                            message_data["sources"] = ast.literal_eval(
                                message_data["sources"]
                            )
                        except (ValueError, AttributeError):
                            message_data["sources"] = []

                    # Convert retrieved_doc_ids
                    if message_data.get("retrieved_doc_ids") == "":
                        message_data["retrieved_doc_ids"] = None
                    elif message_data.get("retrieved_doc_ids"):
                        try:
                            doc_ids_str = message_data[
                                "retrieved_doc_ids"
                            ].strip("[]")
                            message_data["retrieved_doc_ids"] = [
                                int(id.strip())
                                for id in doc_ids_str.split(",")
                                if id.strip()
                            ]
                        except (ValueError, AttributeError):
                            message_data["retrieved_doc_ids"] = None

                    # Convert timestamp
                    if message_data.get("timestamp"):
                        message_data["timestamp"] = (
                            datetime.datetime.fromisoformat(
                                message_data["timestamp"]
                            )
                        )

                    messages.append(MessageData(**message_data))

            except RedisError as e:
                logger.error(f"Redis retrieval error: {e}")
                raise RedisStorageError(
                    f"Failed to retrieve messages from Redis: {e}"
                )

        # Group messages by conversation_uuid
        conversations_dict = {}
        for message in messages:
            if message.conversation_uuid not in conversations_dict:
                conversations_dict[message.conversation_uuid] = []
            conversations_dict[message.conversation_uuid].append(message)

        # Create ConversationData objects
        conversations = []
        for conv_uuid, conv_messages in conversations_dict.items():
            # Sort messages by timestamp
            conv_messages.sort(key=lambda x: x.timestamp)

            # Group into turns
            turns = []
            current_turn = None

            for message in conv_messages:
                if message.role == MessageRole.USER:
                    if (
                        current_turn
                        and current_turn.user_message
                        and not current_turn.assistant_message
                    ):
                        turns.append(current_turn)
                    current_turn = ConversationTurn(user_message=message)
                elif message.role == MessageRole.ASSISTANT and current_turn:
                    current_turn.assistant_message = message
                    turns.append(current_turn)
                    current_turn = None

            # Add the last turn if it only contains a user message
            if current_turn and current_turn.user_message:
                turns.append(current_turn)

            conversations.append(
                ConversationData(
                    conversation_uuid=conv_uuid,
                    turns=turns,
                )
            )

        return conversations

    def get_user_preferences(self, db: Session, user_uuid: str) -> dict:
        """
        Get user preferences from Redis cache or fallback to Postgres.

        Args:
            db: Database session
            user_uuid: UUID of the user

        Returns:
            dict: User preferences dictionary or None if not found

        Raises:
            RedisStorageError: If Redis operation fails
        """
        redis_key = f"user_preferences:{user_uuid}"

        try:
            # Try Redis first
            preferences = {}
            str_preferences = self.redis_client.hgetall(redis_key)

            if str_preferences:
                for key, value in str_preferences.items():
                    try:
                        # Try to parse as JSON first
                        preferences[key] = json.loads(value)
                    except json.JSONDecodeError:
                        try:
                            # Fallback to literal_eval if not valid JSON
                            preferences[key] = ast.literal_eval(value)
                        except (ValueError, SyntaxError) as e:
                            logger.error(
                                f"Failed to parse preference value for {key}: {e}"
                            )
                            # Skip this value if we can't parse it
                            continue
                return preferences if preferences else None

        except RedisError as e:
            logger.error(
                f"Redis error while fetching preferences for user {user_uuid}: {str(e)}"
            )

        # Fallback to postgres if not in Redis
        if db is not None:
            try:
                db_prefs = (
                    db.query(UserPreferences)
                    .filter(UserPreferences.user_uuid == user_uuid)
                    .first()
                )
                if db_prefs:
                    # Cache in Redis for future requests - use json.dumps for nested structures
                    try:
                        redis_data = {
                            k: json.dumps(v)
                            for k, v in db_prefs.user_preferences.items()
                        }
                        self.redis_client.hset(redis_key, mapping=redis_data)
                        # self.redis_client.expire(redis_key, self.config.cache_ttl_seconds)
                    except RedisError as e:
                        logger.error(
                            f"Failed to cache preferences in Redis: {str(e)}"
                        )

                    return db_prefs.user_preferences
            except Exception as e:
                logger.error(
                    f"Database error while fetching preferences: {str(e)}"
                )
                raise

        return None
