from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx

from utils.logging import get_logger

logger = get_logger(__name__)


class BaseLLMClientFactory(ABC):
    """Abstract base class for LLM client factories"""

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        self.http_client = http_client

    @abstractmethod
    def create_client(self, config: Dict[str, Any]):
        """Create a client instance with the given configuration"""
        pass


class OpenAIClientFactory(BaseLLMClientFactory):
    """Factory for creating OpenAI clients"""

    def create_client(self, config: Dict[str, Any]):
        import openai

        if config.get("azure_deployment"):
            return openai.AsyncAzureOpenAI(
                api_key=config["api_key"],
                api_version=config["api_version"],
                azure_endpoint=config["api_endpoint"],
                http_client=self.http_client,
            )
        else:
            return openai.AsyncOpenAI(
                api_key=config["api_key"],
                http_client=self.http_client,
            )


class AnthropicClientFactory(BaseLLMClientFactory):
    """Factory for creating Anthropic clients"""

    def create_client(self, config: Dict[str, Any]):
        from anthropic import AsyncAnthropic

        return AsyncAnthropic(
            api_key=config["api_key"],
            http_client=self.http_client,
        )


class GroqClientFactory(BaseLLMClientFactory):
    """Factory for creating Groq clients"""

    def create_client(self, config: Dict[str, Any]):
        from groq import AsyncGroq

        return AsyncGroq(
            api_key=config["api_key"],
            http_client=self.http_client,
        )


class OllamaClientFactory(BaseLLMClientFactory):
    """Factory for creating Ollama clients"""

    def create_client(self, config: Dict[str, Any]):
        from ollama import AsyncClient

        return AsyncClient(
            host=config.get("api_endpoint", "http://localhost:11434"),
            http_client=self.http_client,
        )


class ClientFactoryRegistry:
    """Registry for client factories"""

    def __init__(self):
        self._factories = {
            "openai": OpenAIClientFactory(),
            "azure": OpenAIClientFactory(),
            "anthropic": AnthropicClientFactory(),
            "groq": GroqClientFactory(),
            "ollama": OllamaClientFactory(),
        }

    def get_factory(self, provider: str) -> BaseLLMClientFactory:
        """Get factory for specified provider"""
        factory = self._factories.get(provider.lower())
        if not factory:
            raise ValueError(f"Unsupported provider: {provider}")
        return factory

    def register_factory(self, provider: str, factory: BaseLLMClientFactory):
        """Register a new factory"""
        self._factories[provider.lower()] = factory


# Create singleton instance
client_factory_registry = ClientFactoryRegistry()
