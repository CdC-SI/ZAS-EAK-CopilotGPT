from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from ..models import MessageData, ConversationData
from ..interfaces.storage import BaseStorage, DatabaseStorage


class BaseMemoryStrategy(ABC):
    """Base class for all memory strategies."""

    def __init__(
        self,
        cache_storage: BaseStorage,
        db_storage: DatabaseStorage,
        k_memory: int,
    ):
        self.cache = cache_storage
        self.db = db_storage
        self.k_memory = k_memory

    @abstractmethod
    def add_message_to_memory(
        self,
        db: Session,
        message: MessageData,
    ):
        """Add a message to the memory strategy."""
        pass

    @abstractmethod
    async def get_conversational_memory(
        self,
        db: Session,
        user_uuid: str,
        conversation_uuid: str,
        k_memory: int,
    ) -> ConversationData:
        """Get the conversational memory for the user and conversation."""
        pass

    def store(self, db: Session, message: MessageData):
        """Coordinated store operation that updates both cache and database."""
        self.cache.store_message(message)
        self.db.index_chat_history(db, message)

    def conversation_uuid_exists(
        self, db: Session, conversation_uuid: str
    ) -> bool:
        return self.db.conversation_uuid_exists(db, conversation_uuid)

    def index_chat_title(
        self, db: Session, user_uuid: str, conversation_uuid: str, title: str
    ) -> None:
        self.db.index_chat_title(db, user_uuid, conversation_uuid, title)
