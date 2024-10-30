import os
from dotenv import load_dotenv
from typing import List, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from redis import Redis

from database.models import ChatHistory, ChatTitle

# Load environment variables
load_dotenv()
REDIS_PW = os.getenv("REDIS_PASSWORD", None)
REDIS_HOST = os.getenv("REDIS_HOST", None)
REDIS_PORT = os.getenv("REDIS_PORT", None)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RedisMemoryHandler:

    def __init__(self, k_memory: int = 1):
        self.k_memory = k_memory
        self.redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PW, decode_responses=True)

    def clean_cache(self, user_uuid: str, conversation_uuid: str):
        """
        Method to clean the Redis cache
        """
        key = f"user:{user_uuid}:conversation:{conversation_uuid}:*"
        self.redis_client.expire(key, 60 * 60 * 24)  # 24 hours expiration
        self.redis_client.flushdb()

    # TO DO: run this method in a separate thread
    def store_message(self, user_uuid: str, conversation_uuid: str, message_uuid: str, role: str, message: str):
        """
        Method to store a message in Redis
        """
        # Create a hash for the message
        message_data = {
            'user_uuid': user_uuid,
            'conversation_uuid': conversation_uuid,
            'message_uuid': message_uuid,
            'role': role,
            'message': message,
            'timestamp': datetime.now().isoformat(),
        }

        # Store message in Redis with key `user:{user_uuid}:conversation:{conversation_uuid}`
        key = f"user:{user_uuid}:conversation:{conversation_uuid}:{message_uuid}"
        self.redis_client.hset(key, mapping=message_data)

        # Index message to postgres in the background
        # future = executor.submit(self.save_chat_history, db=db, user_uuid=user_uuid, conversation_uuid=conversation_uuid, role=role, message=message)
        # try:
        #     result = future.result()  # This will raise any exceptions that occurred
        # except Exception as e:
        #     logging.error(f"Exception in thread: {e}")

    # TO DO: Retrieve conversation from Postgres if cache cleared
    def retrieve_conversation(self, user_uuid: str, conversation_uuid: str, k_memory: int) -> List[dict]:
        """
        Method to retrieve a conversation from Redis based on user_uuid and conversation_uuid
        """
        pattern = f"user:{user_uuid}:conversation:{conversation_uuid}:*"
        keys = self.redis_client.keys(pattern)

        conversation = []
        for key in keys:
            message_data = self.redis_client.hgetall(key)
            conversation.append(message_data)

        # Sort by timestamp
        conversation.sort(key=lambda msg: msg['timestamp'])

        # Group conversation into turns
        turns = []
        current_turn = []

        for message in conversation:
            current_turn.append({message["role"]: message["message"]})
            if message["role"] == "assistant":
                turns.append(current_turn)
                current_turn = []

        # Retrieve the last `k_memory` turns
        # When k is passed as a param, check if k==None
        if k_memory:
            turns = turns[-k_memory:]
        else:
            turns = turns[-self.k_memory:]

        flattened_turns = [msg for turn in turns for msg in turn]

        return flattened_turns

class PostgresMemoryHandler:

    # TO DO: Make this method async
    def index_chat_history(self, db: Session, user_uuid: str = None, conversation_uuid: str = None, message_uuid: str = None, role: str = None, message: str = None, language: str = None, url: Optional[str] = None, faq_id: Optional[int] = None, retrieved_doc_ids: Optional[List[int]] = None):
        """
        Method to index the chat history in the Postgres "chat_history" table.
        """
        chat_history = ChatHistory(
            user_uuid=user_uuid,
            conversation_uuid=conversation_uuid,
            message_uuid=message_uuid,
            role=role,
            message=message,
            url=url,
            language=language,
            faq_id=faq_id,
            retrieved_docs=retrieved_doc_ids,
            timestamp=datetime.now()
        )
        try:
            db.add(chat_history)
            db.commit()
        except Exception as e:
            logger.error("Error indexing chat history: %s", e)
            db.rollback()

    # TO DO: Make this method async
    # OPTIMIZE: Check once instead of checking at each conversation turn?
    def conversation_uuid_exists(self, db: Session, conversation_uuid: str) -> bool:
        """
        Method to check if conversation_uuid exists in chat_title table.
        """
        result = db.execute(select(ChatTitle).filter_by(conversation_uuid=conversation_uuid))
        return result.scalars().first() is not None

    # TO DO: Make this method async
    def index_chat_title(self, db: Session, user_uuid: str, conversation_uuid: str, title: str):
        """
        Method to index the chat title in the Postgres "chat_title" table.
        """
        chat_title = ChatTitle(
            user_uuid=user_uuid,
            conversation_uuid=conversation_uuid,
            chat_title=title
        )
        try:
            db.add(chat_title)
            db.commit()
        except Exception as e:
            logger.error("Error indexing chat history: %s", e)
            db.rollback()

class BaseMemory(RedisMemoryHandler, PostgresMemoryHandler):
    """
    Base class for the Conversational Memory.
    """
    def __init__(self, k_memory: int):
        RedisMemoryHandler.__init__(self, k_memory)

    def store(self, db: Session, user_uuid: str, conversation_uuid: str, message_uuid: str, role: str, message: str, language: str, url: Optional[str] = None, faq_id: Optional[int] = None, retrieved_doc_ids: Optional[List[int]] = None):
        """
        Method to store a message in Redis and index it in Postgres.
        """
        self.store_message(user_uuid, conversation_uuid, message_uuid, role, message)

        # Note: make this async with AsyncSession db
        self.index_chat_history(db, user_uuid, conversation_uuid, message_uuid, role, message, language, url, faq_id, retrieved_doc_ids)

    def fetch(self, user_uuid: str, conversation_uuid: str, k_memory: int):
        """
        Method to fetch the conversation from Redis.
        """
        return self.retrieve_conversation(user_uuid, conversation_uuid, k_memory)

class ConversationalMemoryBuffer(BaseMemory):
    """
    Class implementing the Conversational Memory Buffer. Will track the last `k_memory` turns of the conversation.
    """
    def __init__(self, k_memory: int):
        super().__init__(k_memory)

    def add_message_to_memory(self, db: Session, user_uuid: str, conversation_uuid: str, message_uuid: str, role: str, message: str, language: str, url: Optional[str] = None, faq_id: Optional[int] = None, retrieved_doc_ids: Optional[List[int]] = None):
        """
        Method to add a message to the memory buffer and index it in the Postgres DB.
        """
        self.store(db, user_uuid, conversation_uuid, message_uuid, role, message, language, url, faq_id, retrieved_doc_ids)

    def fetch_from_memory(self, user_uuid: str, conversation_uuid: str, k_memory: int):
        """
        Method to fetch the conversation from the memory buffer.
        """
        return self.fetch(user_uuid, conversation_uuid, k_memory)

class ConversationalMemorySummary(BaseMemory):
    """
    Class implementing the Conversational Memory Summary. Will provide a summary of the conversation history.
    """
    def __init__(self):
        pass

    def add_message_to_memory(self, db: Session, user_uuid: str, conversation_uuid: str, role: str, message: str, language: str, url: Optional[str] = None, faq_id: Optional[int] = None, retrieved_doc_ids: Optional[List[int]] = None):
        self.store(db, user_uuid, conversation_uuid, role, message, language, url, faq_id, retrieved_doc_ids)

    def fetch_from_memory(self, user_uuid: str, conversation_uuid: str, k_memory: int):
        conversation_history = self.fetch(user_uuid, conversation_uuid, k_memory)
        # Logic to create summary here OR ADD STATE TO TRACK SUMMARY

class ConversationalMemoryBufferSummary(BaseMemory):
    """
    Class implementing the Conversational Memory Buffer Summary. Will provide a summary of the last `k_memory` - 1 turns of the conversation and the previous turn.
    """
    def __init__(self):
        pass

    def add_message_to_memory(self, message: str):
        pass

class ConversationalMemory:
    """
    Class implementing the selected Conversational Memory.
    Saves conversation turns to Redis DB with `user_uuid`, `conversation_uuid`, `role`, `message`, and `timestamp`.
    Saves entire chat history to Postgres DB with `user_uuid`, `conversation_uuid`, `role`, `message`, `timestamp`, and `retrieved_doc_ids`.
    Saves and generates current chat title to Postgres DB with `user_uuid`, `conversation_uuid`, and `chat_title`.
    """
    def __init__(self, memory_type: str, k_memory: int):
        self.k_memory = k_memory
        self.memory_instance = self._initialize_memory(memory_type, k_memory)

    def _initialize_memory(self, memory_type: str, k_memory: int):
        memory_types = {
            "buffer": ConversationalMemoryBuffer,
            "summary": ConversationalMemorySummary,
            "buffer_summary": ConversationalMemoryBufferSummary,
        }
        if memory_type in memory_types:
            return memory_types[memory_type](k_memory) if memory_type == "buffer" else memory_types[memory_type]()
        else:
            raise ValueError("Invalid memory type selected.")
