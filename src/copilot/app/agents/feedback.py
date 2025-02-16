from typing import AsyncGenerator
from dataclasses import dataclass

from schemas.chat import ChatRequest
from enums.agents import FeedbackType
from utils.streaming import Token
from langfuse.decorators import observe


@dataclass
class FeedbackMessage:
    de: str
    fr: str
    it: str

    def get(self, language: str) -> str:
        return getattr(self, language.lower(), self.de)


class FeedbackMessages:
    NO_DOCS = FeedbackMessage(
        de="Keine Dokumente gefunden, die Ihrer Anfrage entsprechen.\n\nBitte aktualisieren oder setzen Sie die Dokumentenfilter (Tags, Quelle) und/oder Sprache zurück (einige Dokumente sind nur in einer Sprache verfügbar, meist deutsch).",
        fr="Aucun document trouvé correspondant à votre demande.\n\nVeuillez mettre à jour ou réinitialiser les filtres de documents (tags, source) et/ou la langue (certains documents ne sont disponibles que dans une seule langue, principalement en allemand).",
        it="Nessun documento trovato corrispondente alla tua richiesta.\n\nAggiorna o reimposta i filtri dei documenti (tag, fonte) e/o la lingua (alcuni documenti sono disponibili solo in una lingua, principalmente in tedesco).",
    )


@observe(name="ask_user_feedback")
async def ask_user_feedback(
    request: ChatRequest,
    feedback_type: FeedbackType,
    **kwargs,
) -> AsyncGenerator[Token, None]:
    """
    Generate a user feedback question.
    """
    match feedback_type:
        case FeedbackType.NO_DOCS:
            message = FeedbackMessages.NO_DOCS.get(request.language)
            yield Token.from_text(message)

        case FeedbackType.NO_VALIDATED_DOCS:
            message_builder = kwargs.get("message_builder")
            llm_client = kwargs.get("llm_client")
            streaming_handler = kwargs.get("streaming_handler")
            formatted_invalid_docs = kwargs.get("formatted_invalid_docs")
            conversational_memory = kwargs.get("conversational_memory")
            user_preferences = kwargs.get("user_preferences")

            feedback_message = (
                message_builder.build_ask_user_feedback_no_valid_docs_prompt(
                    request.language,
                    request.llm_model,
                    request.query,
                    formatted_invalid_docs,
                    conversational_memory,
                    user_preferences=user_preferences,
                )
            )

            event_stream = llm_client.call(
                feedback_message,
                model="gpt-4o",
                stream=True,
                temperature=0.0,
                max_tokens=1024,
            )
            async for token in streaming_handler.generate_stream(event_stream):
                yield token

        case FeedbackType.PARTIAL_VALIDATED_DOCS:
            pass
