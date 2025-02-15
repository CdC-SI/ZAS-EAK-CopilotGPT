from typing import List, Dict, Union
from fastapi import Depends
from sqlalchemy.orm import Session

from utils.logging import get_logger

logger = get_logger(__name__)

from prompts.memory import (
    SUMMARY_MEMORY_PROMPT_DE,
    SUMMARY_MEMORY_PROMPT_FR,
    SUMMARY_MEMORY_PROMPT_IT,
)
from prompts.rag import (
    RAG_SYSTEM_PROMPT_DE,
    RAG_SYSTEM_PROMPT_FR,
    RAG_SYSTEM_PROMPT_IT,
    RAG_REASONING_SYSTEM_PROMPT_DE,
    RAG_REASONING_SYSTEM_PROMPT_FR,
    RAG_REASONING_SYSTEM_PROMPT_IT,
)
from prompts.retrieval import (
    QUERY_REWRITING_PROMPT_DE,
    QUERY_REWRITING_PROMPT_FR,
    QUERY_REWRITING_PROMPT_IT,
    QUERY_STATEMENT_REWRITING_PROMPT_DE,
    QUERY_STATEMENT_REWRITING_PROMPT_FR,
    QUERY_STATEMENT_REWRITING_PROMPT_IT,
    CONTEXTUAL_COMPRESSION_PROMPT_DE,
    CONTEXTUAL_COMPRESSION_PROMPT_FR,
    CONTEXTUAL_COMPRESSION_PROMPT_IT,
)
from prompts.commands import (
    SUMMARIZE_COMMAND_PROMPT_DE,
    SUMMARIZE_COMMAND_PROMPT_FR,
    SUMMARIZE_COMMAND_PROMPT_IT,
)
from prompts.chat import (
    TOPIC_CHECK_PROMPT_DE,
    TOPIC_CHECK_PROMPT_FR,
    TOPIC_CHECK_PROMPT_IT,
    CHAT_TITLE_SYSTEM_PROMPT_DE,
    CHAT_TITLE_SYSTEM_PROMPT_FR,
    CHAT_TITLE_SYSTEM_PROMPT_IT,
)
from prompts.source import (
    SOURCE_DESCRIPTION_SYSTEM_PROMPT_DE,
    SOURCE_DESCRIPTION_SYSTEM_PROMPT_FR,
    SOURCE_DESCRIPTION_SYSTEM_PROMPT_IT,
)
from prompts.agents import (
    INTENT_DETECTION_PROMPT_DE,
    INTENT_DETECTION_PROMPT_FR,
    INTENT_DETECTION_PROMPT_IT,
    SOURCE_SELECTION_PROMPT_DE,
    SOURCE_SELECTION_PROMPT_FR,
    SOURCE_SELECTION_PROMPT_IT,
    TAGS_SELECTION_PROMPT_DE,
    TAGS_SELECTION_PROMPT_FR,
    TAGS_SELECTION_PROMPT_IT,
    AGENT_HANDOFF_PROMPT_DE,
    AGENT_HANDOFF_PROMPT_FR,
    AGENT_HANDOFF_PROMPT_IT,
    NO_VALIDATED_DOCS_PROMPT_DE,
    NO_VALIDATED_DOCS_PROMPT_FR,
    NO_VALIDATED_DOCS_PROMPT_IT,
    UPDATE_USER_PREFERENCES_PROMPT_DE,
    UPDATE_USER_PREFERENCES_PROMPT_FR,
    UPDATE_USER_PREFERENCES_PROMPT_IT,
    PARSE_TRANSLATE_ARGS_PROMPT_DE,
    PARSE_TRANSLATE_ARGS_PROMPT_FR,
    PARSE_TRANSLATE_ARGS_PROMPT_IT,
    AGENT_SUMMARIZE_PROMPT_DE,
    AGENT_SUMMARIZE_PROMPT_FR,
    AGENT_SUMMARIZE_PROMPT_IT,
    PENSION_FUNCTION_CALLING_PROMPT_DE,
    PENSION_FUNCTION_CALLING_PROMPT_FR,
    PENSION_FUNCTION_CALLING_PROMPT_IT,
    UNIQUE_SOURCE_VALIDATION_PROMPT_DE,
    UNIQUE_SOURCE_VALIDATION_PROMPT_FR,
    UNIQUE_SOURCE_VALIDATION_PROMPT_IT,
)
from prompts.response_style import (
    RULES_ES_DE,
    RULES_ES_FR,
    RULES_ES_IT,
    RULES_LS_DE,
    RULES_LS_FR,
    RULES_LS_IT,
    RULES_CONCISE_DE,
    RULES_CONCISE_FR,
    RULES_CONCISE_IT,
    RULES_DETAILED_DE,
    RULES_DETAILED_FR,
    RULES_DETAILED_IT,
    RULES_LEGAL_DE,
    RULES_LEGAL_FR,
    RULES_LEGAL_IT,
    COMPLETE_PROMPT_DE,
    COMPLETE_PROMPT_FR,
    COMPLETE_PROMPT_IT,
    CONDENSED_PROMPT_DE,
    CONDENSED_PROMPT_FR,
    CONDENSED_PROMPT_IT,
    PROMPT_TEMPLATE_CONCISE_DE,
    PROMPT_TEMPLATE_CONCISE_FR,
    PROMPT_TEMPLATE_CONCISE_IT,
    PROMPT_TEMPLATE_DETAILED_DE,
    PROMPT_TEMPLATE_DETAILED_FR,
    PROMPT_TEMPLATE_DETAILED_IT,
    PROMPT_TEMPLATE_ES_DE,
    PROMPT_TEMPLATE_ES_FR,
    PROMPT_TEMPLATE_ES_IT,
    PROMPT_TEMPLATE_LS_DE,
    PROMPT_TEMPLATE_LS_FR,
    PROMPT_TEMPLATE_LS_IT,
    PROMPT_TEMPLATE_LEGAL_DE,
    PROMPT_TEMPLATE_LEGAL_FR,
    PROMPT_TEMPLATE_LEGAL_IT,
)
from config.llm_config import (
    SUPPORTED_OPENAI_LLM_MODELS,
    SUPPORTED_AZUREOPENAI_LLM_MODELS,
    SUPPORTED_ANTHROPIC_LLM_MODELS,
    SUPPORTED_GROQ_LLM_MODELS,
    SUPPORTED_OLLAMA_LLM_MODELS,
    SUPPORTED_MLX_LLM_MODELS,
    SUPPORTED_LLAMACPP_LLM_MODELS,
)

from database.database import get_db
from settings_api import (
    get_tags_descriptions,
    get_source_descriptions,
    get_intentions_descriptions,
)

from langfuse.decorators import observe


class MessageBuilder:

    _SUMMARY_MEMORY_PROMPT = {
        "de": SUMMARY_MEMORY_PROMPT_DE,
        "fr": SUMMARY_MEMORY_PROMPT_FR,
        "it": SUMMARY_MEMORY_PROMPT_IT,
    }

    _RAG_SYSTEM_PROMPT = {
        "de": RAG_SYSTEM_PROMPT_DE,
        "fr": RAG_SYSTEM_PROMPT_FR,
        "it": RAG_SYSTEM_PROMPT_IT,
    }

    _RAG_REASONING_SYSTEM_PROMPT = {
        "de": RAG_REASONING_SYSTEM_PROMPT_DE,
        "fr": RAG_REASONING_SYSTEM_PROMPT_FR,
        "it": RAG_REASONING_SYSTEM_PROMPT_IT,
    }

    _CHAT_TITLE_PROMPT = {
        "de": CHAT_TITLE_SYSTEM_PROMPT_DE,
        "fr": CHAT_TITLE_SYSTEM_PROMPT_FR,
        "it": CHAT_TITLE_SYSTEM_PROMPT_IT,
    }

    _SOURCE_DESCRIPTION_PROMPT = {
        "de": SOURCE_DESCRIPTION_SYSTEM_PROMPT_DE,
        "fr": SOURCE_DESCRIPTION_SYSTEM_PROMPT_FR,
        "it": SOURCE_DESCRIPTION_SYSTEM_PROMPT_IT,
    }

    _TOPIC_CHECK_PROMPT = {
        "de": TOPIC_CHECK_PROMPT_DE,
        "fr": TOPIC_CHECK_PROMPT_FR,
        "it": TOPIC_CHECK_PROMPT_IT,
    }

    _UNIQUE_SOURCE_VALIDATION_PROMPT = {
        "de": UNIQUE_SOURCE_VALIDATION_PROMPT_DE,
        "fr": UNIQUE_SOURCE_VALIDATION_PROMPT_FR,
        "it": UNIQUE_SOURCE_VALIDATION_PROMPT_IT,
    }

    _INTENT_DETECTION_PROMPT = {
        "de": INTENT_DETECTION_PROMPT_DE,
        "fr": INTENT_DETECTION_PROMPT_FR,
        "it": INTENT_DETECTION_PROMPT_IT,
    }

    _SOURCE_SELECTION_PROMPT = {
        "de": SOURCE_SELECTION_PROMPT_DE,
        "fr": SOURCE_SELECTION_PROMPT_FR,
        "it": SOURCE_SELECTION_PROMPT_IT,
    }

    _TAGS_SELECTION_PROMPT = {
        "de": TAGS_SELECTION_PROMPT_DE,
        "fr": TAGS_SELECTION_PROMPT_FR,
        "it": TAGS_SELECTION_PROMPT_IT,
    }

    _AGENT_HANDOFF_PROMPT = {
        "de": AGENT_HANDOFF_PROMPT_DE,
        "fr": AGENT_HANDOFF_PROMPT_FR,
        "it": AGENT_HANDOFF_PROMPT_IT,
    }

    _NO_VALIDATED_DOCS_PROMPT = {
        "de": NO_VALIDATED_DOCS_PROMPT_DE,
        "fr": NO_VALIDATED_DOCS_PROMPT_FR,
        "it": NO_VALIDATED_DOCS_PROMPT_IT,
    }

    _PARSE_TRANSLATE_ARGS_PROMPT = {
        "de": PARSE_TRANSLATE_ARGS_PROMPT_DE,
        "fr": PARSE_TRANSLATE_ARGS_PROMPT_FR,
        "it": PARSE_TRANSLATE_ARGS_PROMPT_IT,
    }

    _AGENT_SUMMARIZE_PROMPT = {
        "de": AGENT_SUMMARIZE_PROMPT_DE,
        "fr": AGENT_SUMMARIZE_PROMPT_FR,
        "it": AGENT_SUMMARIZE_PROMPT_IT,
    }

    _PENSION_FUNCTION_CALLING_PROMPT = {
        "de": PENSION_FUNCTION_CALLING_PROMPT_DE,
        "fr": PENSION_FUNCTION_CALLING_PROMPT_FR,
        "it": PENSION_FUNCTION_CALLING_PROMPT_IT,
    }

    _UPDATE_USER_PREFERENCES_PROMPT = {
        "de": UPDATE_USER_PREFERENCES_PROMPT_DE,
        "fr": UPDATE_USER_PREFERENCES_PROMPT_FR,
        "it": UPDATE_USER_PREFERENCES_PROMPT_IT,
    }

    _QUERY_REWRITING_PROMPT = {
        "de": QUERY_REWRITING_PROMPT_DE,
        "fr": QUERY_REWRITING_PROMPT_FR,
        "it": QUERY_REWRITING_PROMPT_IT,
    }

    _QUERY_STATEMENT_REWRITING_PROMPT = {
        "de": QUERY_STATEMENT_REWRITING_PROMPT_DE,
        "fr": QUERY_STATEMENT_REWRITING_PROMPT_FR,
        "it": QUERY_STATEMENT_REWRITING_PROMPT_IT,
    }

    _CONTEXTUAL_COMPRESSION_PROMPT = {
        "de": CONTEXTUAL_COMPRESSION_PROMPT_DE,
        "fr": CONTEXTUAL_COMPRESSION_PROMPT_FR,
        "it": CONTEXTUAL_COMPRESSION_PROMPT_IT,
    }

    _SUMMARIZE_COMMAND_PROMPT = {
        "de": SUMMARIZE_COMMAND_PROMPT_DE,
        "fr": SUMMARIZE_COMMAND_PROMPT_FR,
        "it": SUMMARIZE_COMMAND_PROMPT_IT,
    }

    _DEFAULT_LANGUAGE = "de"

    _RESPONSE_FORMAT = {
        "concise": {
            "de": PROMPT_TEMPLATE_CONCISE_DE,
            "fr": PROMPT_TEMPLATE_CONCISE_FR,
            "it": PROMPT_TEMPLATE_CONCISE_IT,
        },
        "detailed": {
            "de": PROMPT_TEMPLATE_DETAILED_DE,
            "fr": PROMPT_TEMPLATE_DETAILED_FR,
            "it": PROMPT_TEMPLATE_DETAILED_IT,
        },
        "plain": {
            "de": PROMPT_TEMPLATE_ES_DE,
            "fr": PROMPT_TEMPLATE_ES_FR,
            "it": PROMPT_TEMPLATE_ES_IT,
        },
        "easy": {
            "de": PROMPT_TEMPLATE_LS_DE,
            "fr": PROMPT_TEMPLATE_LS_FR,
            "it": PROMPT_TEMPLATE_LS_IT,
        },
        "legal": {
            "de": PROMPT_TEMPLATE_LEGAL_DE,
            "fr": PROMPT_TEMPLATE_LEGAL_FR,
            "it": PROMPT_TEMPLATE_LEGAL_IT,
        },
    }

    _DEFAULT_STYLE = "detailed"

    _COMPLETENESS = {
        "complete": {
            "de": COMPLETE_PROMPT_DE,
            "fr": COMPLETE_PROMPT_FR,
            "it": COMPLETE_PROMPT_IT,
        },
        "condensed": {
            "de": CONDENSED_PROMPT_DE,
            "fr": CONDENSED_PROMPT_FR,
            "it": CONDENSED_PROMPT_IT,
        },
    }

    _DEFAULT_COMPLETENESS = "complete"

    _RULES = {
        "concise": {
            "de": RULES_CONCISE_DE,
            "fr": RULES_CONCISE_FR,
            "it": RULES_CONCISE_IT,
        },
        "detailed": {
            "de": RULES_DETAILED_DE,
            "fr": RULES_DETAILED_FR,
            "it": RULES_DETAILED_IT,
        },
        "plain": {
            "de": RULES_ES_DE,
            "fr": RULES_ES_FR,
            "it": RULES_ES_IT,
        },
        "easy": {
            "de": RULES_LS_DE,
            "fr": RULES_LS_FR,
            "it": RULES_LS_IT,
        },
        "legal": {
            "de": RULES_LEGAL_DE,
            "fr": RULES_LEGAL_FR,
            "it": RULES_LEGAL_IT,
        },
    }

    _DEFAULT_RULE = "detailed"

    @observe(name="MessageBuilder_build_summary_memory_prompt")
    def build_conversation_summary_prompt(
        self, llm_model: str, language: str, conversational_memory: str
    ) -> str:
        """
        Format the Summary Memory message to send to the appropriate LLM API.
        """

        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            conversation_summary_prompt = self._SUMMARY_MEMORY_PROMPT.get(
                language,
                self._SUMMARY_MEMORY_PROMPT.get(self._DEFAULT_LANGUAGE),
            ).format(conversational_memory=conversational_memory)

            return [
                {"role": "system", "content": conversation_summary_prompt},
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_chat_prompt")
    def build_chat_prompt(
        self,
        language: str,
        llm_model: str,
        context_docs: List[Dict],
        query: str,
        conversational_memory: str,
        response_style: str,
        response_format: str,
    ) -> Union[List[Dict], str]:
        """
        Format the RAG message to send to the appropriate LLM API.
        """

        if llm_model == "ollama/deepseek-r1:8b":
            rag_system_prompt = self._RAG_REASONING_SYSTEM_PROMPT.get(
                language,
                self._RAG_REASONING_SYSTEM_PROMPT.get(self._DEFAULT_LANGUAGE),
            )
        else:
            rag_system_prompt = self._RAG_SYSTEM_PROMPT.get(
                language, self._RAG_SYSTEM_PROMPT.get(self._DEFAULT_LANGUAGE)
            )

        completeness = self._COMPLETENESS.get(
            response_format,
            self._COMPLETENESS.get(self._DEFAULT_COMPLETENESS),
        ).get(
            language,
            self._COMPLETENESS.get(self._DEFAULT_COMPLETENESS).get(
                self._DEFAULT_LANGUAGE
            ),
        )

        rules = self._RULES.get(
            response_style, self._RULES.get(self._DEFAULT_RULE)
        ).get(
            language,
            self._RULES.get(self._DEFAULT_RULE).get(self._DEFAULT_LANGUAGE),
        )

        response_format = self._RESPONSE_FORMAT.get(
            response_style, self._RESPONSE_FORMAT.get(self._DEFAULT_STYLE)
        ).get(
            language,
            self._RESPONSE_FORMAT.get(self._DEFAULT_STYLE).get(
                self._DEFAULT_LANGUAGE
            ),
        )

        response_format = response_format.format(
            completeness=completeness,
            rules=rules,
        )

        rag_system_prompt = rag_system_prompt.format(
            context_docs=context_docs,
            conversational_memory=conversational_memory,
            response_format=response_format,
        )

        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            return [
                {"role": "system", "content": rag_system_prompt},
                {"role": "user", "content": query},
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    def build_chat_title_prompt(
        self,
        language: str,
        llm_model: str,
        query: str,
        assistant_response: str,
    ) -> List[Dict]:
        """
        Format the CreateChatTitle message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            chat_title_system_prompt = self._CHAT_TITLE_PROMPT.get(
                language, self._CHAT_TITLE_PROMPT.get(self._DEFAULT_LANGUAGE)
            )
            chat_title_system_prompt = chat_title_system_prompt.format(
                assistant_response=assistant_response
            )
            return [
                {"role": "system", "content": chat_title_system_prompt},
                {"role": "user", "content": query},
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    def build_source_description_prompt(
        self,
        language: str,
        llm_model: str,
        source_name: str,
        docs: str,
    ) -> List[Dict]:
        """
        Format the CreateSourceDescription message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            source_description_system_prompt = (
                self._SOURCE_DESCRIPTION_PROMPT.get(
                    language,
                    self._SOURCE_DESCRIPTION_PROMPT.get(
                        self._DEFAULT_LANGUAGE
                    ),
                )
            )
            source_description_system_prompt = (
                source_description_system_prompt.format(
                    source_name=source_name,
                    docs=docs,
                )
            )
            return [
                {
                    "role": "system",
                    "content": source_description_system_prompt,
                },
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_topic_check_prompt")
    def build_topic_check_prompt(
        self, language: str, llm_model: str, query: str
    ) -> Union[List[Dict], str]:
        """
        Format the Topic Check message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            topic_check_system_prompt = self._TOPIC_CHECK_PROMPT.get(
                language, self._TOPIC_CHECK_PROMPT.get(self._DEFAULT_LANGUAGE)
            )
            topic_check_system_prompt = topic_check_system_prompt.format(
                query=query,
            )
            return [
                {"role": "system", "content": topic_check_system_prompt},
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_unique_source_validation_prompt")
    def build_unique_source_validation_prompt(
        self, language: str, llm_model: str, query: str, source: Dict
    ) -> List[Dict]:
        """
        Format the Unique Source Validation message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            unique_source_validation_system_prompt = (
                self._UNIQUE_SOURCE_VALIDATION_PROMPT.get(
                    language,
                    self._UNIQUE_SOURCE_VALIDATION_PROMPT.get(
                        self._DEFAULT_LANGUAGE
                    ),
                )
            )

            unique_source_validation_system_prompt = (
                unique_source_validation_system_prompt.format(
                    query=query,
                    tags=source.get("tags"),
                    source=source.get("text"),
                )
            )
            return [
                {
                    "role": "system",
                    "content": unique_source_validation_system_prompt,
                },
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_intent_detection_prompt")
    async def build_intent_detection_prompt(
        self,
        language: str,
        llm_model: str,
        query: str,
        conversational_memory: str,
        db: Session = Depends(get_db),
    ) -> Union[List[Dict], str]:
        """
        Format the Intent Detection message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):

            # tags = await get_tags_descriptions(db, language)
            # formatted_tags = "\n".join([f"{tag[0]}: {tag[1]}" for tag in tags])

            # sources = await get_source_descriptions(db)
            # formatted_sources = "\n".join([f"{source['url']}: {source['description']}" for source in sources])

            intentions = await get_intentions_descriptions(db, language)
            formatted_intentions = "\n".join(
                [
                    f"{intent['name']}: {intent['description']}"
                    for intent in intentions
                ]
            )

            # TO DO: check duplicates
            # better formatting and prompt instruction

            intent_detection_system_prompt = self._INTENT_DETECTION_PROMPT.get(
                language,
                self._INTENT_DETECTION_PROMPT.get(self._DEFAULT_LANGUAGE),
            )
            intent_detection_system_prompt = (
                intent_detection_system_prompt.format(
                    conversational_memory=conversational_memory,
                    intentions=formatted_intentions,
                    query=query,
                )
            )
            return [
                {"role": "system", "content": intent_detection_system_prompt},
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_source_selection_prompt")
    async def build_source_selection_prompt(
        self,
        language: str,
        llm_model: str,
        query: str,
        intent: str,
        conversational_memory: str,
        db: Session = Depends(get_db),
    ) -> Union[List[Dict], str]:
        """
        Format the Source Selection message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):

            sources = await get_source_descriptions(db)
            formatted_sources = "\n\n".join(
                [
                    f"**{source['url']}**: {source['description']}"
                    for source in sources
                ]
            )
            source_selection_system_prompt = self._SOURCE_SELECTION_PROMPT.get(
                language,
                self._SOURCE_SELECTION_PROMPT.get(self._DEFAULT_LANGUAGE),
            )
            source_selection_system_prompt = (
                source_selection_system_prompt.format(
                    query=query,
                    intent=intent,
                    conversational_memory=conversational_memory,
                    sources=formatted_sources,
                )
            )
            return [
                {"role": "system", "content": source_selection_system_prompt},
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_tag_selection_prompt")
    async def build_tag_selection_prompt(
        self,
        language: str,
        llm_model: str,
        query: str,
        intent: str,
        sources: List[str],
        conversational_memory: str,
        db: Session = Depends(get_db),
    ) -> Union[List[Dict], str]:
        """
        Format the Source Selection message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):

            tags = await get_tags_descriptions(db, language)
            formatted_tags = "\n".join(
                [f"**{tag['name']}**: {tag['description']}" for tag in tags]
            )
            tags_selection_system_prompt = self._TAGS_SELECTION_PROMPT.get(
                language,
                self._TAGS_SELECTION_PROMPT.get(self._DEFAULT_LANGUAGE),
            )
            tags_selection_system_prompt = tags_selection_system_prompt.format(
                query=query,
                intent=intent,
                sources=sources,
                tags=formatted_tags,
                conversational_memory=conversational_memory,
            )
            return [
                {"role": "system", "content": tags_selection_system_prompt},
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_agent_handoff_prompt")
    async def build_agent_handoff_prompt(
        self,
        language: str,
        llm_model: str,
        query: str,
        intent: str,
        tags: List[str],
        sources: List[str],
        conversational_memory: str,
    ) -> Union[List[Dict], str]:
        """
        Format the Agent Handoff message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):

            agent_handoff_system_prompt = self._AGENT_HANDOFF_PROMPT.get(
                language,
                self._AGENT_HANDOFF_PROMPT.get(self._DEFAULT_LANGUAGE),
            )
            agent_handoff_system_prompt = agent_handoff_system_prompt.format(
                query=query,
                intent=intent,
                tags=tags,
                sources=sources,
                conversational_memory=conversational_memory,
            )
            return [
                {"role": "system", "content": agent_handoff_system_prompt},
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_function_call_prompt")
    def build_function_call_prompt(
        self, language: str, llm_model: str, query: str, func_metadata: str
    ) -> Union[List[Dict], str]:
        """
        Format the Function Call message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            pension_function_calling_system_prompt = (
                self._PENSION_FUNCTION_CALLING_PROMPT.get(
                    language,
                    self._PENSION_FUNCTION_CALLING_PROMPT.get(
                        self._DEFAULT_LANGUAGE
                    ),
                )
            )
            pension_function_calling_system_prompt = (
                pension_function_calling_system_prompt.format(
                    query=query,
                    func_metadata=func_metadata,
                )
            )
            return [
                {
                    "role": "system",
                    "content": pension_function_calling_system_prompt,
                },
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_parse_translate_args_prompt")
    def build_parse_translate_args_prompt(
        self,
        language: str,
        llm_model: str,
        query: str,
    ) -> Union[List[Dict], str]:
        """
        Format the Parse translate args message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            parse_translate_args_system_prompt = (
                self._PARSE_TRANSLATE_ARGS_PROMPT.get(
                    language,
                    self._PARSE_TRANSLATE_ARGS_PROMPT.get(
                        self._DEFAULT_LANGUAGE
                    ),
                )
            )
            parse_translate_args_system_prompt = (
                parse_translate_args_system_prompt.format(
                    query=query,
                )
            )
            return [
                {
                    "role": "system",
                    "content": parse_translate_args_system_prompt,
                },
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_agent_summarize_prompt")
    def build_agent_summarize_prompt(
        self,
        language: str,
        llm_model: str,
        query: str,
        conversational_memory: str,
    ) -> Union[List[Dict], str]:
        """
        Format the agent summarize message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            agent_summarize_system_prompt = self._AGENT_SUMMARIZE_PROMPT.get(
                language,
                self._AGENT_SUMMARIZE_PROMPT.get(self._DEFAULT_LANGUAGE),
            )
            agent_summarize_system_prompt = (
                agent_summarize_system_prompt.format(
                    query=query,
                    conversational_memory=conversational_memory,
                )
            )
            return [
                {
                    "role": "system",
                    "content": agent_summarize_system_prompt,
                },
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(
        name="MessageBuilder_build_ask_user_feedback_no_valid_docs_prompt"
    )
    def build_ask_user_feedback_no_valid_docs_prompt(
        self,
        language: str,
        llm_model: str,
        query: str,
        reasons: List[str],
        tags: List[str],
        invalid_docs: List[str],
        conversational_memory: str,
    ) -> Union[List[Dict], str]:
        """
        Format the Ask user feedback message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            ask_user_feedback_no_valid_docs_system_prompt = (
                self._NO_VALIDATED_DOCS_PROMPT.get(
                    language,
                    self._NO_VALIDATED_DOCS_PROMPT.get(self._DEFAULT_LANGUAGE),
                )
            )
            ask_user_feedback_no_valid_docs_system_prompt = (
                ask_user_feedback_no_valid_docs_system_prompt.format(
                    query=query,
                    reasons=reasons,
                    tags=tags,
                    invalid_docs=invalid_docs,
                    conversational_memory=conversational_memory,
                )
            )
            return [
                {
                    "role": "system",
                    "content": ask_user_feedback_no_valid_docs_system_prompt,
                },
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(
        name="MessageBuilder_build_ask_user_feedback_no_valid_docs_prompt"
    )
    def build_user_preferences_prompt(
        self,
        language: str,
        llm_model: str,
        query: str,
        conversational_memory: str,
    ) -> Union[List[Dict], str]:
        """
        Format the Ask user feedback message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            update_user_preferences_system_prompt = (
                self._UPDATE_USER_PREFERENCES_PROMPT.get(
                    language,
                    self._NO_VALIDATED_DOCS_PROMPT.get(self._DEFAULT_LANGUAGE),
                )
            )
            update_user_preferences_system_prompt = (
                update_user_preferences_system_prompt.format(
                    query=query,
                    conversational_memory=conversational_memory,
                )
            )
            return [
                {
                    "role": "system",
                    "content": update_user_preferences_system_prompt,
                },
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_query_rewriting_prompt")
    def build_query_rewriting_prompt(
        self,
        language: str,
        llm_model: str,
        n_alt_queries: int,
        query: str,
        conversational_memory: str,
    ) -> List[Dict]:
        """
        Format the Query Rewriting message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            query_rewriting_system_prompt = self._QUERY_REWRITING_PROMPT.get(
                language,
                self._QUERY_REWRITING_PROMPT.get(self._DEFAULT_LANGUAGE),
            )
            query_rewriting_system_prompt = (
                query_rewriting_system_prompt.format(
                    n_alt_queries=n_alt_queries,
                    query=query,
                    conversational_memory=conversational_memory,
                )
            )
            return [
                {"role": "system", "content": query_rewriting_system_prompt},
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_query_statement_rewriting_prompt")
    def build_query_statement_rewriting_prompt(
        self,
        language: str,
        llm_model: str,
        n_alt_queries: int,
        query: str,
        conversational_memory: str,
    ) -> List[Dict]:
        """
        Format the Query Statement Rewriting message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            query_statement_rewriting_system_prompt = (
                self._QUERY_STATEMENT_REWRITING_PROMPT.get(
                    language,
                    self._QUERY_STATEMENT_REWRITING_PROMPT.get(
                        self._DEFAULT_LANGUAGE
                    ),
                )
            )
            query_statement_rewriting_system_prompt = (
                query_statement_rewriting_system_prompt.format(
                    n_alt_queries=n_alt_queries,
                    query=query,
                    conversational_memory=conversational_memory,
                )
            )
            return [
                {
                    "role": "system",
                    "content": query_statement_rewriting_system_prompt,
                },
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_contextual_compression_prompt")
    def build_contextual_compression_prompt(
        self, language: str, llm_model: str, context_doc: str, query: str
    ) -> List[Dict]:
        """
        Format the Contextual Compression message to send to the appropriate LLM API.
        """
        # For OpenAI LLM models
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            contextual_compression_system_prompt = (
                self._CONTEXTUAL_COMPRESSION_PROMPT.get(
                    language,
                    self._CONTEXTUAL_COMPRESSION_PROMPT.get(
                        self._DEFAULT_LANGUAGE
                    ),
                )
            )
            contextual_compression_system_prompt = (
                contextual_compression_system_prompt.format(
                    context_doc=context_doc, query=query
                )
            )
            return [
                {
                    "role": "system",
                    "content": contextual_compression_system_prompt,
                },
            ]
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")

    @observe(name="MessageBuilder_build_summarize_prompt")
    def build_summarize_prompt(
        self,
        language: str,
        llm_model: str,
        command: str,
        input_text: str,
        mode: str,
        style: str,
    ) -> List[Dict]:
        """
        Format the SummarizeCommand message to send to the appropriate LLM API.
        """
        if (
            llm_model
            in SUPPORTED_OPENAI_LLM_MODELS
            + SUPPORTED_AZUREOPENAI_LLM_MODELS
            + SUPPORTED_ANTHROPIC_LLM_MODELS
            + SUPPORTED_GROQ_LLM_MODELS
            + SUPPORTED_OLLAMA_LLM_MODELS
            + SUPPORTED_MLX_LLM_MODELS
            + SUPPORTED_LLAMACPP_LLM_MODELS
        ):
            if command == "/summarize":
                summarize_command_system_prompt = (
                    self._SUMMARIZE_COMMAND_PROMPT.get(
                        language,
                        self._SUMMARIZE_COMMAND_PROMPT.get(
                            self._DEFAULT_LANGUAGE
                        ),
                    )
                )
                summarize_command_system_prompt = (
                    SUMMARIZE_COMMAND_PROMPT_DE.format(
                        input_text=input_text, mode=mode, style=style
                    )
                )
                return [
                    {
                        "role": "system",
                        "content": summarize_command_system_prompt,
                    },
                    {"role": "user", "content": command},
                ]
            else:
                raise ValueError(f"Unsupported command: {command}")
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")
