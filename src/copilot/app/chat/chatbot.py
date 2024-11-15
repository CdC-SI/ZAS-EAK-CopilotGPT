import logging
from typing import Dict, List
import uuid

from chat.memory import ConversationalMemory
from rag.factory import RetrieverFactory
from rag.llm.factory import LLMFactory
from rag.llm.base import BaseLLM
from rag.retrievers import RetrieverClient

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

    def get_conversational_memory(self, user_uuid: str, conversation_uuid: str, k_memory: int) -> str:
        """
        Fetch and format conversational memory.
        """
        if user_uuid:
            conversational_memory = self.chat_memory.memory_instance.fetch_from_memory(user_uuid, conversation_uuid, k_memory)
            return "\n".join([f"{role}: {message}" for msg in conversational_memory for role, message in msg.items()])
        else:
            conversational_memory = [{"user": "", "assistant": ""}]
            return "\n".join([f"{role}: {message}" for msg in conversational_memory for role, message in msg.items()])

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

    async def _retrieve_documents(self, db: Session, request: ChatRequest, retriever_client: RetrieverClient):
        """
        Retrieve relevant documents from the database.
        """
        documents = await self.rag_service.retrieve(db, request=request, retriever_client=retriever_client)
        formatted_context_docs = "\n\n".join([f"DOC [{i}]: {doc['text']}" for i, doc in enumerate(documents, start=1)])
        source_url = documents[0]["url"]  # TO DO: display multiple sources in frontend
        return documents, formatted_context_docs, source_url

    async def _stream_response(self, llm_client: BaseLLM, streaming_handler: StreamingHandler, messages: List[Dict], source_url: str):
        """
        Stream the response from the LLM client.
        """
        event_stream = llm_client.call(messages)
        async for token in streaming_handler.generate_stream(event_stream, source_url):
            yield token.decode("utf-8").replace("ß", "ss")

    async def _index_conversation_turn(self, db: Session, request: ChatRequest, assistant_response: List[str], documents: List[Dict], source_url: str, user_message_uuid: str = None, assistant_message_uuid: str = None):
        """
        Index the query and response in chat history.
        """
        if request.command:
            self.chat_memory.memory_instance.add_message_to_memory(db, request.user_uuid, request.conversation_uuid, user_message_uuid, "user", request.command, request.language)
        else:
            self.chat_memory.memory_instance.add_message_to_memory(db, user_uuid=request.user_uuid, conversation_uuid=request.conversation_uuid, message_uuid=user_message_uuid, role="user", message=request.query, language="de")

        retrieved_doc_ids = [doc["id"] for doc in documents if doc["id"]]
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
    async def process(self, db: Session, request: ChatRequest, llm_client: BaseLLM, streaming_handler: StreamingHandler, retriever_client: RetrieverClient, message_builder: MessageBuilder, command_service: CommandService):
        """
        Process a ChatRequest to retrieve relevant documents and generate a response.

        This method retrieves relevant documents from the database, constructs a context from the documents,
        and then uses an LLM client to generate a response based on the request query and the context.
        """
        assistant_response = []
        source_url = None
        documents = [{"id": "", "text": "", "url": ""}]
        result = {}

        if request.command and request.user_uuid: # execute command
            result = await command_service.execute_command(request, self.get_conversational_memory)

        elif request.rag: # execute rag
            documents, formatted_context_docs, source_url = await self._retrieve_documents(db, request, retriever_client)

            conversational_memory = ""
            if request.user_uuid:
                conversational_memory = self.get_conversational_memory(request.user_uuid, request.conversation_uuid, request.k_memory)

            messages = message_builder.build_chat_prompt(
                context_docs=formatted_context_docs,
                query=request.query,
                conversational_memory=conversational_memory,
            )
            result = {"messages": messages}

        else: # execute vanilla LLM call
            result = {"messages": [{"role": "user", "content": request.query}]}

        messages = result.get("messages")
        translated_text = result.get("translated_text")

        # stream response
        if messages:
            event_stream = llm_client.call(messages)
            async for token in streaming_handler.generate_stream(event_stream, source_url):
                token_str = token.decode("utf-8").replace("ß", "ss")
                if "<a href=" not in token_str:
                    assistant_response.append(token_str)
                yield token

        elif translated_text:
            for token in translated_text:
                token_str = token.replace("ß", "ss")
                assistant_response.append(token_str)
                yield token_str.encode("utf-8")

        # save chat_history and chat_title
        if request.user_uuid:
            assistant_message_uuid = str(uuid.uuid4())
            yield f"\n\n<message_uuid>{assistant_message_uuid}</message_uuid>".encode("utf-8")

            user_message_uuid = str(uuid.uuid4())
            assistant_response_text = "".join(assistant_response)
            await self._index_conversation_turn(
                db,
                request,
                assistant_response_text,
                documents,
                source_url,
                user_message_uuid,
                assistant_message_uuid,
            )
            await self._index_chat_title(
                db, request, assistant_response_text, message_builder, llm_client
            )

    async def process_request(self, db: Session, request: ChatRequest):
        """
        Process a request by setting up necessary components.
        """
        logger.info("Request params: %s", request.dict())
        llm_client, message_builder, retriever_client, streaming_handler, command_service = self._initialize_components(request)

        return self.process(db=db, request=request, llm_client=llm_client, streaming_handler=streaming_handler, retriever_client=retriever_client, message_builder=message_builder, command_service=command_service)

bot = ChatBot()
