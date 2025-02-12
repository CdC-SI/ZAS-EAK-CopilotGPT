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

    def format(
        self,
        k_turns: Optional[int] = -1,
        roles: Optional[List[MessageRole]] = [
            MessageRole.USER,
            MessageRole.ASSISTANT,
        ],
    ) -> str:
        """Format the conversation data for use in prompt.

        Args:
            k_turns: Number of most recent turns to include. -1 means all turns.
            roles: List of roles to include in the formatting. Empty list means all roles.
        """
        formatted_messages = []
        total_turns = len(self.turns)
        # Handle k_turns: if negative or exceeds length, use all turns
        k_turns = (
            total_turns if k_turns < 0 or k_turns > total_turns else k_turns
        )

        for turn in self.turns[-k_turns:]:
            # Format user message if USER role is requested
            if MessageRole.USER in roles and turn.user_message:
                formatted_messages.append(
                    f"{turn.user_message.timestamp} - {turn.user_message.role.value}\n{turn.user_message.message}"
                )

            # Format assistant message if ASSISTANT role is requested
            if MessageRole.ASSISTANT in roles and turn.assistant_message:
                assistant_msg = f"{turn.assistant_message.timestamp} - {turn.assistant_message.role.value}\n{turn.assistant_message.message}"
                if turn.assistant_message.retrieved_doc_ids:
                    assistant_msg += f"\nSource doc IDs: {turn.assistant_message.retrieved_doc_ids}"
                formatted_messages.append(assistant_msg)

        return "\n\n".join(formatted_messages)
