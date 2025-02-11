import os
import logging
from typing import Dict, AsyncGenerator
from dotenv import load_dotenv

from llm.base import BaseLLM
from rag.retrievers import RetrieverClient
from memory import MemoryService
from chat.status_service import status_service, StatusType

from schemas.chat import ChatRequest
from schemas.embedding import EmbeddingRequest
from agents.query_orchestrator import (
    infer_intent,
    infer_sources,
    # infer_tags,
    select_agent,
    run_agent,
)

from sqlalchemy.orm import Session
from utils.embedding import get_embedding
from utils.streaming import StreamingHandler, Token
from chat.messages import MessageBuilder
from agents import (
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
        self.source_validator_agent = SourceValidatorAgent()

    async def embed(self, text_input: EmbeddingRequest):
        """
        Get the embedding of an embedding request.
        """
        embedding = await get_embedding(text_input.text)
        return {"data": embedding}

    @observe(name="RAG_service_retrieve")
    async def retrieve(
        self,
        db: Session,
        request: ChatRequest,
        retriever_client: RetrieverClient,
        conversational_memory: str,
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
            organizations=request.organizations,
            user_uuid=request.user_uuid,
            k_retrieve=request.k_retrieve,
            llm_model=request.llm_model,
            conversational_memory=conversational_memory,
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
        memory_service: MemoryService,
        sources: Dict,
    ) -> AsyncGenerator[Token, None]:
        """
        Process a ChatRequest to retrieve relevant documents and generate a response.

        This method retrieves relevant documents from the database, constructs context from the documents and conversational history,
        and then uses an LLM client to generate a response based on the request query and the context.
        """
        # Retrieval status update
        yield Token.from_status(
            f"<retrieval>{status_service.get_status_message(StatusType.RETRIEVAL, request.language)}</retrieval>"
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

        documents = await self.retrieve(
            db, request, retriever_client, conversational_memory
        )

        validated_docs = []
        validated_sources = []

        # Source validation
        if request.source_validation:
            async for doc in self.source_validator_agent.validate_sources(
                request,
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
                f"<doc_{i}>{doc['text']}</doc_{i}>"
                for i, doc in enumerate(validated_docs, start=1)
            ]
        )

        messages = message_builder.build_chat_prompt(
            language=request.language,
            llm_model=request.llm_model,
            context_docs=formatted_context_docs,
            query=request.query,
            conversational_memory=conversational_memory.format(),
            response_style=request.response_style,
            response_format=request.response_format,
        )

        # stream response
        event_stream = llm_client.call(messages)
        async for token in streaming_handler.generate_stream(event_stream):
            yield token

        sources["documents"] = validated_docs
        sources["source_urls"] = validated_sources

    @observe()
    async def process_agentic_rag(
        self,
        db: Session,
        request: ChatRequest,
        llm_client: BaseLLM,
        streaming_handler: StreamingHandler,
        retriever_client: RetrieverClient,
        message_builder: MessageBuilder,
        memory_service: MemoryService,
        sources: Dict,
    ) -> AsyncGenerator[Token, None]:
        # Routing status update
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

        logger.info("----- CONVERSATIONAL MEMORY: %s", conversational_memory)

        # Intent detection
        # TO DO: perform retrieval to get context docs
        # TO DO: format docs
        # documents = await self.retrieve(db, request, retriever_client)
        # formatted_docs = "\n\n".join([doc["text"] for doc in documents])

        # TO DO: yield status message
        (inferred_intent, followup_question) = await infer_intent(
            db=db,
            message_builder=message_builder,
            llm_client=llm_client,
            request=request,
            conversational_memory=conversational_memory,
        )

        # TO DO: method to observe with langfuse for FollowUpQ --> FollowUpQ should be applied to all agentic workflows
        if followup_question:
            yield Token.from_text(followup_question)
            return

        # Workflow selection
        # TO DO: implement workflow steps
        # if step is user_followup_q -> don't do retrieval, only lookup conv memory
        # if step is factual_qa -> rag_agent
        # if step is ...

        # Source detection
        # Need user actions (eg pdf upload) added to chat history/conversational memory
        # TO DO: yield status message
        if not request.source:
            inferred_sources = await infer_sources(
                db=db,
                message_builder=message_builder,
                llm_client=llm_client,
                request=request,
                inferred_intent=inferred_intent,
                conversational_memory=conversational_memory,
            )
            request.source = inferred_sources

        # Tags detection
        # TO DO: yield status message
        if not request.tags:
            # inferred_tags = await infer_tags(
            #     db=db,
            #     message_builder=message_builder,
            #     llm_client=llm_client,
            #     request=request,
            #     inferred_intent=inferred_intent,
            #     inferred_sources=inferred_sources,
            #     conversational_memory=conversational_memory,
            # )
            # request.tags = inferred_tags
            request.tags = None

        # Agent handoff
        agent = await select_agent(
            request,
            message_builder,
            llm_client,
            conversational_memory,
            inferred_intent,
        )

        yield Token.from_status(
            f"<agent_handoff>{status_service.get_status_message(StatusType.AGENT_HANDOFF, request.language, agent_name=agent.name)}</agent_handoff>"
        )

        logger.info("Selected Agent: %s", agent.name)

        async for token in run_agent(
            db=db,
            llm_client=llm_client,
            message_builder=message_builder,
            streaming_handler=streaming_handler,
            retriever_client=retriever_client,
            memory_service=memory_service,
            agent=agent,
            request=request,
            sources=sources,
        ):
            yield token


rag_service = RAGService(
    stream=rag_config["llm"]["stream"],
    max_tokens=rag_config["llm"]["max_output_tokens"],
    temperature=rag_config["llm"]["temperature"],
    top_p=rag_config["llm"]["top_p"],
    top_k=rag_config["retrieval"]["top_k"],
)
