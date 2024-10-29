import os
import logging
import uuid
from typing import Dict, List
from dotenv import load_dotenv
from pyaml_env import parse_config

from rag.models import EmbeddingRequest#, RAGRequest
from rag.factory import RetrieverFactory
from rag.llm.factory import LLMFactory
from rag.llm.base import BaseLLM
from rag.retrievers import RetrieverClient
from chat.memory import ConversationalMemory
from chat.models import ChatRequest

from sqlalchemy.orm import Session
from utils.embedding import get_embedding
from utils.streaming import StreamingHandlerFactory, StreamingHandler
from rag.messages import MessageBuilder

from config.base_config import chat_config
from config.base_config import rag_config

from langfuse import Langfuse
from langfuse.decorators import observe
from langfuse.decorators import langfuse_context

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", None)
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", None)
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", None)

# Load Proxy settings
HTTP_PROXY = os.environ.get("HTTP_PROXY", None)
REQUESTS_CA_BUNDLE = os.environ.get("REQUESTS_CA_BUNDLE", None)
logger.info(f"HTTP_PROXY: {HTTP_PROXY}, REQUESTS_CA_BUNDLE: {REQUESTS_CA_BUNDLE}")

# if HTTP_PROXY then set the proxy
httpx_client = None
if HTTP_PROXY and REQUESTS_CA_BUNDLE:
    logger.info(f"Setting up HTTP_PROXY: {HTTP_PROXY}")
    logger.info(f"Setting up REQUESTS_CA_BUNDLE: {REQUESTS_CA_BUNDLE}")

    import httpx
    httpx_client = httpx.AsyncClient(proxy=HTTP_PROXY, verify=REQUESTS_CA_BUNDLE)

# Initialize Langfuse client
langfuse_client = Langfuse(
  secret_key=LANGFUSE_SECRET_KEY,
  public_key=LANGFUSE_PUBLIC_KEY,
  host=LANGFUSE_HOST,
  httpx_client=httpx_client
)

# Configure the Langfuse client with a custom httpx client
langfuse_context.configure(
    secret_key=LANGFUSE_SECRET_KEY,
    public_key=LANGFUSE_PUBLIC_KEY,
    httpx_client=httpx_client,
    host=LANGFUSE_HOST,
    enabled=True,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGService:
    """
    Class implementing the RAG process
    """
    def __init__(self, stream: bool, max_tokens: int, temperature: float,
                 top_p: float, top_k: int, memory_type: str, k_memory: int):

        self.stream = stream
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.k_retrieve = top_k
        self.chat_memory = ConversationalMemory(
            memory_type=memory_type,
            k_memory=k_memory
        )

    async def embed(self, text_input: EmbeddingRequest):
        """
        Get the embedding of an embedding request.
        """
        embedding = await get_embedding(text_input.text)
        return {"data": embedding}

    @observe()
    async def retrieve(self, db: Session, request: ChatRequest, retriever_client: RetrieverClient):
        """
        Retrieve context documents related to the user input question.
        """
        # TO DO: parse list of tags/sources
        # TO DO: filter sources in matching service
        tag = None if not request.tag or request.tag == [""] else request.tag[0]
        rows = await retriever_client.get_documents(db, request.query, language=request.language, tag=tag, k=request.k_retrieve)
        #rows = await retriever_client.get_documents(db, request.query, language=None, tag=request.tag, k=request.k_retrieve)

        return rows if len(rows) > 0 else [{"id": "", "text": "", "url": ""}]

    @observe()
    async def process(self, db: Session, request: ChatRequest, streaming_handler: StreamingHandler, llm_client: BaseLLM, retriever_client: RetrieverClient, message_builder: MessageBuilder, conversational_memory: List[Dict] = None):
        """
        Process a ChatRequest to retrieve relevant documents and generate a response.

        This method retrieves relevant documents from the database, constructs a context from the documents, and then uses an LLM client to generate a response based on the request query and the context.
        """
        # If command received, go into command mode
        # Refactor memory to retrieve last k_messages depending on command args (eg. last, all) -> pass in process_request and process
        if request.command:
            # k = -1 if request.command_args == "last" else None
            # Implement fetch_last_k_messages in memory.py
            # input_text = self.chat_memory.memory_instance.fetch_last_k_messages(db, request.user_uuid, request.conversation_uuid, k=5)
            input_text = self.chat_memory.memory_instance.fetch_from_memory(request.user_uuid, request.conversation_uuid)
            messages = message_builder.build_command_prompt(command=request.command, input_text=input_text)
            source_url = None
            documents = [{"id": "", "text": "", "url": ""}]

        else:
            documents = await self.retrieve(db, request=request, retriever_client=retriever_client)
            context_docs = "\n\nDOC: ".join([doc["text"] for doc in documents])
            source_url = documents[0]["url"]  # TO DO: display multiple sources in frontend

            conversational_memory = "\n".join([f"{role}: {message}" for msg in conversational_memory for role, message in msg.items()])
            messages = message_builder.build_chat_prompt(context_docs=context_docs, query=request.query, conversational_memory=conversational_memory)

        event_stream = llm_client.call(messages)

        assistant_response = []
        async for token in streaming_handler.generate_stream(event_stream, source_url):
            yield token
            if "<a href=" not in token.decode("utf-8"):
                assistant_response.append(token.decode("utf-8"))

        # If user is logged in, index chat history (user query and assistant response)
        if request.user_uuid:

            # Send assistant message UUID to frontend for thumbs up/down feedback
            assistant_message_uuid = str(uuid.uuid4())
            yield f"\n\n<message_uuid>{assistant_message_uuid}</message_uuid>".encode("utf-8")

            # Index user query in chat history_table
            user_message_uuid = str(uuid.uuid4())
            self.chat_memory.memory_instance.add_message_to_memory(db, request.user_uuid, request.conversation_uuid, user_message_uuid, role="user", message=request.query, language=request.language)

            # Index assistant response in chat_history table
            retrieved_doc_ids = [doc["id"] for doc in documents if doc["id"]]
            self.chat_memory.memory_instance.add_message_to_memory(db, request.user_uuid, request.conversation_uuid, assistant_message_uuid, role="assistant", message="".join(assistant_response), url=source_url, language=request.language, faq_id=None, retrieved_doc_ids=retrieved_doc_ids)

            # Index chat title
            if not self.chat_memory.memory_instance.conversation_uuid_exists(db, request.conversation_uuid):
                create_title_message = message_builder.build_chat_title_prompt(query=request.query, assistant_response=assistant_response)
                chat_title = await llm_client.agenerate(create_title_message)
                self.chat_memory.memory_instance.index_chat_title(db, request.user_uuid, request.conversation_uuid, chat_title.choices[0].message.content)

    async def process_request(self, db: Session, request: ChatRequest):

        if request.user_uuid:
            conversational_memory = self.chat_memory.memory_instance.fetch_from_memory(request.user_uuid, request.conversation_uuid)
        else:
            conversational_memory = [{"user": "", "assistant": ""}]

        llm_client = LLMFactory.get_llm_client(llm_model=request.llm_model, stream=self.stream, temperature=self.temperature, top_p=self.top_p, max_tokens=self.max_tokens)
        message_builder = MessageBuilder(language=request.language, llm_model=request.llm_model)
        retriever_client = RetrieverFactory.get_retriever_client(retrieval_method=request.retrieval_method, llm_client=llm_client, message_builder=message_builder)
        streaming_handler = StreamingHandlerFactory.get_streaming_strategy(llm_model=request.llm_model)

        return self.process(db=db,
                            request=request,
                            streaming_handler=streaming_handler,
                            llm_client=llm_client,
                            retriever_client=retriever_client,
                            message_builder=message_builder,
                            conversational_memory=conversational_memory)

rag_service = RAGService(
    stream=rag_config["llm"]["stream"],
    max_tokens=rag_config["llm"]["max_output_tokens"],
    temperature=rag_config["llm"]["temperature"],
    top_p=rag_config["llm"]["top_p"],
    top_k=rag_config["retrieval"]["top_k"],
    memory_type=chat_config["memory"]["memory_type"],
    k_memory=chat_config["memory"]["k_memory"]
    )
