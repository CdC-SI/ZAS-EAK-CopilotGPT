import logging
from typing import Dict, List
import uuid

from chat.memory import ConversationalMemory
from chat.status_service import status_service, StatusType, offtopic_service
from rag.factory import RetrieverFactory
from rag.llm.factory import LLMFactory
from rag.llm.base import BaseLLM

from utils.streaming import StreamingHandlerFactory, StreamingHandler, Token
from rag.messages import MessageBuilder
from commands.command_service import CommandService, TranslationService

from config.base_config import chat_config
from config.base_config import rag_config

from autocomplete.autocomplete_service import autocomplete_service
from rag.rag_service import rag_service

from schemas.chat import ChatRequest
from schemas.llm import TopicCheck

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
        self.max_tokens = rag_config["llm"]["max_output_tokens"]
        self.temperature = rag_config["llm"]["temperature"]
        self.top_p = rag_config["llm"]["top_p"]
        self.top_k = rag_config["retrieval"]["top_k"]
        self.chat_memory = ConversationalMemory(
            memory_type=chat_config["memory"]["memory_type"],
            k_memory=chat_config["memory"]["k_memory"],
        )

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
        message_builder = MessageBuilder(
            language=request.language, llm_model=request.llm_model
        )
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
            user_message = request.command
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

        self.chat_memory.memory_instance.add_message_to_memory(
            db,
            user_uuid=request.user_uuid,
            conversation_uuid=request.conversation_uuid,
            message_uuid=user_message_uuid,
            role="user",
            message=user_message,
            language=request.language,
        )

        self.chat_memory.memory_instance.add_message_to_memory(
            db,
            user_uuid=request.user_uuid,
            conversation_uuid=request.conversation_uuid,
            message_uuid=assistant_message_uuid,
            role="assistant",
            message=assistant_response,
            language=request.language,
            url=source_url,
            retrieved_doc_ids=retrieved_doc_ids,
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
        if not self.chat_memory.memory_instance.conversation_uuid_exists(
            db, request.conversation_uuid
        ):
            create_title_message = message_builder.build_chat_title_prompt(
                query=request.query, assistant_response=assistant_response
            )
            chat_title = await llm_client.agenerate(create_title_message)
            self.chat_memory.memory_instance.index_chat_title(
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
        sources: Dict,
    ):

        messages = [{"role": "user", "content": request.query}]

        event_stream = llm_client.call(messages)
        async for token in streaming_handler.generate_stream(
            event_stream, sources["source_url"]
        ):
            yield token

    @observe(name="login_message")
    async def login_message(self, language: str = "de"):

        message = {
            "de": "Bitte registrieren Sie sich und melden Sie sich an, um auf diese Funktion zuzugreifen.",
            "fr": "Veuillez vous inscrire et vous connecter pour accéder à cette fonctionnalité.",
            "it": "Si prega di registrarsi e accedere per accedere a questa funzionalità.",
        }.get(
            language,
            "Bitte registrieren Sie sich und melden Sie sich an, um auf diese Funktion zuzugreifen.",
        )

        yield Token.from_text(message).content

    @observe(name="on_topic_check")
    async def on_topic_check(
        self,
        query: str,
        language: str,
        llm_client: BaseLLM,
        message_builder: MessageBuilder,
    ):
        """
        Check if the query is on topic.
        """
        messages = message_builder.build_topic_check_prompt(query=query)
        res = await llm_client.llm_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=0,
            top_p=0.95,
            max_tokens=512,
            messages=messages,
            response_format=TopicCheck,
        )

        on_topic = res.choices[0].message.parsed.on_topic

        if not on_topic:
            message = offtopic_service.get_message(language)
            yield Token.from_text(message)
            yield Token.from_source("https://www.eak.admin.ch")
            yield Token.from_status("<off_topic>true</off_topic>")
            return
        else:
            yield Token.from_status("<off_topic>false</off_topic>")

    async def process_request(self, db: Session, request: ChatRequest):
        """
        Process a request by setting up necessary components and routing to appropriate service.
        """
        logger.info("Request params: %s", request.dict())
        (
            llm_client,
            message_builder,
            retriever_client,
            streaming_handler,
            command_service,
        ) = self._initialize_components(request)

        assistant_response = []
        sources = {"documents": [], "source_url": None}

        # On-topic check status update
        yield Token.from_status(
            f"<topic_check>{status_service.get_status_message(StatusType.TOPIC_CHECK, request.language)}</topic_check>"
        ).content

        is_off_topic = False
        if chat_config["topic_check"]:
            async for token in self.on_topic_check(
                query=request.query,
                language=request.language,
                llm_client=llm_client,
                message_builder=message_builder,
            ):
                yield token.content
                if b"<off_topic>true</off_topic>" in token.content:
                    is_off_topic = True
                if (
                    b"<off_topic>true</off_topic>" not in token.content
                    and b"<off_topic>false</off_topic>" not in token.content
                ):
                    assistant_response.append(token.content.decode("utf-8"))

        if is_off_topic:
            # index chat_history and chat_title for off-topic responses
            if request.user_uuid:
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
            return

        if request.rag:  # execute rag
            async for token in self.rag_service.process_rag(
                db=db,
                request=request,
                llm_client=llm_client,
                streaming_handler=streaming_handler,
                retriever_client=retriever_client,
                message_builder=message_builder,
                memory_client=self.chat_memory,
                sources=sources,
            ):
                yield token.content
                if not token.is_source:
                    assistant_response.append(token.content.decode("utf-8"))

        elif request.agentic_rag:  # execute agentic rag
            if not request.user_uuid:
                async for token in self.login_message(
                    language=request.language
                ):
                    assistant_response.append(token.decode("utf-8"))
                    yield token
                return
            async for token in self.rag_service.process_agentic_rag(
                db=db,
                request=request,
                llm_client=llm_client,
                streaming_handler=streaming_handler,
                retriever_client=retriever_client,
                message_builder=message_builder,
                memory_client=self.chat_memory,
                sources=sources,
            ):
                yield token.content
                if not token.is_source:
                    assistant_response.append(token.content.decode("utf-8"))

        elif request.command:  # execute command
            if not request.user_uuid:
                async for token in self.login_message(
                    language=request.language
                ):
                    assistant_response.append(token.decode("utf-8"))
                    yield token
                return
            async for token in command_service.process_command(
                request=request,
                llm_client=llm_client,
                streaming_handler=streaming_handler,
                memory_client=self.chat_memory,
                sources=sources,
            ):
                yield token.content
                if not token.is_source:
                    assistant_response.append(token.content.decode("utf-8"))

        else:  # vanilla LLM call
            async for token in self.process_vanilla_llm(
                request=request,
                streaming_handler=streaming_handler,
                llm_client=llm_client,
                sources=sources,
            ):
                yield token.content
                if not token.is_source:
                    assistant_response.append(token.content.decode("utf-8"))

        # index chat_history and chat_title
        if request.user_uuid:
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
