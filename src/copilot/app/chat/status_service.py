from enum import Enum
import uuid

from utils.streaming import Token
from llm.base import BaseLLM
from chat.messages import MessageBuilder
from schemas.agents import TopicCheck

from langfuse.decorators import observe

import logging

logger = logging.getLogger(__name__)


class StatusType(Enum):
    RETRIEVAL = "retrieval"
    ROUTING = "routing"
    INTENT_PROCESSING = "intent_processing"
    SOURCE_PROCESSING = "source_processing"
    TAGS_PROCESSING = "tags_processing"
    AGENT_HANDOFF = "agent_handoff"
    TOOL_USE = "tool_use"
    TOPIC_CHECK = "topic_check"
    LOGIN = "login"


class StatusMessageService:
    """Service for handling chat status messages in different languages"""

    _STATUS_MESSAGES = {
        StatusType.RETRIEVAL: {
            "de": "Suche nach relevanten Dokumenten",
            "fr": "Recherche des documents pertinents",
            "it": "Ricerca di documenti rilevanti",
        },
        StatusType.ROUTING: {
            "de": "Weiterleitung an den entsprechenden Dienst",
            "fr": "Routage vers le service approprié",
            "it": "Instradamento al servizio appropriato",
        },
        StatusType.INTENT_PROCESSING: {
            "de": "Verarbeitung der Anfrage",
            "fr": "Traitement de la demande",
            "it": "Elaborazione della richiesta",
        },
        StatusType.SOURCE_PROCESSING: {
            "de": "Auswahl der Quellen",
            "fr": "Sélection des sources",
            "it": "Selezione della fonte",
        },
        StatusType.TAGS_PROCESSING: {
            "de": "Auswahl der Tags",
            "fr": "Sélection des tags",
            "it": "Selezione dei tag",
        },
        StatusType.AGENT_HANDOFF: {
            "de": "{} bearbeitet Ihre Anfrage",
            "fr": "{} traite votre demande",
            "it": "{} sta elaborando la sua richiesta",
        },
        StatusType.TOOL_USE: {
            "de": "Verwendung des Tools: {}",
            "fr": "Utilisation de l'outil: {}",
            "it": "Utilizzo dello strumento: {}",
        },
        StatusType.TOPIC_CHECK: {
            "de": "Validierungsabfrage",
            "fr": "Validation de la requête",
            "it": "Convalida della query",
        },
    }

    DEFAULT_LANGUAGE = "de"

    @classmethod
    def get_status_message(
        cls, status_type: StatusType, language: str, **kwargs
    ) -> str:
        """
        Get status message for given type and language.

        Parameters
        ----------
        status_type : StatusType
            Type of status message to retrieve
        language : str
            Language code for the message
        **kwargs : dict
            Additional arguments for message formatting

        Returns
        -------
        str
            Formatted status message in requested language
        """
        messages = cls._STATUS_MESSAGES[status_type]
        message = messages.get(language, messages.get(cls.DEFAULT_LANGUAGE))

        if status_type == StatusType.AGENT_HANDOFF and "agent_name" in kwargs:
            message = message.format(kwargs["agent_name"])

        if status_type == StatusType.TOOL_USE and "tool_name" in kwargs:
            message = message.format(kwargs["tool_name"])

        return message


class LoginMessageService:
    """Service for handling login messages in different languages"""

    _LOGIN_MESSAGES = {
        StatusType.LOGIN: {
            "de": "Bitte registrieren Sie sich und melden Sie sich an, um auf diese Funktion zuzugreifen.",
            "fr": "Veuillez vous inscrire et vous connecter pour accéder à cette fonctionnalité.",
            "it": "Si prega di registrarsi e accedere per accedere a questa funzionalità.",
        },
    }

    DEFAULT_LANGUAGE = "de"

    @classmethod
    def get_message(cls, status_type: StatusType, language: str) -> str:
        """
        Get login message for given language.

        Parameters
        ----------
        status_type : StatusType
            Type of message to retrieve
        language : str
            Language code for the message

        Returns
        -------
        str
            Login message in requested language
        """
        if status_type == StatusType.LOGIN:
            messages = cls._LOGIN_MESSAGES[status_type]
            messages = messages.get(
                language, messages.get(cls.DEFAULT_LANGUAGE)
            )
            return messages


class TopicCheckService:
    """Service for handling topic validation and off-topic responses"""

    _MESSAGES = {
        "de": "Wie kann ich Ihnen bei Ihren Fragen zur AHV/IV helfen?",
        "fr": "Comment puis-je vous aider à répondre à vos questions concernant l'AVS/AI ?",
        "it": "Come posso aiutarvi a rispondere alle vostre domande sull'AVS/AI?",
    }

    DEFAULT_LANGUAGE = "de"

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name

    def get_message(self, language: str) -> str:
        """
        Get off-topic message for given language.

        Parameters
        ----------
        language : str
            Language code for the message

        Returns
        -------
        str
            Off-topic message in requested language
        """
        return self._MESSAGES.get(
            language, self._MESSAGES[self.DEFAULT_LANGUAGE]
        )

    @observe(name="check_topic")
    async def check_topic(
        self,
        query: str,
        language: str,
        llm_client: BaseLLM,
        message_builder: MessageBuilder,
    ):
        """
        Check if query is on topic and yield appropriate responses.

        Parameters
        ----------
        query : str
            User query to check
        language : str
            Language code for the response
        llm_client : BaseLLM
            Language model client instance
        message_builder : MessageBuilder
            Message builder instance for prompt construction

        Yields
        ------
        Token
            Response tokens for off-topic queries
        """
        messages = message_builder.build_topic_check_prompt(
            language=language, llm_model=self.model_name, query=query
        )

        res = await llm_client.llm_client.beta.chat.completions.parse(
            model=self.model_name,
            temperature=0,
            top_p=0.95,
            max_tokens=512,
            messages=messages,
            response_format=TopicCheck,
        )

        on_topic = res.choices[0].message.parsed.on_topic

        if on_topic:
            return
        else:
            message_uuid = str(uuid.uuid4())
            message = self.get_message(language)
            yield Token.from_text(message)
            yield Token.from_status(
                f"\n\n<message_uuid>{message_uuid}</message_uuid>"
            )
            return


status_service = StatusMessageService()
login_message_service = LoginMessageService()
topic_check_service = TopicCheckService()
