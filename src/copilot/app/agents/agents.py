import logging
from enum import Enum

from .function_metadata import extract_function_metadata
from .functions import calculate_reduction_rate_and_supplement
from .function_executor import FunctionExecutor
from rag.messages import MessageBuilder
from rag.llm.base import BaseLLM
from rag.prompts import (
    RAG_FOLLOWUP_AGENT_PROMPT_DE,
    RAG_FOLLOWUP_AGENT_PROMPT_FR,
    RAG_FOLLOWUP_AGENT_PROMPT_IT,
)
from schemas.agents import FunctionCall
from .response_service import calculation_response_service

logger = logging.getLogger(__name__)

executor = FunctionExecutor()
executor.register_function(calculate_reduction_rate_and_supplement)


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
        func_metadata = extract_function_metadata(
            calculate_reduction_rate_and_supplement
        )

        messages = message_builder.build_function_call_prompt(
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
                yield token
            yield f"\n\n<source><a href='{source}' target='_blank' class='source-link'>{source}</a></source>"
        except ValueError as e:
            logger.info("Error executing function %s", e)
            message = "Sorry, an error occurred while processing your request. Please try again."
            for token in message.split():
                yield f"{token} "
            yield f"\n\n<source><a href='{source}' target='_blank' class='source-link'>{source}</a></source>"


class RAGAgent:

    def __init__(self):
        pass

    async def process(self, query: str, message_builder: MessageBuilder):
        """
        Process the query with RAG agent.
        """
        pass
