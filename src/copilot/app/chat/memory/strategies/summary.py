from sqlalchemy.orm import Session

from .base import BaseMemoryStrategy
from ..interfaces.storage import BaseStorage, DatabaseStorage
from ..models import MessageData, ConversationData


class ConversationalMemorySummary(BaseMemoryStrategy):
    """Class implementing the Conversational Memory Summary."""

    def __init__(
        self,
        cache_storage: BaseStorage,
        db_storage: DatabaseStorage,
        k_memory: int = -1,
    ):
        super().__init__(cache_storage, db_storage, k_memory)

    def add_message_to_memory(self, db: Session, message: MessageData):
        self.store(db, message)

    def get_conversational_memory(
        self, user_uuid: str, conversation_uuid: str, k_memory: int
    ) -> ConversationData:
        # TODO: Implement summary generation
        return ConversationData(conversation_uuid=conversation_uuid, turns=[])
