from typing import List, Dict
from rag.prompts import OPENAI_RAG_SYSTEM_PROMPT_DE, OPENAI_RAG_SYSTEM_PROMPT_FR, OPENAI_RAG_SYSTEM_PROMPT_IT, QUERY_REWRITING_PROMPT_DE, QUERY_REWRITING_PROMPT_FR, QUERY_REWRITING_PROMPT_IT, CONTEXTUAL_COMPRESSION_PROMPT_DE, CONTEXTUAL_COMPRESSION_PROMPT_FR, CONTEXTUAL_COMPRESSION_PROMPT_IT
from config.llm_config import SUPPORTED_OPENAI_LLM_MODELS, SUPPORTED_AZUREOPENAI_LLM_MODELS, SUPPORTED_ANTHROPIC_LLM_MODELS, SUPPORTED_GROQ_LLM_MODELS

from langfuse.decorators import observe

class MessageBuilder:

    def __init__(self, session_language: str, llm_model: str):
        self.session_language = session_language
        self.llm_model = llm_model

    @observe()
    def build_chat_prompt(self, context_docs: List[Dict], query: str) -> List[Dict]:
        """
        Format the RAG message to send to the appropriate LLM API.
        """
        # For OpenAI LLM models
        if self.llm_model in SUPPORTED_OPENAI_LLM_MODELS + SUPPORTED_AZUREOPENAI_LLM_MODELS:
            if self.session_language == "de":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_DE.format(context_docs=context_docs, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "fr":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_FR.format(context_docs=context_docs, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "it":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_IT.format(context_docs=context_docs, query=query)
                return [{"role": "system", "content": prompt},]

        # NEED TO IMPLEMENT OPTIMIZED ANTHROPIC PROMPT
        elif self.llm_model in SUPPORTED_ANTHROPIC_LLM_MODELS:
            if self.session_language == "de":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_DE.format(context_docs=context_docs, query=query)
                return [{"role": "user", "content": prompt},]
            elif self.session_language == "fr":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_FR.format(context_docs=context_docs, query=query)
                return [{"role": "user", "content": prompt},]
            elif self.session_language == "it":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_IT.format(context_docs=context_docs, query=query)
                return [{"role": "user", "content": prompt},]

        # NEED TO IMPLEMENT OPTIMIZED GROQ PROMPT
        elif self.llm_model in SUPPORTED_GROQ_LLM_MODELS:
            if self.session_language == "de":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_DE.format(context_docs=context_docs, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "fr":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_FR.format(context_docs=context_docs, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "it":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_IT.format(context_docs=context_docs, query=query)
                return [{"role": "system", "content": prompt},]

    def build_query_rewriting_prompt(self, n_alt_queries: int, query: str) -> List[Dict]:
        """
        Format the Query Rewriting message to send to the appropriate LLM API.
        """
        # For OpenAI LLM models
        if self.llm_model in SUPPORTED_OPENAI_LLM_MODELS + SUPPORTED_AZUREOPENAI_LLM_MODELS:
            if self.session_language == "de":
                prompt = QUERY_REWRITING_PROMPT_DE.format(n_alt_queries=n_alt_queries, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "fr":
                prompt = QUERY_REWRITING_PROMPT_FR.format(n_alt_queries=n_alt_queries, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "it":
                prompt = QUERY_REWRITING_PROMPT_IT.format(n_alt_queries=n_alt_queries, query=query)
                return [{"role": "system", "content": prompt},]

        # NEED TO IMPLEMENT OPTIMIZED CONTEXTUAL COMPRESSION
        elif self.llm_model in SUPPORTED_ANTHROPIC_LLM_MODELS:
            if self.session_language == "de":
                prompt = QUERY_REWRITING_PROMPT_DE.format(n_alt_queries=n_alt_queries, query=query)
                return [{"role": "user", "content": prompt},]
            elif self.session_language == "fr":
                prompt = QUERY_REWRITING_PROMPT_FR.format(n_alt_queries=n_alt_queries, query=query)
                return [{"role": "user", "content": prompt},]
            elif self.session_language == "it":
                prompt = QUERY_REWRITING_PROMPT_IT.format(n_alt_queries=n_alt_queries, query=query)
                return [{"role": "user", "content": prompt},]

        # NEED TO IMPLEMENT OPTIMIZED GROQ PROMPT
        elif self.llm_model in SUPPORTED_GROQ_LLM_MODELS:
            if self.session_language == "de":
                prompt = QUERY_REWRITING_PROMPT_DE.format(n_alt_queries=n_alt_queries, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "fr":
                prompt = QUERY_REWRITING_PROMPT_FR.format(n_alt_queries=n_alt_queries, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "it":
                prompt = QUERY_REWRITING_PROMPT_IT.format(n_alt_queries=n_alt_queries, query=query)
                return [{"role": "system", "content": prompt},]

    def build_contextual_compression_prompt(self, context_doc: str, query: str) -> List[Dict]:
        """
        Format the Contextual Compression message to send to the appropriate LLM API.
        """
        # For OpenAI LLM models
        if self.llm_model in SUPPORTED_OPENAI_LLM_MODELS + SUPPORTED_AZUREOPENAI_LLM_MODELS:
            if self.session_language == "de":
                prompt = CONTEXTUAL_COMPRESSION_PROMPT_DE.format(context_doc=context_doc, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "fr":
                prompt = CONTEXTUAL_COMPRESSION_PROMPT_FR.format(context_doc=context_doc, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "it":
                prompt = CONTEXTUAL_COMPRESSION_PROMPT_IT.format(context_doc=context_doc, query=query)
                return [{"role": "system", "content": prompt},]

        # NEED TO IMPLEMENT OPTIMIZED CONTEXTUAL COMPRESSION
        elif self.llm_model in SUPPORTED_ANTHROPIC_LLM_MODELS:
            if self.session_language == "de":
                prompt = CONTEXTUAL_COMPRESSION_PROMPT_DE.format(context_doc=context_doc, query=query)
                return [{"role": "user", "content": prompt},]
            elif self.session_language == "fr":
                prompt = CONTEXTUAL_COMPRESSION_PROMPT_FR.format(context_doc=context_doc, query=query)
                return [{"role": "user", "content": prompt},]
            elif self.session_language == "it":
                prompt = CONTEXTUAL_COMPRESSION_PROMPT_IT.format(context_doc=context_doc, query=query)
                return [{"role": "user", "content": prompt},]

        # NEED TO IMPLEMENT OPTIMIZED GROQ PROMPT
        elif self.llm_model in SUPPORTED_GROQ_LLM_MODELS:
            if self.session_language == "de":
                prompt = CONTEXTUAL_COMPRESSION_PROMPT_DE.format(context_doc=context_doc, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "fr":
                prompt = CONTEXTUAL_COMPRESSION_PROMPT_FR.format(context_doc=context_doc, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "it":
                prompt = CONTEXTUAL_COMPRESSION_PROMPT_IT.format(context_doc=context_doc, query=query)
                return [{"role": "system", "content": prompt},]