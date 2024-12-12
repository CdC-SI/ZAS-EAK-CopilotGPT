import logging
from enum import Enum
from typing import List, Dict
import asyncio
from asyncio import Semaphore
from collections.abc import AsyncIterator

from .function_metadata import extract_function_metadata
from .functions import determine_reduction_rate_and_supplement
from .function_executor import FunctionExecutor
from chat.messages import MessageBuilder
from llm.base import BaseLLM
from prompts.agents import (
    RAG_FOLLOWUP_AGENT_PROMPT_DE,
    RAG_FOLLOWUP_AGENT_PROMPT_FR,
    RAG_FOLLOWUP_AGENT_PROMPT_IT,
)
from schemas.agents import FunctionCall, UniqueSourceValidation
from .response_service import calculation_response_service
from utils.streaming import Token
from chat.status_service import status_service, StatusType

from langfuse.decorators import observe

logger = logging.getLogger(__name__)

executor = FunctionExecutor()
executor.register_function(determine_reduction_rate_and_supplement)


class Agent:

    # What should an agent do?
    # What methods?
    # Access to conversational memory, have memory (state), llm_client, message_builder, tools (eg. functions, rag)
    # input: query, language
    # output: (stream of) tokens

    def __init__(
        self,
        model: BaseLLM,
        system_prompt: str,
        max_loops: int = 3,
        tools=None,
        output_type=None,
        reason=None,
        result_schema=None,
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.max_loops = max_loops
        self.tools = tools
        self.output_type = output_type  # stream or single
        self.reason = reason  # will setup plan itself
        self.result_schema = result_schema  # structured schema -> you must return this schema and fill in the values
        self.context_vars = {}
        self.memory = None
        self.llm_client = None
        self.stream = True

    async def run(self) -> str:
        pass

    async def run_stream(self):  # -> AsyncIterator[Token]:
        pass

    def _register_tool(self, tool) -> None:
        pass

    def _prepare_messages(self, query: str) -> str:
        pass


class Swarm:
    pass


class FollowUp(Enum):
    RAG = "rag"
    FAK_REDUCTION_RATE = "reduction_rate"
    FAK_ELIGIBILITY = "eligibility"


class FollowUpAgent:
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


class PensionAgent:

    def __init__(self):
        pass

    async def process(
        self,
        query: str,
        language: str,
        message_builder: MessageBuilder,
        llm_client: BaseLLM,
    ):
        """
        Process the query with Pension agent.
        """
        yield Token.from_status(
            f"<tool_use>{status_service.get_status_message(StatusType.TOOL_USE, language, tool_name='determine_reduction_rate_and_supplement')}</tool_use>"
        )
        func_metadata = extract_function_metadata(
            determine_reduction_rate_and_supplement
        )

        messages = message_builder.build_function_call_prompt(
            language=language,
            llm_model="gpt-4o-mini",
            query=query,
            func_metadata=func_metadata,
        )

        res = await llm_client.llm_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
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
                    calculation_result=calculation_result, language=language
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


class FAK_EAK_Agent:

    def __init__(self):
        pass

    async def process(self, query: str, message_builder: MessageBuilder):
        """
        Process the query with RAG agent.
        """
        pass


class RAGAgent:

    def __init__(self):
        pass

    async def process(self, query: str, message_builder: MessageBuilder):
        """
        Process the query with RAG agent.
        """
        pass


class ResearchAgent:

    def __init__(self):
        pass

    async def process(
        self,
        query: str,
        language: str,
        message_builder: MessageBuilder,
        llm_client: BaseLLM,
    ):
        """
        Process the query with Research agent.
        """
        pass


class SourceValidatorAgent:

    def __init__(self):
        self.semaphore = Semaphore(5)  # Limit to 3 concurrent requests
        self.max_retries = 3
        self.retry_delay = 1

    async def process(
        self,
        query: str,
        language: str,
        message_builder: MessageBuilder,
        llm_client: BaseLLM,
    ):
        """
        Process the query with Source Validator agent.
        """
        pass

    @observe(name="_validate_single_source")
    async def _validate_single_source(
        self,
        language: str,
        query: str,
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
                            language=language,
                            llm_model="gpt-4o-mini",
                            query=query,
                            source=document,
                        ),
                        response_format=UniqueSourceValidation,
                    )
                    if result.choices[0].message.parsed.is_valid:
                        logger.info(
                            "---------Source validated: %s",
                            result.choices[0].message.parsed,
                        )
                        return Token.from_source(document["url"])
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
        language: str,
        query: str,
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
                language=language,
                query=query,
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
