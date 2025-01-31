from sqlalchemy.orm import Session

from .base import BaseMemoryStrategy
from ..interfaces.storage import BaseStorage, DatabaseStorage
from ..models import MessageData, ConversationData


class ConversationalMemoryBuffer(BaseMemoryStrategy):
    """Class implementing the Conversational Memory Buffer."""

    def __init__(
        self,
        cache_storage: BaseStorage,
        db_storage: DatabaseStorage,
        k_memory: int,
    ):
        super().__init__(cache_storage, db_storage, k_memory)

    def add_message_to_memory(self, db: Session, message: MessageData):
        self.store(db, message)

    def get_conversational_memory(
        self, user_uuid: str, conversation_uuid: str, k_memory: int
    ) -> ConversationData:
        if not (user_uuid and conversation_uuid):
            return ConversationData(
                conversation_uuid=conversation_uuid, turns=[]
            )

        return self.cache.get_conversation(
            user_uuid, conversation_uuid, k_memory
        )
