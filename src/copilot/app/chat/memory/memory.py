from typing import Optional

from .config import StorageConfig
from sqlalchemy.orm import Session

from .enums import MemoryType
from .models import MessageData, ConversationData
from .factories import MemoryStrategyFactory
from .interfaces.storage import BaseStorage, DatabaseStorage
from .exceptions import MemoryStrategyError


class ConversationalMemory:
    """
    Class implementing the selected Conversational Memory.
    Creates and manages memory strategies with their required storage handlers.
    """

    def __init__(
        self,
        memory_type: MemoryType,
        k_memory: int,
        config: Optional[StorageConfig] = None,
        cache_storage: Optional[BaseStorage] = None,
        db_storage: Optional[DatabaseStorage] = None,
    ):
        """
        Initialize ConversationalMemory with optional configuration and storage handlers.

        Args:
            memory_type: Type of memory strategy to use
            k_memory: Number of conversation turns to remember
            config: Optional storage configuration
            cache_storage: Optional custom cache storage implementation
            db_storage: Optional custom database storage implementation
        """
        self.k_memory = k_memory

        try:
            self.memory_instance = MemoryStrategyFactory.create_strategy(
                memory_type=memory_type,
                k_memory=k_memory,
                cache_storage=cache_storage,
                db_storage=db_storage,
                config=config,
            )
        except Exception as e:
            raise MemoryStrategyError(
                f"Failed to initialize memory strategy: {e}"
            )

    def add_message(self, db: Session, message: MessageData) -> None:
        """Add a message to the current memory strategy."""
        self.memory_instance.add_message_to_memory(db, message)

    def get_conversation(
        self, db: Session, user_uuid: str, conversation_uuid: str
    ) -> ConversationData:
        """Get the conversation using the current memory strategy."""
        return self.memory_instance.get_conversational_memory(
            db, user_uuid, conversation_uuid, self.k_memory
        )
