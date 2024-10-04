from config.llm_config import SUPPORTED_OPENAI_LLM_MODELS, SUPPORTED_ANTHROPIC_LLM_MODELS
from rag.prompts.prompts import OPENAI_RAG_SYSTEM_PROMPT_DE

class PromptFactory:
    """
    A factory class for creating a prompt based on the chosen LLM.

    This factory method allows for the creation of a prompt with specific system/user/assistant tags, depending on the specified LLM.
    """
    @staticmethod
    def get_prompt(llm_model: str) -> str:
        """
        Create a prompt based on the given LLM.

        Parameters
        ----------
        llm_model: str

        Returns
        -------
        str
            A prompt instance configured with the specified LLM system/user/assistant tags.

        Raises
        ------
        ValueError
            If an unsupported LLM model is provided.
        """
        if llm_model in SUPPORTED_OPENAI_LLM_MODELS:
            return OPENAI_RAG_SYSTEM_PROMPT_DE
        elif llm_model in SUPPORTED_ANTHROPIC_LLM_MODELS:
            return OPENAI_RAG_SYSTEM_PROMPT_DE