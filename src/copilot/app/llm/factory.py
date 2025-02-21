from llm.base import BaseLLM
from llm import OpenAILLM, AnthropicLLM, MLXLLM, LlamaCppLLM, OllamaLLM
from config.llm_config import (
    SUPPORTED_OPENAI_LLM_MODELS,
    SUPPORTED_AZUREOPENAI_LLM_MODELS,
    SUPPORTED_ANTHROPIC_LLM_MODELS,
    SUPPORTED_GROQ_LLM_MODELS,
)


import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LLMFactory:
    @staticmethod
    def get_llm_client(
        model: str,
        stream: bool,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> BaseLLM:
        """
        Factory method to instantiate llm clients based on a string identifier.

        Parameters
        ----------
        model : str
            The name of the LLM model. Currently supported models are in config/llm_config.py.
        stream : bool
            Whether to stream the response as events or return a single text response.
        temperature : float
            Sampling temperature between 0 and 1. Higher values make output more random.
        top_p : float
            Nucleus sampling parameter between 0 and 1. Lower values make output more focused.
        max_tokens : int
            Maximum number of tokens to generate in the response.

        Returns
        -------
        BaseLLM
            An instance of the appropriate LLM client implementing the BaseLLM interface.

        Raises
        ------
        ValueError
            If the provided model name is not supported or configured.
        """
        if (
            model in SUPPORTED_OPENAI_LLM_MODELS
            or model in SUPPORTED_AZUREOPENAI_LLM_MODELS
            or model in SUPPORTED_GROQ_LLM_MODELS
        ):
            return OpenAILLM(
                model=model,
                stream=stream,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
        elif model in SUPPORTED_ANTHROPIC_LLM_MODELS:
            return AnthropicLLM(
                model=model,
                stream=stream,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
        elif model.startswith("mlx-community:"):
            return MLXLLM(
                model=model,
                stream=stream,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
        elif model.startswith("llama-cpp:"):
            return LlamaCppLLM(
                model=model,
                stream=stream,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
        elif model.startswith("ollama:"):
            return OllamaLLM(
                model=model,
                stream=stream,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
        else:
            raise ValueError(
                f"Unsupported llm model: {model}. Please check documentation at https://cdc-si.github.io/ZAS-EAK-CopilotGPT/ for supported models."
            )
