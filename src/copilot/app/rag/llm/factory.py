from rag.llm.base import BaseLLM
from rag.llm import OpenAILLM  # , MlxLLM, LlamaCppLLM, HuggingFaceLLM
from config.rag.config import LLMConfig

from dataclasses import asdict
from utils.enum import Client


class LLMFactory:
    @staticmethod
    def get_llm_client(llm_config: LLMConfig) -> BaseLLM:
        """
        Factory method to instantiate llm clients based on a string identifier.

        Parameters
        ----------
        llm_config : LLMConfig
            LLM model configuration. Currently supported models are in config/rag/ai_models/supported.py.

        Returns
        -------
        LLM
            An instance of the appropriate llm client.

        Raises
        ------
        ValueError
            If the `llm_model` is not supported.
        """
        api = llm_config.model.value.api
        if api == Client.OPENAI:  # or api == Client.GROQ:
            return OpenAILLM(**asdict(llm_config))
        # elif api == Client.LOCAL:
        #     return MlxLLM(model_name=llm_model)
        # elif api == SUPPORTED_LLAMACPP_LLM_MODELS:
        #     return LlamaCppLLM(model_name=llm_model)
        # elif api == SUPPORTED_HUGGINGFACE_LLM_MODELS:
        #     return HuggingFaceLLM(model_name=llm_model)
        else:
            raise ValueError(f"Unsupported api: {api}")
