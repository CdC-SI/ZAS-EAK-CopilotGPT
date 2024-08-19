from rag.llm.base import BaseLLM
from rag.llm import OpenAILLM#, MlxLLM, LlamaCppLLM, HuggingFaceLLM
from config.llm_config import SUPPORTED_OPENAI_LLM_MODELS#, SUPPORTED_MLX_LLM_MODELS, SUPPORTED_LLAMACPP_LLM_MODELS, SUPPORTED_HUGGINGFACE_LLM_MODELS


class LLMFactory:
    @staticmethod
    def get_llm_client(llm_model: str, stream: bool) -> BaseLLM:
        """
        Factory method to instantiate llm clients based on a string identifier.

        Parameters
        ----------
        llm_model : str
            The name of the LLM model. Currently supported models are in config/llm_config.py.
        stream : bool
            Whether to stream the response as events or return a single text response.

        Returns
        -------
        LLM
            An instance of the appropriate llm client.

        Raises
        ------
        ValueError
            If the `llm_model` is not supported.
        """
        if llm_model in SUPPORTED_OPENAI_LLM_MODELS:
            return OpenAILLM(model_name=llm_model, stream=stream)
        # elif llm_model in SUPPORTED_MLX_LLM_MODELS:
        #     return MlxLLM(model_name=llm_model)
        # elif llm_model in SUPPORTED_LLAMACPP_LLM_MODELS:
        #     return LlamaCppLLM(model_name=llm_model)
        # elif llm_model in SUPPORTED_HUGGINGFACE_LLM_MODELS:
        #     return HuggingFaceLLM(model_name=llm_model)
        else:
            raise ValueError(f"Unsupported llm model type: {llm_model}")