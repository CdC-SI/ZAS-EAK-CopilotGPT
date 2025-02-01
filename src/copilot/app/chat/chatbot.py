import logging
from typing import Dict, List
import uuid

from memory import MemoryService
from memory.models import MessageData
from memory.config import MemoryConfig

from chat.status_service import (
    status_service,
    StatusType,
    login_message_service,
    topic_check_service,
)
from rag.factory import RetrieverFactory
from llm.factory import LLMFactory
from llm.base import BaseLLM

from utils.streaming import StreamingHandlerFactory, StreamingHandler, Token
from chat.messages import MessageBuilder
from commands.command_service import CommandService, TranslationService

from config.base_config import chat_config
from config.base_config import rag_config

from autocomplete.autocomplete_service import autocomplete_service
from rag.rag_service import rag_service

from schemas.chat import ChatRequest

from sqlalchemy.orm import Session

from langfuse.decorators import observe

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ChatBot:
    def __init__(self):

        self.stream = rag_config["llm"]["stream"]
        self.rag_service = rag_service
        self.autocomplete_service = autocomplete_service
        memory_config = MemoryConfig.from_dict(chat_config["memory"])
        self.memory_service = MemoryService(
            memory_type=memory_config.memory_type,
            k_memory=memory_config.k_memory,
            config=memory_config.storage,
        )
        self.max_tokens = rag_config["llm"]["max_output_tokens"]
        self.temperature = rag_config["llm"]["temperature"]
        self.top_p = rag_config["llm"]["top_p"]
        self.top_k = rag_config["retrieval"]["top_k"]

    def _initialize_components(self, request: ChatRequest):
        """
        Initialize LLM client, MessageBuilder, Retriever client, StreamingHandler and CommandService.
        """
        llm_client = LLMFactory.get_llm_client(
            llm_model=request.llm_model,
            stream=self.stream,
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_output_tokens,
        )
        message_builder = MessageBuilder()
        if request.response_style == "legal":
            retrieval_method = request.retrieval_method
            retrieval_method.append("fedlex_retriever")
            retriever_client = RetrieverFactory.get_retriever_client(
                retrieval_method=retrieval_method,
                llm_client=llm_client,
                message_builder=message_builder,
            )
        else:
            retriever_client = RetrieverFactory.get_retriever_client(
                retrieval_method=request.retrieval_method,
                llm_client=llm_client,
                message_builder=message_builder,
            )
        streaming_handler = StreamingHandlerFactory.get_streaming_strategy(
            llm_model=request.llm_model
        )
        translation_service = TranslationService()
        command_service = CommandService(translation_service, message_builder)
        return (
            llm_client,
            message_builder,
            retriever_client,
            streaming_handler,
            command_service,
        )

    async def _index_conversation_turn(
        self,
        db: Session,
        request: ChatRequest,
        assistant_response: List[str],
        documents: List[Dict],
        source_url: str,
        user_message_uuid: str = None,
        assistant_message_uuid: str = None,
    ):
        """
        Index the query and response in chat history.
        """
        if request.command:
            user_message = f"{request.command} {request.command_args}"
            retrieved_doc_ids = None
        elif request.rag or request.agentic_rag:
            user_message = request.query
            retrieved_doc_ids = (
                [doc["id"] for doc in documents if doc["id"]]
                if documents
                else None
            )
        else:
            user_message = request.query
            retrieved_doc_ids = None

        user_message = MessageData(
            user_uuid=request.user_uuid,
            conversation_uuid=request.conversation_uuid,
            message_uuid=user_message_uuid,
            role="user",
            message=user_message,
            language=request.language,
        )

        self.memory_service.chat_memory.add_message_to_memory(
            db,
            user_message,
        )

        assistant_message = MessageData(
            user_uuid=request.user_uuid,
            conversation_uuid=request.conversation_uuid,
            message_uuid=assistant_message_uuid,
            role="assistant",
            message=assistant_response,
            language=request.language,
            url=source_url,
            retrieved_doc_ids=retrieved_doc_ids,
        )
        self.memory_service.chat_memory.add_message_to_memory(
            db, assistant_message
        )

    async def _index_chat_title(
        self,
        db: Session,
        request: ChatRequest,
        assistant_response: List[str],
        message_builder: MessageBuilder,
        llm_client: BaseLLM,
    ):
        """
        Index the chat title if it does not already exist.
        """
        if not self.memory_service.chat_memory.conversation_uuid_exists(
            db, request.conversation_uuid
        ):
            create_title_message = message_builder.build_chat_title_prompt(
                language=request.language,
                llm_model=request.llm_model,
                query=request.query,
                assistant_response=assistant_response,
            )
            chat_title = await llm_client.agenerate(create_title_message)
            self.memory_service.chat_memory.index_chat_title(
                db,
                request.user_uuid,
                request.conversation_uuid,
                chat_title.choices[0].message.content,
            )

    @observe()
    async def process_vanilla_llm(
        self,
        request: ChatRequest,
        llm_client: BaseLLM,
        streaming_handler: StreamingHandler,
    ):

        messages = [{"role": "user", "content": request.query}]

        event_stream = llm_client.call(messages)
        async for token in streaming_handler.generate_stream(event_stream):
            yield token

    @observe(name="topic_check")
    async def _topic_check(
        self,
        query: str,
        language: str,
        llm_client: BaseLLM,
        message_builder: MessageBuilder,
    ):
        """Check if the query is on topic."""
        async for token in topic_check_service.check_topic(
            query=query,
            language=language,
            llm_client=llm_client,
            message_builder=message_builder,
        ):
            yield token

    async def _handle_login_required(self, language: str):
        """Handle case when user is not logged in"""
        message_uuid = str(uuid.uuid4())
        message = login_message_service.get_message(StatusType.LOGIN, language)

        yield Token.from_text(message)
        yield Token.from_status(
            f"\n\n<message_uuid>{message_uuid}</message_uuid>"
        )

    async def process_request(self, db: Session, request: ChatRequest):
        """
        Process a request by setting up necessary components and routing to appropriate service.
        """
        # Login check for advanced features
        if not request.user_uuid:
            async for token in self._handle_login_required(request.language):
                yield token.content
            return

        logger.info("Request params: %s", request.dict())

        # Initialize components
        (
            llm_client,
            message_builder,
            retriever_client,
            streaming_handler,
            command_service,
        ) = self._initialize_components(request)

        assistant_response = []
        sources = {"documents": [], "source_url": None}

        # Query validation
        is_on_topic = True
        if request.topic_check:
            yield Token.from_status(
                f"<topic_check>{status_service.get_status_message(StatusType.TOPIC_CHECK, request.language)}</topic_check>"
            ).content

            async for token in self._topic_check(
                query=request.query,
                language=request.language,
                llm_client=llm_client,
                message_builder=message_builder,
            ):
                yield token.content
                if not token.is_source and not token.is_status:
                    assistant_response.append(token.content.decode("utf-8"))
                is_on_topic = False

        # Only proceed with regular processing if is on topic
        if is_on_topic:
            if request.rag:
                async for token in self.rag_service.process_rag(
                    db=db,
                    request=request,
                    llm_client=llm_client,
                    streaming_handler=streaming_handler,
                    retriever_client=retriever_client,
                    message_builder=message_builder,
                    memory_service=self.memory_service,
                    sources=sources,
                ):
                    yield token.content
                    if not token.is_source and not token.is_status:
                        assistant_response.append(
                            token.content.decode("utf-8")
                        )

            elif request.agentic_rag:
                async for token in self.rag_service.process_agentic_rag(
                    db=db,
                    request=request,
                    llm_client=llm_client,
                    streaming_handler=streaming_handler,
                    retriever_client=retriever_client,
                    message_builder=message_builder,
                    memory_service=self.memory_service,
                    sources=sources,
                ):
                    yield token.content
                    if not token.is_source and not token.is_status:
                        assistant_response.append(
                            token.content.decode("utf-8")
                        )

            elif request.command:
                async for token in command_service.process_command(
                    db=db,
                    request=request,
                    llm_client=llm_client,
                    streaming_handler=streaming_handler,
                    memory_service=self.memory_service,
                ):
                    yield token.content
                    if not token.is_source and not token.is_status:
                        assistant_response.append(
                            token.content.decode("utf-8")
                        )

            else:
                async for token in self.process_vanilla_llm(
                    request=request,
                    streaming_handler=streaming_handler,
                    llm_client=llm_client,
                ):
                    yield token.content
                    if not token.is_source and not token.is_status:
                        assistant_response.append(
                            token.content.decode("utf-8")
                        )

        # Always index the response, whether off-topic or not
        assistant_message_uuid = str(uuid.uuid4())
        yield Token.from_status(
            f"\n\n<message_uuid>{assistant_message_uuid}</message_uuid>"
        ).content

        user_message_uuid = str(uuid.uuid4())
        assistant_response_text = "".join(assistant_response)
        await self._index_conversation_turn(
            db,
            request,
            assistant_response_text,
            sources["documents"],
            sources["source_url"],
            user_message_uuid,
            assistant_message_uuid,
        )
        await self._index_chat_title(
            db,
            request,
            assistant_response_text,
            message_builder,
            llm_client,
        )


bot = ChatBot()
