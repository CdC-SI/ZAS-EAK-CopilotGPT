from sqlalchemy.orm import Session

from .base import BaseMemoryStrategy
from ..interfaces.storage import BaseStorage, DatabaseStorage
from ..models import MessageData, ConversationData
from ..enums import MessageRole


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
        """
        Add a message to the conversation memory.

        Parameters
        ----------
        db : Session
            Database session object
        message : MessageData
            Message data to be stored in memory
        """
        self.store(db, message)

    async def get_conversational_memory(
        self,
        db: Session,
        user_uuid: str,
        conversation_uuid: str,
        k_memory: int,
    ) -> ConversationData:
        """
        Retrieve conversation memory for a specific user and conversation.

        Parameters
        ----------
        db : Session
            Database session object
        user_uuid : str
            User identifier
        conversation_uuid : str
            Conversation identifier
        k_memory : int
            Number of memory turns to retrieve

        Returns
        -------
        ConversationData
            Conversation data containing message turns
        """
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
        **kwargs,
    ) -> str:
        """
        Get formatted conversation from memory.

        Parameters
        ----------
        db : Session
            Database session object
        user_uuid : str
            User identifier
        conversation_uuid : str
            Conversation identifier
        k_memory : int
            Number of memory turns to retrieve
        **kwargs : dict
            k_turns : int
                Number of conversation turns to format (-1 for all)
            roles : list
                List of message roles to include in formatting

        Returns
        -------
        str
            Formatted conversation string
        """
        k_turns = kwargs.get("k_turns", -1)
        roles = kwargs.get("roles", [MessageRole.USER, MessageRole.ASSISTANT])

        conversational_memory = await self.get_conversational_memory(
            db, user_uuid, conversation_uuid, k_memory
        )

        return conversational_memory.format(k_turns=k_turns, roles=roles)
