from typing import Optional
import datetime
from redis import Redis, RedisError
import logging

from ..interfaces.storage import BaseStorage
from ..exceptions import RedisStorageError
from ..models import MessageData, ConversationData, ConversationTurn
from ..config import RedisConfig
from ..enums import MessageRole

logger = logging.getLogger(__name__)


class RedisMemoryHandler(BaseStorage):
    def __init__(
        self, k_memory: int = 1, config: Optional[RedisConfig] = None
    ):
        self.k_memory = k_memory
        config = config or RedisConfig()

        try:
            self.redis_client = Redis(
                host=config.host,
                port=config.port,
                db=config.db,
                password=config.password,
                decode_responses=config.decode_responses,
            )
        except RedisError as e:
            raise RedisStorageError(
                f"Failed to initialize Redis connection: {e}"
            )

    def clean_cache(self, user_uuid: str, conversation_uuid: str) -> None:
        key = f"user:{user_uuid}:conversation:{conversation_uuid}:*"
        self.redis_client.expire(
            key, 60 * 60 * 24
        )  # 24 hours expiration -> load from postgres after 24 hours
        self.redis_client.flushdb()

    def store_message(self, message: MessageData) -> None:
        message_data = message.dict()
        key = f"user:{message.user_uuid}:conversation:{message.conversation_uuid}:{message.message_uuid}"

        # Debug logging
        logger.debug(f"Message data before conversion: {message_data}")

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

        logger.debug(f"Message data after conversion: {message_data}")

        try:
            self.redis_client.hset(key, mapping=message_data)
        except RedisError as e:
            logger.error(f"Redis storage error with data: {message_data}")
            raise RedisStorageError(f"Failed to store message in Redis: {e}")

    def get_conversation(
        self, user_uuid: str, conversation_uuid: str, k_memory: int
    ) -> ConversationData:
        pattern = f"user:{user_uuid}:conversation:{conversation_uuid}:*"
        keys = self.redis_client.keys(pattern)

        messages = []
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
                    doc_ids_str = message_data["retrieved_doc_ids"].strip("[]")
                    message_data["retrieved_doc_ids"] = [
                        int(id.strip())
                        for id in doc_ids_str.split(",")
                        if id.strip()
                    ]
                except (ValueError, AttributeError):
                    message_data["retrieved_doc_ids"] = None

            # Convert timestamp string back to datetime
            if message_data.get("timestamp"):
                message_data["timestamp"] = datetime.datetime.fromisoformat(
                    message_data["timestamp"]
                )

            messages.append(MessageData(**message_data))

        # Sort by timestamp
        messages.sort(key=lambda msg: msg.timestamp)

        # Group into turns
        turns = []
        current_turn = None

        for message in messages:
            if message.role == MessageRole.USER.value:
                current_turn = ConversationTurn(user_message=message)
            elif message.role == MessageRole.ASSISTANT.value and current_turn:
                current_turn.assistant_message = message
                turns.append(current_turn)
                current_turn = None

        # Apply k_memory limit
        if k_memory != -1:
            turns = turns[-k_memory:]

        return ConversationData(
            conversation_uuid=conversation_uuid, turns=turns
        )
