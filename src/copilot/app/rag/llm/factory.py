from rag.llm.base import BaseLLM
from rag.llm import OpenAILLM, AnthropicLLM, MLXLLM, LlamaCppLLM
from config.llm_config import SUPPORTED_OPENAI_LLM_MODELS, SUPPORTED_AZUREOPENAI_LLM_MODELS, SUPPORTED_ANTHROPIC_LLM_MODELS, SUPPORTED_GROQ_LLM_MODELS


import logging
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMFactory:
    @staticmethod
    def get_llm_client(llm_model: str, stream: bool, temperature: float, top_p: float, max_tokens: int) -> BaseLLM:
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
        if llm_model in SUPPORTED_OPENAI_LLM_MODELS or llm_model in SUPPORTED_AZUREOPENAI_LLM_MODELS or llm_model in SUPPORTED_GROQ_LLM_MODELS:
            return OpenAILLM(model_name=llm_model,
                             stream=stream,
                             temperature=temperature,
                             top_p=top_p,
                             max_tokens=max_tokens)
        elif llm_model in SUPPORTED_ANTHROPIC_LLM_MODELS:
            return AnthropicLLM(model_name=llm_model,
                                stream=stream,
                                temperature=temperature,
                                top_p=top_p,
                                max_tokens=max_tokens)
        elif llm_model.startswith("mlx-community/"):
            return MLXLLM(model_name=llm_model,
                                stream=stream,
                                temperature=temperature,
                                top_p=top_p,
                                max_tokens=max_tokens)
        elif llm_model.startswith("llama-cpp/"):
            return LlamaCppLLM(model_name=llm_model,
                                stream=stream,
                                temperature=temperature,
                                top_p=top_p,
                                max_tokens=max_tokens)
        else:
            raise ValueError(f"Unsupported llm model: {llm_model}. Please check documentation at https://cdc-si.github.io/ZAS-EAK-CopilotGPT/ for supported models.")
