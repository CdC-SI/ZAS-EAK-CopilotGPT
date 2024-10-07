from typing import List, Dict
from rag.prompts import OPENAI_RAG_SYSTEM_PROMPT_DE, OPENAI_RAG_SYSTEM_PROMPT_FR, OPENAI_RAG_SYSTEM_PROMPT_IT, QUERY_REWRITING_PROMPT, CONTEXTUAL_COMPRESSION_PROMPT
from config.llm_config import SUPPORTED_OPENAI_LLM_MODELS, SUPPORTED_AZUREOPENAI_LLM_MODELS, SUPPORTED_ANTHROPIC_LLM_MODELS, SUPPORTED_GROQ_LLM_MODELS

from langfuse.decorators import observe

class MessageBuilder:

    def __init__(self, session_language: str, llm_model: str):
        self.session_language = session_language
        self.llm_model = llm_model

    @observe()
    def build_chat_prompt(self, context_docs: List[Dict], query: str) -> List[Dict]:
        """
        Format the RAG message to send to the appropriate API.
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
        elif self.llm_model in SUPPORTED_ANTHROPIC_LLM_MODELS:
            if self.session_language == "de":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_DE.format(context_docs=context_docs, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "fr":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_FR.format(context_docs=context_docs, query=query)
                return [{"role": "system", "content": prompt},]
            elif self.session_language == "it":
                prompt = OPENAI_RAG_SYSTEM_PROMPT_IT.format(context_docs=context_docs, query=query)
                return [{"role": "system", "content": prompt},]

    def build_retriever_prompt(self):
        pass
