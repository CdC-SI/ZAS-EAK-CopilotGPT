from sqlalchemy.orm import Session

from .base import BaseMemoryStrategy
from ..interfaces.storage import BaseStorage, DatabaseStorage
from ..models import MessageData, ConversationData
from chat.messages import MessageBuilder
from config.clients_config import clientLLM


class ConversationalMemorySummary(BaseMemoryStrategy):
    """Class implementing the Conversational Memory Summary."""

    def __init__(
        self,
        cache_storage: BaseStorage,
        db_storage: DatabaseStorage,
        k_memory: int = -1,
    ):
        super().__init__(cache_storage, db_storage, k_memory)
        self.message_builder = MessageBuilder()
        self.llm_client = clientLLM

    def add_message_to_memory(self, db: Session, message: MessageData):
        self.store(db, message)

    async def get_conversational_memory(
        self,
        db: Session,
        user_uuid: str,
        conversation_uuid: str,
        k_memory: int,
    ) -> ConversationData:
        if not (user_uuid and conversation_uuid):
            return ConversationData(
                conversation_uuid=conversation_uuid, turns=[]
            )

        return self.cache.get_conversation(
            db, user_uuid, conversation_uuid, k_memory
        )

    async def get_formatted_conversation(
        self,
        db: Session,
        user_uuid: str,
        conversation_uuid: str,
        k_memory: int,
    ) -> str:
        """
        Get formatted conversation from memory.
        """

        conversational_memory = await self.get_conversational_memory(
            db, user_uuid, conversation_uuid, k_memory
        )

        if not conversational_memory.turns:
            return ""

        messages = self.message_builder.build_conversation_summary_prompt(
            llm_model="gpt-4o-mini",
            language="fr",
            conversational_memory=conversational_memory.format(),
        )

        # TO DO: update LLM config and abstract classes
        res = await self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            stream=False,
            temperature=0.0,
            top_p=0.95,
            max_tokens=512,
            messages=messages,
        )

        return res.choices[0].message.content
