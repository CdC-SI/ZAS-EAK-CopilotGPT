import logging
from typing import Dict, List
import uuid

from chat.memory import ConversationalMemory
from rag.factory import RetrieverFactory
from rag.llm.factory import LLMFactory
from rag.llm.base import BaseLLM

from utils.streaming import StreamingHandlerFactory, StreamingHandler
from rag.messages import MessageBuilder
from commands.command_service import CommandService, TranslationService

from config.base_config import chat_config
from config.base_config import rag_config

from autocomplete.autocomplete_service import autocomplete_service
from rag.rag_service import rag_service

from schemas.chat import ChatRequest

from sqlalchemy.orm import Session

from langfuse.decorators import observe

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
            k_memory=chat_config["memory"]["k_memory"]
        )

    def _initialize_components(self, request: ChatRequest):
        """
        Initialize LLM client, MessageBuilder, Retriever client, StreamingHandler and TranslationService.
        """
        llm_client = LLMFactory.get_llm_client(llm_model=request.llm_model, stream=self.stream, temperature=request.temperature, top_p=request.top_p, max_tokens=request.max_output_tokens)
        message_builder = MessageBuilder(language=request.language, llm_model=request.llm_model)
        retriever_client = RetrieverFactory.get_retriever_client(retrieval_method=request.retrieval_method, llm_client=llm_client, message_builder=message_builder)
        streaming_handler = StreamingHandlerFactory.get_streaming_strategy(llm_model=request.llm_model)
        translation_service = TranslationService()
        command_service = CommandService(translation_service, message_builder)
        return llm_client, message_builder, retriever_client, streaming_handler, command_service

    async def _index_conversation_turn(self, db: Session, request: ChatRequest, assistant_response: List[str], documents: List[Dict], source_url: str, user_message_uuid: str = None, assistant_message_uuid: str = None):
        """
        Index the query and response in chat history.
        """
        if request.command:
            self.chat_memory.memory_instance.add_message_to_memory(db, request.user_uuid, request.conversation_uuid, user_message_uuid, "user", request.command, request.language)
        else:
            self.chat_memory.memory_instance.add_message_to_memory(db, user_uuid=request.user_uuid, conversation_uuid=request.conversation_uuid, message_uuid=user_message_uuid, role="user", message=request.query, language="de")

        retrieved_doc_ids = [doc["id"] for doc in documents if doc["id"]] if documents else None
        self.chat_memory.memory_instance.add_message_to_memory(db, user_uuid=request.user_uuid, conversation_uuid=request.conversation_uuid, message_uuid=assistant_message_uuid, role="assistant", message=assistant_response, language="fr", url=source_url, retrieved_doc_ids=retrieved_doc_ids)

    async def _index_chat_title(self, db: Session, request: ChatRequest, assistant_response: List[str], message_builder: MessageBuilder, llm_client: BaseLLM):
        """
        Index the chat title if it does not already exist.
        """
        if not self.chat_memory.memory_instance.conversation_uuid_exists(db, request.conversation_uuid):
            create_title_message = message_builder.build_chat_title_prompt(query=request.query, assistant_response=assistant_response)
            chat_title = await llm_client.agenerate(create_title_message)
            self.chat_memory.memory_instance.index_chat_title(db, request.user_uuid, request.conversation_uuid, chat_title.choices[0].message.content)

    @observe()
    async def process_vanilla_llm(self, request: ChatRequest, llm_client: BaseLLM, streaming_handler: StreamingHandler, sources: Dict):

        messages = [{"role": "user", "content": request.query}]

        event_stream = llm_client.call(messages)
        async for token in streaming_handler.generate_stream(event_stream, sources["source_url"]):
            yield token

    @observe()
    async def login_message(self, language: str = "de"):

        if language == "de":
            message = "Bitte registrieren Sie sich und melden Sie sich an, um auf diese Funktion zuzugreifen."
        elif language == "fr":
            message = "Veuillez vous inscrire et vous connecter pour accéder à cette fonctionnalité."
        elif language == "it":
            message = "Si prega di registrarsi e accedere per accedere a questa funzionalità."
        else:
            message = "Bitte registrieren Sie sich und melden Sie sich an, um auf diese Funktion zuzugreifen."

        for token in message.split():
            yield f"{token} "

    async def process_request(self, db: Session, request: ChatRequest):
        """
        Process a request by setting up necessary components and routing to appropriate service.
        """
        logger.info("Request params: %s", request.dict())
        llm_client, message_builder, retriever_client, streaming_handler, command_service = self._initialize_components(request)

        assistant_response = []
        sources = {"documents": [], "source_url": None}

        if request.rag:  # execute rag
            async for token in self.rag_service.process_rag(db=db, request=request, llm_client=llm_client, streaming_handler=streaming_handler, retriever_client=retriever_client, message_builder=message_builder, memory_client=self.chat_memory, sources=sources):
                token_str = token.decode("utf-8").replace("ß", "ss")
                if "<a href=" not in token_str:
                    assistant_response.append(token_str)
                yield token_str.encode("utf-8")

        elif request.agentic_rag:  # execute agentic rag
            if not request.user_uuid:
                async for token in self.login_message(language=request.language):
                    assistant_response.append(token)
                    yield token.encode("utf-8")
                return
            async for token in self.rag_service.process_agentic_rag(db=db, request=request, llm_client=llm_client, streaming_handler=streaming_handler, retriever_client=retriever_client, message_builder=message_builder, memory_client=self.chat_memory, sources=sources):
                yield token

        elif request.command:  # execute command
            if not request.user_uuid:
                async for token in self.login_message(language=request.language):
                    assistant_response.append(token)
                    yield token.encode("utf-8")
                return
            async for token in command_service.process_command(request=request, llm_client=llm_client, streaming_handler=streaming_handler, memory_client=self.chat_memory, sources=sources):
                token_str = token.decode("utf-8").replace("ß", "ss")
                if "<a href=" not in token_str:
                    assistant_response.append(token_str)
                yield token_str.encode("utf-8")

        else:  # vanilla LLM call
            async for token in self.process_vanilla_llm(request=request, streaming_handler=streaming_handler, llm_client=llm_client, sources=sources):
                token_str = token.decode("utf-8").replace("ß", "ss")
                if "<a href=" not in token_str:
                    assistant_response.append(token_str)
                yield token_str.encode("utf-8")

        # index chat_history and chat_title
        if request.user_uuid:
            assistant_message_uuid = str(uuid.uuid4())
            yield f"\n\n<message_uuid>{assistant_message_uuid}</message_uuid>".encode("utf-8")

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
                db, request, assistant_response_text, message_builder, llm_client
            )

bot = ChatBot()
