import logging
from typing import Dict, List, Optional

from chat.memory import ConversationalMemory
from rag.models import RAGRequest
from rag.factory import RetrieverFactory
from rag.llm.factory import LLMFactory
from rag.llm.base import BaseLLM
from rag.retrievers import RetrieverClient

from utils.streaming import StreamingHandlerFactory, StreamingHandler
from rag.messages import MessageBuilder

from config.base_config import chat_config
from config.base_config import rag_config

from rag.rag_service import rag_service


from sqlalchemy.orm import Session

from langfuse.decorators import observe

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(self, stream: bool, max_tokens: int, temperature: float, top_p: float, top_k: int, memory_type: str, k_memory: int):
        self.stream = stream
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.k_retrieve = top_k
        self.chat_memory = ConversationalMemory(
            memory_type=memory_type,
            k_memory=k_memory
        )
        self.rag_service = rag_service

    def _get_conversational_memory(self, user_uuid: str, conversation_uuid: str) -> str:
        """
        Fetch and format conversational memory.
        """
        conversational_memory = self.chat_memory.memory_instance.fetch_from_memory(user_uuid, conversation_uuid)
        return "\n".join([f"{role}: {message}" for msg in conversational_memory for role, message in msg.items()])

    def _initialize_components(self, language: Optional[str], llm_model: Optional[str], retrieval_method: Optional[List[str]]):
        """
        Initialize LLM client, MessageBuilder, Retriever client, and StreamingHandler.
        """
        llm_client = LLMFactory.get_llm_client(llm_model=llm_model, stream=self.stream, temperature=self.temperature, top_p=self.top_p, max_tokens=self.max_tokens)
        message_builder = MessageBuilder(language=language, llm_model=llm_model)
        retriever_client = RetrieverFactory.get_retriever_client(retrieval_method=retrieval_method, llm_client=llm_client, message_builder=message_builder)
        streaming_handler = StreamingHandlerFactory.get_streaming_strategy(llm_model=llm_model)
        return llm_client, message_builder, retriever_client, streaming_handler

    async def _retrieve_documents(self, db: Session, request: RAGRequest, language: Optional[str], tag: Optional[str], retriever_client: RetrieverClient):
        """
        Retrieve relevant documents from the database.
        """
        documents = await self.rag_service.retrieve(db, request, language=language, tag=tag, k=self.k_retrieve, retriever_client=retriever_client)
        context_docs = "\n\nDOC: ".join([doc["text"] for doc in documents])
        source_url = documents[0]["url"]  # TO DO: display multiple sources in frontend
        return documents, context_docs, source_url

    def _build_chat_prompt(self, message_builder: MessageBuilder, context_docs: str, query: str, conversational_memory: List[Dict]):
        """
        Build the chat prompt from the context documents and query.
        """
        return message_builder.build_chat_prompt(context_docs=context_docs, query=query, conversational_memory=conversational_memory)

    async def _stream_response(self, llm_client: BaseLLM, streaming_handler: StreamingHandler, messages: List[Dict], source_url: str):
        """
        Stream the response from the LLM client.
        """
        event_stream = llm_client.call(messages)
        async for token in streaming_handler.generate_stream(event_stream, source_url):
            yield token.decode("utf-8")

    async def _index_conversation_turn(self, db: Session, user_uuid: str, conversation_uuid: str, query: str, assistant_response: List[str], documents: List[Dict]):
        """
        Index the query and response in chat history.
        """
        self.chat_memory.memory_instance.add_message_to_memory(db, user_uuid, conversation_uuid, "user", query)
        retrieved_doc_ids = [doc["id"] for doc in documents]
        self.chat_memory.memory_instance.add_message_to_memory(db, user_uuid, conversation_uuid, "assistant", "".join(assistant_response), retrieved_doc_ids=retrieved_doc_ids)

    async def _index_chat_title(self, db: Session, user_uuid: str, conversation_uuid: str, query: str, assistant_response: List[str], message_builder: MessageBuilder, llm_client: BaseLLM):
        """
        Index the chat title if it does not already exist.
        """
        if not self.chat_memory.memory_instance.conversation_uuid_exists(db, conversation_uuid):
            create_title_message = message_builder.build_chat_title_prompt(query=query, assistant_response=assistant_response)
            chat_title = await llm_client.agenerate(create_title_message)
            self.chat_memory.memory_instance.index_chat_title(db, user_uuid, conversation_uuid, chat_title.choices[0].message.content)

    @observe()
    async def process(self, db: Session, llm_client: BaseLLM, streaming_handler: StreamingHandler, retriever_client: RetrieverClient, message_builder: MessageBuilder, request: RAGRequest, language: Optional[str] = None, tag: Optional[str] = None, user_uuid: str = None, conversation_uuid: str = None, conversational_memory: List[Dict] = None):
        """
        Process a RAGRequest to retrieve relevant documents and generate a response.

        This method retrieves relevant documents from the database, constructs a context from the documents, and then uses an LLM client to generate a response based on the request query and the context.
        """
        documents, context_docs, source_url = await self._retrieve_documents(db, request, language, tag, retriever_client)
        messages = self._build_chat_prompt(message_builder, context_docs, request.query, conversational_memory)

        assistant_response = [token async for token in self._stream_response(llm_client, streaming_handler, messages, source_url)]
        await self._index_conversation_turn(db, user_uuid, conversation_uuid, request.query, assistant_response, documents)
        await self._index_chat_title(db, user_uuid, conversation_uuid, request.query, assistant_response, message_builder, llm_client)

    async def process_request(self, db: Session, request: RAGRequest, language: Optional[str] = None, tag: Optional[str] = None, llm_model: Optional[str] = rag_config["llm"]["model"], retrieval_method: Optional[List[str]] = rag_config["retrieval"]["retrieval_method"], k_memory: Optional[int] = chat_config["memory"]["k_memory"], user_uuid: Optional[str] = None, conversation_uuid: Optional[str] = None):
        """
        Process a request by setting up necessary components and fetching conversational memory.
        """
        conversational_memory = self._get_conversational_memory(user_uuid, conversation_uuid)

        llm_client, message_builder, retriever_client, streaming_handler = self._initialize_components(language, llm_model, retrieval_method)

        return self.process(db=db, llm_client=llm_client, streaming_handler=streaming_handler, retriever_client=retriever_client, message_builder=message_builder, request=request, language=language, tag=tag, user_uuid=user_uuid, conversation_uuid=conversation_uuid, conversational_memory=conversational_memory)


bot = ChatBot(
    stream=rag_config["llm"]["stream"],
    max_tokens=rag_config["llm"]["max_output_tokens"],
    temperature=rag_config["llm"]["temperature"],
    top_p=rag_config["llm"]["top_p"],
    top_k=rag_config["retrieval"]["top_k"],
    memory_type=chat_config["memory"]["memory_type"],
    k_memory=chat_config["memory"]["k_memory"]
)
