import os
import logging
from typing import Dict
from dotenv import load_dotenv

from llm.base import BaseLLM
from rag.retrievers import RetrieverClient
from chat.memory import ConversationalMemory
from chat.status_service import status_service, StatusType

from schemas.chat import ChatRequest
from schemas.embedding import EmbeddingRequest
from schemas.rag import AgentHandoff

from sqlalchemy.orm import Session
from utils.embedding import get_embedding
from utils.streaming import StreamingHandler, Token
from chat.messages import MessageBuilder
from agents import (
    RAGAgent,
    PensionAgent,
    FAK_EAK_Agent,
    FollowUpAgent,
    SourceValidatorAgent,
)

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
        self.rag_agent = RAGAgent()
        self.pension_agent = PensionAgent()
        self.fak_eak_agent = FAK_EAK_Agent()
        self.followup_agent = FollowUpAgent()
        self.source_validator_agent = SourceValidatorAgent()

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
            k_retrieve=request.k_retrieve,
            llm_model=request.llm_model,
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
        # Retrieval status update
        yield Token.from_status(
            f"<retrieval>{status_service.get_status_message(StatusType.RETRIEVAL, request.language)}</retrieval>"
        )

        documents = await self.retrieve(db, request, retriever_client)

        validated_docs = []
        validated_sources = []

        # Source validation
        if request.source_validation:
            async for doc in self.source_validator_agent.validate_sources(
                request.language,
                request.query,
                documents,
                llm_client,
                message_builder,
            ):
                yield Token.from_source(doc["url"])
                validated_docs.append(doc)
                validated_sources.append(doc["url"])

        else:
            # Return top sources if no source validation
            for doc in documents:
                yield Token.from_source(doc["url"])
                validated_docs.append(doc)
                validated_sources.append(doc["url"])

        formatted_context_docs = "\n\n".join(
            [
                f"DOC [{i}]: {doc['text']}"
                for i, doc in enumerate(validated_docs, start=1)
            ]
        )

        conversational_memory = (
            memory_client.memory_instance.format_conversational_memory(
                request.user_uuid, request.conversation_uuid, request.k_memory
            )
        )

        messages = message_builder.build_chat_prompt(
            language=request.language,
            llm_model=request.llm_model,
            context_docs=formatted_context_docs,
            query=request.query,
            conversational_memory=conversational_memory,
            response_style=request.response_style,
            response_format=request.response_format,
        )

        # stream response
        event_stream = llm_client.call(messages)
        async for token in streaming_handler.generate_stream(event_stream):
            yield token

        # TO DO: update this
        sources["documents"] = validated_docs
        sources["source_url"] = (
            validated_sources[0] if validated_sources else None
        )

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
        # Routing status update
        yield Token.from_status(
            f"<routing>{status_service.get_status_message(StatusType.ROUTING, request.language)}</routing>"
        )

        messages = message_builder.build_agent_handoff_prompt(
            language=request.language,
            llm_model=request.llm_model,
            query=request.query,
        )
        res = await llm_client.llm_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=0,
            top_p=0.95,
            max_tokens=1024,
            messages=messages,
            response_format=AgentHandoff,
        )

        agent_name = res.choices[0].message.parsed.agent
        logger.info("Selected Agent: %s", agent_name)

        if agent_name == "RAG_AGENT":
            logger.info("Routing to RAG Agent")
            yield Token.from_status(
                f"<agent_handoff>{status_service.get_status_message(StatusType.AGENT_HANDOFF, request.language, agent_name=agent_name)}</agent_handoff>"
            )

            # Follow-up question
            # async for token in self.followup_agent.process(FollowUp.RAG, request.language):
            #     yield token

            async for token in self.process_rag(
                db,
                request,
                llm_client,
                streaming_handler,
                retriever_client,
                message_builder,
                memory_client,
                sources,
            ):
                yield token

        elif agent_name == "PENSION_AGENT":
            logger.info("Routing to PENSION Agent")
            yield Token.from_status(
                f"<agent_handoff>{status_service.get_status_message(StatusType.AGENT_HANDOFF, request.language, agent_name=agent_name)}</agent_handoff>"
            )

            async for token in self.pension_agent.process(
                query=request.query,
                language=request.language,
                message_builder=message_builder,
                llm_client=llm_client,
            ):
                yield token

        elif agent_name == "FAK_EAK_AGENT":
            logger.info("Routing to FAK_EAK Agent")
            yield Token.from_status(
                f"<agent_handoff>{status_service.get_status_message(StatusType.AGENT_HANDOFF, request.language, agent_name=agent_name)}</agent_handoff>"
            )

            async for token in self.fak_eak_agent.process(
                query=request.query,
                language=request.language,
                message_builder=message_builder,
                llm_client=llm_client,
            ):
                yield token

        else:
            logger.info("Agent handoff failed. Asking follow-up question.")
            # LLM logic to clarify topic/ask for more information?
            message = "Can you please provide more information?"
            yield Token.from_text(message)


rag_service = RAGService(
    stream=rag_config["llm"]["stream"],
    max_tokens=rag_config["llm"]["max_output_tokens"],
    temperature=rag_config["llm"]["temperature"],
    top_p=rag_config["llm"]["top_p"],
    top_k=rag_config["retrieval"]["top_k"],
)
