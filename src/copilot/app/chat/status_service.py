from enum import Enum


class StatusType(Enum):
    RETRIEVAL = "retrieval"
    ROUTING = "routing"
    AGENT_HANDOFF = "agent_handoff"
    TOPIC_CHECK = "topic_check"


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
        StatusType.AGENT_HANDOFF: {
            "de": "{} bearbeitet Ihre Anfrage",
            "fr": "{} traite votre demande",
            "it": "{} sta elaborando la sua richiesta",
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
        """Get status message for given type and language"""
        messages = cls._STATUS_MESSAGES[status_type]
        message = messages.get(language, messages.get(cls.DEFAULT_LANGUAGE))

        if status_type == StatusType.AGENT_HANDOFF and "agent_name" in kwargs:
            message = message.format(kwargs["agent_name"])

        return message


status_service = StatusMessageService()


class OfftopicMessageService:
    """Service for handling off-topic responses in different languages"""

    _MESSAGES = {
        "de": "Wie kann ich Ihnen bei Ihren Fragen zur AHV/IV helfen?",
        "fr": "Comment puis-je vous aider à répondre à vos questions concernant l'AVS/AI ?",
        "it": "Come posso aiutarvi a rispondere alle vostre domande sull'AVS/AI?",
    }

    DEFAULT_LANGUAGE = "de"

    @classmethod
    def get_message(cls, language: str) -> str:
        """Get off-topic message for given language"""
        return cls._MESSAGES.get(language, cls._MESSAGES[cls.DEFAULT_LANGUAGE])


offtopic_service = OfftopicMessageService()
