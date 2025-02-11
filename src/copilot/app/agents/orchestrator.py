from sqlalchemy.orm import Session

from llm.base import BaseLLM
from chat.messages import MessageBuilder
from chat.status_service import status_service, StatusType
from schemas.chat import ChatRequest
from memory import MemoryService
from utils.streaming import Token


class AgentOrchestrator:

    def __init__(self):
        pass

    async def process(
        self,
        db: Session,
        request: ChatRequest,
        llm_client: BaseLLM,
        message_builder: MessageBuilder,
        memory_service: MemoryService,
    ):
        """
        Dispatch the user query to the appropriate Agent.
        """

        yield Token.from_status(
            f"<routing>{status_service.get_status_message(StatusType.ROUTING, request.language)}</routing>"
        )

        conversational_memory = (
            await (
                memory_service.chat_memory.get_formatted_conversation(
                    db,
                    request.user_uuid,
                    request.conversation_uuid,
                    request.k_memory,
                )
            )
        )
        return conversational_memory
