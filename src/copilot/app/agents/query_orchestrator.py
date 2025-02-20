from typing import Tuple, List, Dict, AsyncGenerator
from sqlalchemy.orm import Session

from rag.retrievers import RetrieverClient
from memory import MemoryService
from chat.messages import MessageBuilder
from llm.base import BaseLLM
from schemas.chat import ChatRequest
from schemas.agents import (
    IntentDetection,
    AgentHandoff,
    SourceSelection,
    TagSelection,
)
from utils.streaming import Token
from utils.streaming import StreamingHandler
from agents import AgentFactory, RAGAgent
from agents.base import BaseAgent
from utils.logging import get_logger

from langfuse.decorators import observe

logger = get_logger(__name__)

SUPPORTED_AGENTS = ["RAG_AGENT", "CHAT_AGENT", "PENSION_AGENT"]


@observe(name="infer_intent")
async def infer_intent(
    db: Session,
    message_builder: MessageBuilder,
    llm_client: BaseLLM,
    request: ChatRequest,
    conversational_memory: str,
) -> Tuple[str, str]:
    """Infer the intent of a user query.

    Parameters
    ----------
    db : Session
        Database session object
    message_builder : MessageBuilder
        Utility for constructing message prompts
    llm_client : BaseLLM
        Language model client interface
    request : ChatRequest
        The chat request containing query and settings
    conversational_memory : str
        Previous conversation context

    Returns
    -------
    Tuple[str, str]
        A tuple containing (inferred_intent, followup_question)
    """

    messages = await message_builder.build_intent_detection_prompt(
        language=request.language,
        llm_model=request.llm_model,
        query=request.query,
        conversational_memory=conversational_memory,
        db=db,
    )

    try:
        res = await llm_client.llm_client.beta.chat.completions.parse(
            model="gpt-4o",
            temperature=0,
            top_p=0.95,
            max_tokens=4096,
            messages=messages,
            response_format=IntentDetection,
        )
    except Exception as e:
        logger.info("Exception occured when inferring user intent: %s", e)
        return (None, None)

    return (
        res.choices[0].message.parsed.intent,
        res.choices[0].message.parsed.followup_question,
    )


@observe(name="infer_sources")
async def infer_sources(
    db: Session,
    message_builder: MessageBuilder,
    llm_client: BaseLLM,
    request: ChatRequest,
    inferred_intent: str,
    conversational_memory: str,
) -> List[str]:
    """Infer relevant sources for a user query.

    Parameters
    ----------
    db : Session
        Database session object
    message_builder : MessageBuilder
        Utility for constructing message prompts
    llm_client : BaseLLM
        Language model client interface
    request : ChatRequest
        The chat request containing query and settings
    inferred_intent : str
        Previously inferred intent of the query
    conversational_memory : str
        Previous conversation context

    Returns
    -------
    List[str]
        List of inferred source identifiers
    """

    messages = await message_builder.build_source_selection_prompt(
        language=request.language,
        llm_model=request.llm_model,
        query=request.query,
        intent=inferred_intent if inferred_intent else None,
        conversational_memory=conversational_memory,
        db=db,
    )

    try:
        res = await llm_client.llm_client.beta.chat.completions.parse(
            model="gpt-4o",
            temperature=0,
            top_p=0.95,
            max_tokens=2048,
            messages=messages,
            response_format=SourceSelection,
        )
    except Exception as e:
        logger.info("Exception occured when inferring sources: %s", e)
        return None

    inferred_sources = (
        res.choices[0].message.parsed.inferred_sources
        if res.choices[0].message.parsed.inferred_sources
        else None
    )
    return inferred_sources


@observe(name="infer_tags")
async def infer_tags(
    db: Session,
    message_builder: MessageBuilder,
    llm_client: BaseLLM,
    request: ChatRequest,
    inferred_intent: str,
    inferred_sources: List[str],
    conversational_memory: str,
) -> List[str]:
    """Infer relevant tags for a user query.

    Parameters
    ----------
    db : Session
        Database session object
    message_builder : MessageBuilder
        Utility for constructing message prompts
    llm_client : BaseLLM
        Language model client interface
    request : ChatRequest
        The chat request containing query and settings
    inferred_intent : str
        Previously inferred intent
    inferred_sources : List[str]
        Previously inferred sources
    conversational_memory : str
        Previous conversation context

    Returns
    -------
    List[str]
        List of inferred tags
    """

    messages = await message_builder.build_tag_selection_prompt(
        language=request.language,
        llm_model=request.llm_model,
        query=request.query,
        intent=inferred_intent if inferred_intent else None,
        sources=inferred_sources if inferred_sources else None,
        conversational_memory=conversational_memory,
        db=db,
    )

    try:
        res = await llm_client.llm_client.beta.chat.completions.parse(
            model="gpt-4o",
            temperature=0,
            top_p=0.95,
            max_tokens=2048,
            messages=messages,
            response_format=TagSelection,
        )
    except Exception as e:
        logger.info("Exception occured when inferring tags: %s", e)
        return None

    inferred_tags = (
        res.choices[0].message.parsed.inferred_tags
        if res.choices[0].message.parsed.inferred_tags
        else None
    )
    return inferred_tags


@observe(name="select_agent")
async def select_agent(
    request: ChatRequest,
    message_builder: MessageBuilder,
    llm_client: BaseLLM,
    conversational_memory: str,
    inferred_intent: str,
) -> BaseAgent:
    """Select appropriate agent to handle the user query.

    Parameters
    ----------
    request : ChatRequest
        The chat request containing query and settings
    message_builder : MessageBuilder
        Utility for constructing message prompts
    llm_client : BaseLLM
        Language model client interface
    conversational_memory : str
        Previous conversation context
    inferred_intent : str
        Previously inferred intent

    Returns
    -------
    BaseAgent
        Selected agent instance to handle the query
    """
    messages = await message_builder.build_agent_handoff_prompt(
        language=request.language,
        llm_model=request.llm_model,
        query=request.query,
        intent=inferred_intent,
        tags=request.tags,
        sources=request.source,
        conversational_memory=conversational_memory,
    )

    try:
        res = await llm_client.llm_client.beta.chat.completions.parse(
            model="gpt-4o",
            temperature=0,
            top_p=0.95,
            max_tokens=2048,
            messages=messages,
            response_format=AgentHandoff,
        )
    except Exception as e:
        logger.info("Exception occured when selecting agent: %s", e)
        return RAGAgent()

    agent_name = (
        res.choices[0].message.parsed.agent
        if res.choices[0].message.parsed.agent in SUPPORTED_AGENTS
        else "RAG_AGENT"
    )

    agent = AgentFactory.get_agent(agent_name)

    return agent


@observe(name="run_agent")
async def run_agent(
    db: Session,
    llm_client: BaseLLM,
    message_builder: MessageBuilder,
    streaming_handler: StreamingHandler,
    retriever_client: RetrieverClient,
    memory_service: MemoryService,
    agent: BaseAgent,
    request: ChatRequest,
    sources: Dict,
    **kwargs,
) -> AsyncGenerator[Token, None]:
    """Execute the selected agent to process the user query.

    Parameters
    ----------
    db : Session
        Database session object
    llm_client : BaseLLM
        Language model client interface
    message_builder : MessageBuilder
        Utility for constructing message prompts
    streaming_handler : StreamingHandler
        Handler for streaming responses
    retriever_client : RetrieverClient
        Client for retrieving relevant content
    memory_service : MemoryService
        Service for managing conversation memory
    agent : BaseAgent
        The agent selected to handle the query
    request : ChatRequest
        The chat request containing query and settings
    sources : Dict
        Dictionary of source materials
    **kwargs : dict
        Additional keyword arguments

    Yields
    ------
    Token
        Response tokens generated by the agent
    """
    intent = kwargs.get("intent", None)

    try:
        async for token in agent.process(
            request,
            message_builder,
            llm_client,
            streaming_handler=streaming_handler,
            retriever_client=retriever_client,
            memory_service=memory_service,
            sources=sources,
            db=db,
            intent=intent,
        ):
            yield token
    except Exception as e:
        logger.info("Exception occured when running agent: %s", e)

        # LLM logic to clarify topic/ask for more information?
        message = " An error occured while handling request with Agent, please retry."
        yield Token.from_text(message)
