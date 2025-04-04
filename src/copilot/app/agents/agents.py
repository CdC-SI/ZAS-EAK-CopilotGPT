import logging
from typing import List, Dict, AsyncGenerator, Tuple
import asyncio
from asyncio import Semaphore
from collections.abc import AsyncIterator

from agents.function_metadata import extract_function_metadata
from agents.tools import (
    determine_reduction_rate_and_supplement_tool,
    rag_tool,
    translate_tool,
    summarize_tool,
    update_user_preferences_tool,
)
from agents.function_executor import FunctionExecutor
from chat.messages import MessageBuilder
from schemas.chat import ChatRequest
from llm.base import BaseLLM

from schemas.agents import FunctionCall, UniqueSourceValidation
from agents.response_service import calculation_response_service
from agents.base import BaseAgent
from llm.factory import LLMFactory
from utils.streaming import Token
from chat.status_service import status_service, StatusType

from langfuse.decorators import observe

logger = logging.getLogger(__name__)

executor = FunctionExecutor()
executor.register_function(determine_reduction_rate_and_supplement_tool)

llm_client = LLMFactory.get_llm_client(
    model="gpt-4o-mini",
    stream=True,
    temperature=0.0,
    top_p=0.95,
    max_tokens=2056,
)


class ChatAgent(BaseAgent):
    """
    Agent for handling chat-related operations and processing different intents.

    Parameters
    ----------
    name : str, optional
        The name of the agent, defaults to "CHAT_AGENT"
    """

    def __init__(self, name: str = None):
        self.name = name if name else "CHAT_AGENT"

    @observe(name="CHAT_agent_process")
    async def process(
        self,
        request: ChatRequest,
        message_builder: MessageBuilder,
        llm_client: BaseLLM,
        **kwargs,
    ) -> AsyncGenerator[Token, None]:
        """Process the query with Chat agent.

        Parameters
        ----------
        request : ChatRequest
            The chat request containing query and language information
        message_builder : MessageBuilder
            Helper for building message prompts
        llm_client : BaseLLM
            The LLM client instance for making requests
        **kwargs : dict
            Additional keyword arguments

        Yields
        ------
        Token
            Generated tokens from the evaluation process
        """
        intent = kwargs.get("intent")
        db = kwargs.get("db")
        memory_service = kwargs.get("memory_service")
        streaming_handler = kwargs.get("streaming_handler")

        logger.info("------ INTENT: %s", intent)

        match intent:
            case "translate":
                yield Token.from_status(
                    f"<tool_use>{status_service.get_status_message(StatusType.TOOL_USE, request.language, tool_name='translate_conversation')}</tool_use>"
                )
                async for token in translate_tool(
                    request,
                    memory_service,
                    message_builder,
                    llm_client,
                    db,
                ):
                    yield Token.from_text(token)

            case "summarize":
                yield Token.from_status(
                    f"<tool_use>{status_service.get_status_message(StatusType.TOOL_USE, request.language, tool_name='summarize_conversation')}</tool_use>"
                )
                async for token in summarize_tool(
                    request,
                    memory_service,
                    message_builder,
                    llm_client,
                    streaming_handler,
                    db,
                ):
                    yield token

            case "user_followup_q":
                yield Token.from_status(
                    f"<tool_use>{status_service.get_status_message(StatusType.TOOL_USE, request.language, tool_name='ask_user_feedback')}</tool_use>"
                )
                pass

            case "update_user_preferences":
                yield Token.from_status(
                    f"<tool_use>{status_service.get_status_message(StatusType.TOOL_USE, request.language, tool_name='update_user_preferences')}</tool_use>"
                )
                async for token in update_user_preferences_tool(
                    db,
                    request,
                    memory_service,
                    message_builder,
                    llm_client,
                ):
                    yield token

            case _:
                message = "Sorry, I do not understand your intent. Please try again with a more specific question."
                yield Token.from_text(message)


class PensionAgent(BaseAgent):
    """
    Agent for handling pension-related calculations and queries.

    Parameters
    ----------
    name : str, optional
        The name of the agent, defaults to "PENSION_AGENT"
    """

    def __init__(self, name: str = None):
        self.name = name if name else "PENSION_AGENT"

    @observe(name="PENSION_agent_process")
    async def process(
        self,
        request: ChatRequest,
        message_builder: MessageBuilder,
        llm_client: BaseLLM,
        **kwargs,
    ) -> AsyncGenerator[Token, None]:
        """
        Process the query with Pension agent.

        Parameters
        ----------
        request : ChatRequest
            The chat request containing query and language information
        message_builder : MessageBuilder
            Helper for building message prompts
        llm_client : BaseLLM
            The LLM client instance for making requests
        **kwargs : dict
            Additional keyword arguments

        Yields
        ------
        Token
            Generated tokens from the evaluation process
        """
        yield Token.from_status(
            f"<tool_use>{status_service.get_status_message(StatusType.TOOL_USE, request.language, tool_name='determine_reduction_rate_and_supplement')}</tool_use>"
        )
        func_metadata = extract_function_metadata(
            determine_reduction_rate_and_supplement_tool
        )

        messages = message_builder.build_function_call_prompt(
            language=request.language,
            llm_model="gpt-4o",
            query=request.query,
            func_metadata=func_metadata,
        )

        res = await llm_client.llm_client.beta.chat.completions.parse(
            model="gpt-4o",
            temperature=0,
            top_p=0.95,
            max_tokens=512,
            messages=messages,
            response_format=FunctionCall,
        )

        function_call = res.choices[0].message.parsed.function_call

        try:
            calculation_result = executor.execute(function_call)
            response, source = (
                calculation_response_service.get_response_message(
                    calculation_result=calculation_result,
                    language=request.language,
                )
            )
            for token in response:
                yield Token.from_text(token)
            yield Token.from_source(source)
        except ValueError as e:
            logger.info("Error executing function %s", e)
            message = "Sorry, an error occurred while processing your request. Please try again."
            yield Token.from_text(message)
            yield Token.from_source(source)


class RAGAgent(BaseAgent):
    """
    Agent for handling Retrieval-Augmented Generation (RAG) operations.

    Parameters
    ----------
    name : str, optional
        The name of the agent, defaults to "RAG_AGENT"
    """

    def __init__(self, name: str = None):
        self.name = name if name else "RAG_AGENT"

    @observe(name="RAG_agent_process")
    async def process(
        self,
        request: ChatRequest,
        message_builder: MessageBuilder,
        llm_client: BaseLLM,
        **kwargs,
    ) -> AsyncGenerator[Token, None]:
        """
        Process the query with RAG agent.

        Parameters
        ----------
        request : ChatRequest
            The chat request containing query and language information
        message_builder : MessageBuilder
            Helper for building message prompts
        llm_client : BaseLLM
            The LLM client instance for making requests
        **kwargs : dict
            Additional keyword arguments

        Yields
        ------
        Token
            Generated tokens from the evaluation process
        """
        db = kwargs.get("db")
        streaming_handler = kwargs.get("streaming_handler")
        retriever_client = kwargs.get("retriever_client")
        memory_service = kwargs.get("memory_service")
        sources = kwargs.get("sources")
        intent = kwargs.get("intent")

        # Note: Move to ChatAgent ?
        match intent:
            case "factual_qa":
                # use query rewriting retriever with simple rewriting prompt (+ instructions) + from conversation history
                pass

            case "multipart_qa":
                # use query rewriting retriever with multiple subquery extraction/inference + from conversation history
                pass

            case "user_followup_q":
                # use query rewriting retriver with specific prompt for followup q -> perform immediate RAG retrieval on rewritten queries from conversation history
                pass

            # AGENT FOLLOWUP Q
            # infer most suitable retriever ? add retrievers or expand search if retrieved docs not sufficient?
            # ask user feedback

        async for token in rag_tool(
            db=db,
            request=request,
            llm_client=llm_client,
            streaming_handler=streaming_handler,
            retriever_client=retriever_client,
            message_builder=message_builder,
            memory_service=memory_service,
            sources=sources,
        ):
            yield token


class RetrievalEvaluatorAgent(BaseAgent):
    """
    Agent for evaluating retrieval operations and their results.

    Parameters
    ----------
    name : str, optional
        The name of the agent, defaults to "RETRIEVAL_EVALUATOR_AGENT"
    """

    def __init__(self, name: str = None):
        self.name = name if name else "RETRIEVAL_EVALUATOR_AGENT"

    @observe(name="RETRIEVAL_EVALUATOR_agent_process")
    async def process(
        self,
        request: ChatRequest,
        message_builder: MessageBuilder,
        llm_client: BaseLLM,
        **kwargs,
    ) -> AsyncGenerator[Token, None]:
        """
        Process the query with Retrieval Evaluator agent.

        Parameters
        ----------
        request : ChatRequest
            The chat request containing query and language information
        message_builder : MessageBuilder
            Helper for building message prompts
        llm_client : BaseLLM
            The LLM client instance for making requests
        **kwargs : dict
            Additional keyword arguments

        Yields
        ------
        Token
            Generated tokens from the evaluation process
        """
        pass


class SourceValidatorAgent(BaseAgent):
    """
    Agent for validating sources with concurrent processing capabilities.

    Parameters
    ----------
    name : str, optional
        The name of the agent, defaults to "SOURCE_VALIDATOR_AGENT"
    """

    def __init__(self, name: str = None):
        self.name = name if name else "SOURCE_VALIDATOR_AGENT"
        self.semaphore = Semaphore(5)  # Limit to 5 concurrent requests
        self.max_retries = 3
        self.retry_delay = 1

    @observe(name="SOURCE_VALIDATOR_agent_process")
    async def process(
        self,
        request: ChatRequest,
        message_builder: MessageBuilder,
        llm_client: BaseLLM,
        **kwargs,
    ) -> AsyncGenerator[Token, None]:
        """
        Process the query with Source Validator agent.

        Parameters
        ----------
        request : ChatRequest
            The chat request containing query and language information
        message_builder : MessageBuilder
            Helper for building message prompts
        llm_client : BaseLLM
            The LLM client instance for making requests
        **kwargs : dict
            Additional keyword arguments

        Yields
        ------
        Token
            Generated tokens from the evaluation process
        """
        pass

    @observe(name="_validate_single_source")
    async def _validate_single_source(
        self,
        request: ChatRequest,
        document: Dict,
        llm_client: BaseLLM,
        message_builder: MessageBuilder,
    ) -> Tuple:
        """
        Validate a single source with retry logic.

        Parameters
        ----------
        request : ChatRequest
            The chat request containing query and language information
        document : Dict
            The document to be validated
        llm_client : BaseLLM
            The LLM client instance for making validation requests
        message_builder : MessageBuilder
            The message builder for constructing prompts

        Returns
        -------
        Token | None
            Validated document and validation result, or None if validation fails
        """
        for attempt in range(self.max_retries):
            try:
                async with self.semaphore:
                    result = await llm_client.llm_client.beta.chat.completions.parse(
                        model="gpt-4o-mini",
                        temperature=0,
                        top_p=0.95,
                        max_tokens=128,
                        messages=message_builder.build_unique_source_validation_prompt(
                            language=request.language,
                            llm_model="gpt-4o-mini",
                            query=request.query,
                            source=document,
                        ),
                        response_format=UniqueSourceValidation,
                    )
                    logger.info(
                        "---------Source validated: %s",
                        result.choices[0].message.parsed,
                    )
                    return (document, result.choices[0].message.parsed)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(
                        "Final retry failed for source validation: %s", e
                    )
                    return None
                logger.warning(
                    "Retry %d failed, retrying in %d seconds: %s",
                    attempt + 1,
                    self.retry_delay,
                    e,
                )
                await asyncio.sleep(self.retry_delay)
        return None

    @observe(name="validate_sources")
    async def validate_sources(
        self,
        request: ChatRequest,
        documents: List[Dict],
        llm_client: BaseLLM,
        message_builder: MessageBuilder,
    ) -> AsyncIterator[Token]:
        """
        Validate sources against the query using concurrent LLM calls with rate limiting.

        Parameters
        ----------
        request : ChatRequest
            The chat request containing query and language information
        documents : List[Dict]
            List of documents to be validated
        llm_client : BaseLLM
            The LLM client instance for making validation requests
        message_builder : MessageBuilder
            The message builder for constructing prompts

        Yields
        ------
        Token
            Validated document and its validation result as they complete
        """
        tasks = [
            self._validate_single_source(
                request=request,
                document=doc,
                llm_client=llm_client,
                message_builder=message_builder,
            )
            for doc in documents
        ]

        for completed_task in asyncio.as_completed(tasks):
            try:
                doc, source_validation = await completed_task
                if doc:
                    yield doc, source_validation
            except Exception as e:
                logger.error("Error processing validation result: %s", e)
                continue


class AgentFactory:
    """
    Factory class for creating different types of agents.

    Methods
    -------
    get_agent(agent_name: str)
        Creates and returns an agent instance based on the agent name.
    """

    @staticmethod
    def get_agent(agent_name: str) -> BaseAgent:
        """
        Create and return an agent instance based on the agent name.

        Parameters
        ----------
        agent_name : str
            The name of the agent to create. Valid values are:
            'RAG_AGENT', 'PENSION_AGENT', 'CHAT_AGENT', 'SOURCE_VALIDATOR_AGENT'

        Returns
        -------
        BaseAgent
            An instance of the requested agent

        Raises
        ------
        ValueError
            If the agent name is not supported
        """
        match agent_name:
            case "RAG_AGENT":
                return RAGAgent(name=agent_name)
            case "PENSION_AGENT":
                return PensionAgent(name=agent_name)
            case "CHAT_AGENT":
                return ChatAgent(name=agent_name)
            case "SOURCE_VALIDATOR_AGENT":
                return SourceValidatorAgent(name=agent_name)
            case _:
                # TO DO: ask for user feedback to select agent
                raise ValueError(f"Unsupported agent name: {agent_name}")


source_validator_agent = SourceValidatorAgent()
