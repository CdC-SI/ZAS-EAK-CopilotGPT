import logging
from enum import Enum
from typing import List, Dict, AsyncGenerator
import asyncio
from asyncio import Semaphore
from collections.abc import AsyncIterator

from agents.function_metadata import extract_function_metadata
from agents.tools import (
    determine_reduction_rate_and_supplement,
    rag_tool,
    translate_tool,
    summarize_tool,
)
from agents.function_executor import FunctionExecutor
from chat.messages import MessageBuilder
from schemas.chat import ChatRequest
from llm.base import BaseLLM
from prompts.agents import (
    RAG_FOLLOWUP_AGENT_PROMPT_DE,
    RAG_FOLLOWUP_AGENT_PROMPT_FR,
    RAG_FOLLOWUP_AGENT_PROMPT_IT,
)
from schemas.agents import FunctionCall, UniqueSourceValidation
from agents.response_service import calculation_response_service
from agents.base import BaseAgent
from llm.factory import LLMFactory
from utils.streaming import Token
from chat.status_service import status_service, StatusType

from langfuse.decorators import observe

logger = logging.getLogger(__name__)

executor = FunctionExecutor()
executor.register_function(determine_reduction_rate_and_supplement)

llm_client = LLMFactory.get_llm_client(
    model="gpt-4o-mini",
    stream=True,
    temperature=0.0,
    top_p=0.95,
    max_tokens=2056,
)


class FollowUp(Enum):
    RAG = "rag"
    FAK_REDUCTION_RATE = "reduction_rate"
    FAK_ELIGIBILITY = "eligibility"


class FollowUpAgent(BaseAgent):
    """Agent for handling follow-up prompts based on different scenarios"""

    _PROMPTS = {
        FollowUp.RAG: {
            "de": RAG_FOLLOWUP_AGENT_PROMPT_DE,
            "fr": RAG_FOLLOWUP_AGENT_PROMPT_FR,
            "it": RAG_FOLLOWUP_AGENT_PROMPT_IT,
        },
        FollowUp.FAK_REDUCTION_RATE: {
            "de": "Um Ihren Kürzungssatz zu berechnen, benötige ich folgende Informationen:\n"
            "- Ihr genaues Rentenvorbezugsdatum\n"
            "- Ihr Geschlecht\n"
            "Können Sie mir diese Informationen bitte mitteilen?",
            "fr": "Pour calculer votre taux de réduction, j'ai besoin des informations suivantes:\n"
            "- Votre date exacte de retraite anticipée\n"
            "- Votre sexe\n"
            "Pouvez-vous me fournir ces informations?",
            "it": "Per calcolare il tasso di riduzione, ho bisogno delle seguenti informazioni:\n"
            "- La data esatta del pensionamento anticipato\n"
            "- Il suo sesso\n"
            "Può fornirmi queste informazioni?",
        },
        FollowUp.FAK_ELIGIBILITY: {
            "de": "Um Ihre Berechtigung zu prüfen, bitte ich Sie um folgende Angaben:\n"
            "- Sind Sie in der Schweiz wohnhaft?\n"
            "- Sind Sie bei der AHV versichert?",
            "fr": "Pour vérifier votre éligibilité, veuillez me fournir les informations suivantes:\n"
            "- Résidez-vous en Suisse?\n"
            "- Êtes-vous assuré(e) à l'AVS?",
            "it": "Per verificare la sua ammissibilità, la prego di fornirmi le seguenti informazioni:\n"
            "- Risiede in Svizzera?\n"
            "- È assicurato/a all'AVS?",
        },
    }

    DEFAULT_LANGUAGE = "de"

    @classmethod
    def get_follow_up_prompt(
        cls, follow_up_type: FollowUp, language: str
    ) -> str:
        """Get follow-up prompt for given type and language"""
        prompts = cls._PROMPTS[follow_up_type]
        return prompts.get(language, prompts.get(cls.DEFAULT_LANGUAGE))


class ChatAgent(BaseAgent):

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
        """
        Process the query with Chat agent.
        """
        intent = kwargs.get("intent")
        db = kwargs.get("db")
        memory_service = kwargs.get("memory_service")
        streaming_handler = kwargs.get("streaming_handler")

        logger.info("------ INTENT: %s", intent)
        if intent == "translate":
            yield Token.from_status(
                f"<tool_use>{status_service.get_status_message(StatusType.TOOL_USE, request.language, tool_name='translate_conversation')}</tool_use>"
            )
            try:
                async for token in translate_tool(
                    request,
                    memory_service,
                    message_builder,
                    llm_client,
                    db,
                ):
                    yield Token.from_text(token)
            except Exception as e:
                logger.info("Error translating conversation: %s", e)
                raise e
        elif intent == "summarize":
            yield Token.from_status(
                f"<tool_use>{status_service.get_status_message(StatusType.TOOL_USE, request.language, tool_name='summarize_conversation')}</tool_use>"
            )
            try:
                async for token in summarize_tool(
                    request,
                    memory_service,
                    message_builder,
                    llm_client,
                    streaming_handler,
                    db,
                ):
                    yield token
            except Exception as e:
                logger.info("Error summarizing conversation: %s", e)
                raise e
        else:
            message = "Sorry, I do not understand your intent. Please try again with a more specific question."
            yield Token.from_text(message)


class PensionAgent(BaseAgent):

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
        """
        yield Token.from_status(
            f"<tool_use>{status_service.get_status_message(StatusType.TOOL_USE, request.language, tool_name='determine_reduction_rate_and_supplement')}</tool_use>"
        )
        func_metadata = extract_function_metadata(
            determine_reduction_rate_and_supplement
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
        """
        db = kwargs.get("db")
        streaming_handler = kwargs.get("streaming_handler")
        retriever_client = kwargs.get("retriever_client")
        memory_service = kwargs.get("memory_service")
        sources = kwargs.get("sources")

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
        """
        pass


class SourceValidatorAgent(BaseAgent):

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
        """
        pass

    @observe(name="_validate_single_source")
    async def _validate_single_source(
        self,
        request: ChatRequest,
        document: Dict,
        llm_client: BaseLLM,
        message_builder: MessageBuilder,
    ) -> Token | None:
        """Validate a single source with retry logic"""
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
                    if result.choices[0].message.parsed.is_valid:
                        logger.info(
                            "---------Source validated: %s",
                            result.choices[0].message.parsed,
                        )
                        return document
                    return None
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
        Sources are yielded as soon as they are validated.
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
                token = await completed_task
                if token:
                    yield token
            except Exception as e:
                logger.error("Error processing validation result: %s", e)
                continue


class AgentFactory:

    @staticmethod
    def get_agent(agent_name: str):
        if agent_name == "RAG_AGENT":
            return RAGAgent(name=agent_name)
        elif agent_name == "PENSION_AGENT":
            return PensionAgent(name=agent_name)
        elif agent_name == "CHAT_AGENT":
            return ChatAgent(name=agent_name)
        elif agent_name == "SOURCE_VALIDATOR_AGENT":
            return SourceValidatorAgent(name=agent_name)
        else:
            raise ValueError(f"Unsupported agent name: {agent_name}")
