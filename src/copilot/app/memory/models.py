from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .enums import MessageRole

from utils.logging import get_logger

logger = get_logger(__name__)


class MessageData(BaseModel):
    """Represents a single message in the conversation."""

    user_uuid: str
    conversation_uuid: str
    message_uuid: str
    role: MessageRole
    message: str
    language: str
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: Optional[List[str]] = []
    faq_id: Optional[int] = None
    retrieved_doc_ids: Optional[List[int]] = None

    class Config:
        arbitrary_types_allowed = True


class ConversationTurn(BaseModel):
    """Represents a full conversation turn (user message + assistant response)."""

    user_message: MessageData
    assistant_message: MessageData = None


class ConversationData(BaseModel):
    """Represents a conversation with its turns and metadata."""

    conversation_uuid: str
    turns: List[ConversationTurn]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def format(self) -> str:
        """Format the conversation data for use in prompt."""
        formatted_messages = []
        for turn in self.turns:
            # Format user message
            formatted_messages.append(
                f"{turn.user_message.timestamp} - {turn.user_message.role.value}\n{turn.user_message.message}"
            )

            # Format assistant message if it exists
            if turn.assistant_message:
                assistant_msg = f"{turn.assistant_message.timestamp} - {turn.assistant_message.role.value}\n{turn.assistant_message.message}"
                if turn.assistant_message.retrieved_doc_ids:
                    assistant_msg += f"\nSource doc IDs: {turn.assistant_message.retrieved_doc_ids}"
                formatted_messages.append(assistant_msg)

        return "\n\n".join(formatted_messages)
