from sqlalchemy.orm import Session
from sqlalchemy import Table, MetaData, Column, String, distinct
import json
from tiktoken.core import Encoding

from chat.messages import MessageBuilder
from memory import MemoryService
from memory.models import ConversationData
from llm.base import BaseLLM
from schemas.agents import UserPreferences as UserPreferencesSchema
from utils.logging import get_logger
from utils.user_preferences import update_user_preferences_in_db

logger = get_logger(__name__)

metadata = MetaData()
Users = Table(
    "users",
    metadata,
    Column("uuid", String, primary_key=True),
)


def format_conversations(conversations: list[ConversationData]) -> str:
    """Format list of ConversationData objects into a single string.

    Parameters
    ----------
    conversations : list[ConversationData]
        List of conversation data objects to format

    Returns
    -------
    str
        Formatted string containing all conversations
    """
    # Sort conversations by created_at timestamp
    sorted_convs = sorted(conversations, key=lambda x: x.created_at)

    formatted_convs = []
    for conv in sorted_convs:
        conv_lines = [
            f"Conversation UUID: {conv.conversation_uuid}",
            f"Created at: {conv.created_at}",
            f"Updated at: {conv.updated_at}",
            "Conversation history:",
            conv.format(),
        ]
        formatted_convs.append("\n".join(conv_lines))

    return "\n\n".join(formatted_convs)


async def update_user_preferences(
    db: Session,
    memory_service: MemoryService,
    message_builder: MessageBuilder,
    llm_client: BaseLLM,
    tokenizer: Encoding,
) -> list[str]:
    """Update user preferences and return list of unique user UUIDs.

    Parameters
    ----------
    db : Session
        Database session object
    memory_service : MemoryService
        Service for handling memory operations
    message_builder : MessageBuilder
        Builder for creating message prompts
    llm_client : BaseLLM
        LLM client for making completion requests
    tokenizer : Encoding
        Tokenizer for encoding/decoding text

    Returns
    -------
    list[str]
        List of unique user UUIDs that were updated
    """
    # Query distinct user UUIDs
    user_uuids = [uuid[0] for uuid in db.query(distinct(Users.c.uuid)).all()]

    for user_uuid in user_uuids:

        conversations = (
            memory_service.chat_memory.cache.get_all_user_conversations(
                db, user_uuid
            )
        )

        # Format conversations into string
        conversations_str = format_conversations(conversations)
        truncated_conversations = tokenizer.decode(
            tokenizer.encode(conversations_str)[:125_000]
        )

        messages = message_builder.build_infer_user_preferences_prompt(
            llm_model="gpt-4o",
            conversations=truncated_conversations,
            response_schema=json.dumps(
                UserPreferencesSchema.model_json_schema(), indent=4
            ),
        )

        res = await llm_client.beta.chat.completions.parse(
            model="gpt-4o",
            temperature=0.0,
            max_tokens=2048,
            messages=messages,
            response_format=UserPreferencesSchema,
        )

        user_preferences = res.choices[0].message.parsed
        update_user_preferences_in_db(db, user_uuid, user_preferences)

    return user_uuids
