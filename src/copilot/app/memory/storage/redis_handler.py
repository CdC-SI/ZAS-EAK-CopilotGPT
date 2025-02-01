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
                current_turn = ConversationTurn(user_message=message)
            elif message.role == MessageRole.ASSISTANT and current_turn:
                current_turn.assistant_message = message
                turns.append(current_turn)
                current_turn = None

        # Apply k_memory limit
        if k_memory != -1:
            turns = turns[-k_memory:]

        return ConversationData(
            conversation_uuid=conversation_uuid, turns=turns
        )
