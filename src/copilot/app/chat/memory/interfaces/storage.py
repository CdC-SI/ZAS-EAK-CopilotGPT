from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from ..models import MessageData, ConversationData


class BaseStorage(ABC):
    """Abstract base class for memory storage operations."""

    @abstractmethod
    def store_message(self, message: MessageData) -> None:
        """Store a message in the storage system."""
        pass

    @abstractmethod
    def get_conversation(
        self,
        db: Session,
        user_uuid: str,
        conversation_uuid: str,
        k_memory: int,
    ) -> ConversationData:
        """Retrieve conversation history from storage."""
        pass


class DatabaseStorage(ABC):
    """Abstract base class for database storage operations."""

    @abstractmethod
    def index_chat_history(self, db: Session, message: MessageData) -> None:
        """Index chat history in the database."""
        pass

    @abstractmethod
    def conversation_uuid_exists(
        self, db: Session, conversation_uuid: str
    ) -> bool:
        """Check if a conversation UUID exists in the database."""
        pass

    @abstractmethod
    def index_chat_title(
        self, db: Session, user_uuid: str, conversation_uuid: str, title: str
    ) -> None:
        """Index chat title in the database."""
        pass


class UnifiedStorage(BaseStorage, DatabaseStorage):
    """
    Unified interface combining both cache and database storage operations.
    Implementations should coordinate between temporary and persistent storage.
    """

    pass
