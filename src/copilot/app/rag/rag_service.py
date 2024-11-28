import os
import logging
from typing import Dict
from dotenv import load_dotenv

from rag.llm.base import BaseLLM
from rag.retrievers import RetrieverClient
from chat.memory import ConversationalMemory

from schemas.chat import ChatRequest
from schemas.embedding import EmbeddingRequest

from sqlalchemy.orm import Session
from utils.embedding import get_embedding
from utils.streaming import StreamingHandler
from rag.messages import MessageBuilder

from config.base_config import rag_config

from langfuse import Langfuse
from langfuse.decorators import observe
from langfuse.decorators import langfuse_context

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levellevelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", None)
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", None)
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", None)

# Load Proxy settings
HTTP_PROXY = os.environ.get("HTTP_PROXY", None)
REQUESTS_CA_BUNDLE = os.environ.get("REQUESTS_CA_BUNDLE", None)
logger.info(
    f"HTTP_PROXY: {HTTP_PROXY}, REQUESTS_CA_BUNDLE: {REQUESTS_CA_BUNDLE}"
)

# if HTTP_PROXY then set the proxy
httpx_client = None
if HTTP_PROXY and REQUESTS_CA_BUNDLE:
    logger.info(f"Setting up HTTP_PROXY: {HTTP_PROXY}")
    logger.info(f"Setting up REQUESTS_CA_BUNDLE: {REQUESTS_CA_BUNDLE}")

    import httpx

    httpx_client = httpx.AsyncClient(
        proxy=HTTP_PROXY, verify=REQUESTS_CA_BUNDLE
    )

# Initialize Langfuse client
langfuse_client = Langfuse(
    secret_key=LANGFUSE_SECRET_KEY,
    public_key=LANGFUSE_PUBLIC_KEY,
    host=LANGFUSE_HOST,
    httpx_client=httpx_client,
)

# Configure the Langfuse client with a custom httpx client
langfuse_context.configure(
    secret_key=LANGFUSE_SECRET_KEY,
    public_key=LANGFUSE_PUBLIC_KEY,
    httpx_client=httpx_client,
    host=LANGFUSE_HOST,
    enabled=True,
)


class RAGService:
    """
    Class implementing the RAG process
    """

    def __init__(
        self,
        stream: bool,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
    ):

        self.stream = stream
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.k_retrieve = top_k

    async def embed(self, text_input: EmbeddingRequest):
        """
        Get the embedding of an embedding request.
        """
        embedding = await get_embedding(text_input.text)
        return {"data": embedding}

    @observe()
    async def retrieve(
        self,
        db: Session,
        request: ChatRequest,
        retriever_client: RetrieverClient,
    ):
        """
        Retrieve context documents related to the user input question.
        """
        tags = (
            None if not request.tags or request.tags == [""] else request.tags
        )
        rows = await retriever_client.get_documents(
            db,
            request.query,
            language=request.language,
            tags=tags,
            source=request.source,
            k=request.k_retrieve,
        )

        return rows if len(rows) > 0 else [{"id": "", "text": "", "url": ""}]

    @observe()
    async def process_rag(
        self,
        db: Session,
        request: ChatRequest,
        llm_client: BaseLLM,
        streaming_handler: StreamingHandler,
        retriever_client: RetrieverClient,
        message_builder: MessageBuilder,
        memory_client: ConversationalMemory,
        sources: Dict,
    ):
        """
        Process a ChatRequest to retrieve relevant documents and generate a response.

        This method retrieves relevant documents from the database, constructs context from the documents and conversational history,
        and then uses an LLM client to generate a response based on the request query and the context.
        """
        # Add retrieving message
        yield "<retrieving>Retrieving documents</retrieving>".encode("utf-8")

        documents = await self.retrieve(db, request, retriever_client)
        formatted_context_docs = "\n\n".join(
            [
                f"DOC [{i}]: {doc['text']}"
                for i, doc in enumerate(documents, start=1)
            ]
        )
        source_url = documents[0][
            "url"
        ]  # TO DO: display multiple sources in frontend

        sources["documents"] = documents
        sources["source_url"] = source_url

        conversational_memory = (
            memory_client.memory_instance.format_conversational_memory(
                request.user_uuid, request.conversation_uuid, request.k_memory
            )
        )

        messages = message_builder.build_chat_prompt(
            context_docs=formatted_context_docs,
            query=request.query,
            conversational_memory=conversational_memory,
        )

        # stream response
        event_stream = llm_client.call(messages)
        async for token in streaming_handler.generate_stream(
            event_stream, source_url
        ):
            yield token

        @observe()
        async def process_agentic_rag(
            self,
            db: Session,
            request: ChatRequest,
            llm_client: BaseLLM,
            streaming_handler: StreamingHandler,
            retriever_client: RetrieverClient,
            message_builder: MessageBuilder,
            memory_client: ConversationalMemory,
            sources: Dict,
        ):
            pass


rag_service = RAGService(
    stream=rag_config["llm"]["stream"],
    max_tokens=rag_config["llm"]["max_output_tokens"],
    temperature=rag_config["llm"]["temperature"],
    top_p=rag_config["llm"]["top_p"],
    top_k=rag_config["retrieval"]["top_k"],
)
