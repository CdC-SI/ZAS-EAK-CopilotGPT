from abc import ABC, abstractmethod
from typing import Dict, Type, Optional

from llm.base import BaseLLM
from config.llm_config_schemas import LLMConfiguration
from config.clients_config import ProxyConfig
from config.llm_config_schemas import StreamingConfiguration
from utils.logging import get_logger

logger = get_logger(__name__)


class LLMProviderFactory(ABC):
    """Abstract factory for creating LLM clients"""

    @abstractmethod
    def create_client(
        self,
        config: LLMConfiguration,
        proxy_config: ProxyConfig,
        streaming_config: Optional[StreamingConfiguration] = None,
    ) -> BaseLLM:
        """Create an LLM client with the given configuration"""
        pass


class OpenAIProviderFactory(LLMProviderFactory):
    """Factory for creating OpenAI LLM clients"""

    def create_client(
        self,
        config: LLMConfiguration,
        proxy_config: ProxyConfig,
        streaming_config: Optional[StreamingConfiguration] = None,
    ) -> BaseLLM:
        from llm.openai import OpenAILLM

        if streaming_config:
            return OpenAILLM(
                model=config.model,
                stream=config.stream,
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
                streaming_config=streaming_config,
            )
        return OpenAILLM(
            model=config.model,
            stream=config.stream,
            temperature=config.temperature,
            top_p=config.top_p,
            max_tokens=config.max_tokens,
        )


class AnthropicProviderFactory(LLMProviderFactory):
    """Factory for creating Anthropic LLM clients"""

    def create_client(
        self,
        config: LLMConfiguration,
        proxy_config: ProxyConfig,
        streaming_config: Optional[StreamingConfiguration] = None,
    ) -> BaseLLM:
        from llm.anthropic import AnthropicLLM

        if streaming_config:
            return AnthropicLLM(
                model=config.model,
                stream=config.stream,
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
                streaming_config=streaming_config,
            )
        return AnthropicLLM(
            model=config.model,
            stream=config.stream,
            temperature=config.temperature,
            top_p=config.top_p,
            max_tokens=config.max_tokens,
        )


class MLXProviderFactory(LLMProviderFactory):
    """Factory for creating MLX LLM clients"""

    def create_client(
        self,
        config: LLMConfiguration,
        proxy_config: ProxyConfig,
        streaming_config: Optional[StreamingConfiguration] = None,
    ) -> BaseLLM:
        from llm.mlx import MLXLLM

        if streaming_config:
            return MLXLLM(
                model=config.model,
                stream=config.stream,
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
                streaming_config=streaming_config,
            )
        return MLXLLM(
            model=config.model,
            stream=config.stream,
            temperature=config.temperature,
            top_p=config.top_p,
            max_tokens=config.max_tokens,
        )


class LlamaCppProviderFactory(LLMProviderFactory):
    """Factory for creating LlamaCpp LLM clients"""

    def create_client(
        self,
        config: LLMConfiguration,
        proxy_config: ProxyConfig,
        streaming_config: Optional[StreamingConfiguration] = None,
    ) -> BaseLLM:
        from llm.llama_cpp import LlamaCppLLM

        if streaming_config:
            return LlamaCppLLM(
                model=config.model,
                stream=config.stream,
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
                streaming_config=streaming_config,
            )
        return LlamaCppLLM(
            model=config.model,
            stream=config.stream,
            temperature=config.temperature,
            top_p=config.top_p,
            max_tokens=config.max_tokens,
        )


class OllamaProviderFactory(LLMProviderFactory):
    """Factory for creating Ollama LLM clients"""

    def create_client(
        self,
        config: LLMConfiguration,
        proxy_config: ProxyConfig,
        streaming_config: Optional[StreamingConfiguration] = None,
    ) -> BaseLLM:
        from llm.ollama import OllamaLLM

        if streaming_config:
            return OllamaLLM(
                model=config.model,
                stream=config.stream,
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
                streaming_config=streaming_config,
            )
        return OllamaLLM(
            model=config.model,
            stream=config.stream,
            temperature=config.temperature,
            top_p=config.top_p,
            max_tokens=config.max_tokens,
        )


class GroqProviderFactory(LLMProviderFactory):
    """Factory for creating Groq LLM clients"""

    def create_client(
        self,
        config: LLMConfiguration,
        proxy_config: ProxyConfig,
        streaming_config: Optional[StreamingConfiguration] = None,
    ) -> BaseLLM:
        from llm.openai import OpenAILLM  # Groq uses OpenAI-compatible client

        if streaming_config:
            return OpenAILLM(
                model=config.model,
                stream=config.stream,
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
                streaming_config=streaming_config,
            )
        return OpenAILLM(
            model=config.model,
            stream=config.stream,
            temperature=config.temperature,
            top_p=config.top_p,
            max_tokens=config.max_tokens,
        )


# Registry of provider factories
PROVIDER_FACTORIES: Dict[str, Type[LLMProviderFactory]] = {
    "openai": OpenAIProviderFactory,
    "azure": OpenAIProviderFactory,  # Azure uses OpenAI-compatible client
    "anthropic": AnthropicProviderFactory,
    "groq": GroqProviderFactory,
    "mlx": MLXProviderFactory,
    "llama-cpp": LlamaCppProviderFactory,
    "ollama": OllamaProviderFactory,
}


def get_provider_factory(provider: str) -> LLMProviderFactory:
    """
    Get the appropriate provider factory for the given provider.

    Parameters
    ----------
    provider : str
        The provider identifier

    Returns
    -------
    LLMProviderFactory
        An instance of the appropriate provider factory

    Raises
    ------
    ValueError
        If the provider is not supported
    """
    factory_class = PROVIDER_FACTORIES.get(provider.lower())
    if not factory_class:
        raise ValueError(f"Unsupported provider: {provider}")

    try:
        return factory_class()
    except Exception as e:
        logger.error(
            f"Error creating factory for provider {provider}: {str(e)}"
        )
        raise


# Create singleton instances for each provider factory
openai_factory = OpenAIProviderFactory()
anthropic_factory = AnthropicProviderFactory()
mlx_factory = MLXProviderFactory()
llama_cpp_factory = LlamaCppProviderFactory()
ollama_factory = OllamaProviderFactory()
groq_factory = GroqProviderFactory()
