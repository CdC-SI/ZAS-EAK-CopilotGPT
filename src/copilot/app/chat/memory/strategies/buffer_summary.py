from typing import List, Optional
from sqlalchemy.orm import Session

from .base import BaseMemoryStrategy
from ..interfaces.storage import BaseStorage, DatabaseStorage


class ConversationalMemoryBufferSummary(BaseMemoryStrategy):
    """Class implementing the Conversational Memory Buffer Summary."""

    def __init__(
        self,
        cache_storage: BaseStorage,
        db_storage: DatabaseStorage,
        k_memory: int = -1,
    ):
        super().__init__(cache_storage, db_storage, k_memory)

    def add_message_to_memory(
        self,
        db: Session,
        user_uuid: str,
        conversation_uuid: str,
        message_uuid: str,
        role: str,
        message: str,
        language: str,
        url: Optional[str] = None,
        faq_id: Optional[int] = None,
        retrieved_doc_ids: Optional[List[int]] = None,
    ):
        # TODO: Implement buffer summary strategy
        pass

    def get_conversational_memory(
        self, user_uuid: str, conversation_uuid: str, k_memory: int
    ) -> str:
        # TODO: Implement buffer summary formatting
        return ""
