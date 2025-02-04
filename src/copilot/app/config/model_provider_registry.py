from typing import Dict, Any, Optional
from dataclasses import dataclass
from .llm_config import (
    SUPPORTED_OPENAI_LLM_MODELS,
    SUPPORTED_AZUREOPENAI_LLM_MODELS,
    SUPPORTED_ANTHROPIC_LLM_MODELS,
    SUPPORTED_GROQ_LLM_MODELS,
    SUPPORTED_MLX_LLM_MODELS,
    SUPPORTED_LLAMACPP_LLM_MODELS,
    SUPPORTED_OLLAMA_LLM_MODELS,
)
from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ProviderInfo:
    """Information about a model provider"""

    provider: str
    requires_api_key: bool = True
    requires_endpoint: bool = False
    supports_streaming: bool = True
    defaults: Dict[str, Any] = None

    def __post_init__(self):
        if self.defaults is None:
            self.defaults = {}


class ModelProviderRegistry:
    """Registry managing model-provider mappings and configurations"""

    def __init__(self):
        self._providers: Dict[str, ProviderInfo] = {
            "openai": ProviderInfo(
                provider="openai",
                requires_api_key=True,
                requires_endpoint=False,
                supports_streaming=True,
            ),
            "azure": ProviderInfo(
                provider="azure",
                requires_api_key=True,
                requires_endpoint=True,
                supports_streaming=True,
            ),
            "anthropic": ProviderInfo(
                provider="anthropic",
                requires_api_key=True,
                requires_endpoint=False,
                supports_streaming=True,
            ),
            "groq": ProviderInfo(
                provider="groq",
                requires_api_key=True,
                requires_endpoint=False,
                supports_streaming=True,
            ),
            "mlx": ProviderInfo(
                provider="mlx",
                requires_api_key=False,
                requires_endpoint=True,
                supports_streaming=True,
            ),
            "llama-cpp": ProviderInfo(
                provider="llama-cpp",
                requires_api_key=False,
                requires_endpoint=True,
                supports_streaming=True,
            ),
            "ollama": ProviderInfo(
                provider="ollama",
                requires_api_key=False,
                requires_endpoint=True,
                supports_streaming=True,
            ),
        }

        self._model_mappings = {}
        self._initialize_model_mappings()

    def _initialize_model_mappings(self):
        """Initialize mappings between models and their providers"""
        # OpenAI models
        for model in SUPPORTED_OPENAI_LLM_MODELS:
            self._model_mappings[model] = "openai"

        # Azure OpenAI models
        for model in SUPPORTED_AZUREOPENAI_LLM_MODELS:
            self._model_mappings[model] = "azure"

        # Anthropic models
        for model in SUPPORTED_ANTHROPIC_LLM_MODELS:
            self._model_mappings[model] = "anthropic"

        # Groq models
        for model in SUPPORTED_GROQ_LLM_MODELS:
            self._model_mappings[model] = "groq"

        # MLX models
        for model in SUPPORTED_MLX_LLM_MODELS:
            self._model_mappings[model] = "mlx"

        # Llama.cpp models
        for model in SUPPORTED_LLAMACPP_LLM_MODELS:
            self._model_mappings[model] = "llama-cpp"

        # Ollama models
        for model in SUPPORTED_OLLAMA_LLM_MODELS:
            self._model_mappings[model] = "ollama"

    def get_provider(self, model: str) -> str:
        """Get the provider for a given model"""
        # Handle prefix-based models (e.g., "groq:", "ollama:")
        if ":" in model:
            prefix = model.split(":", 1)[0]
            if prefix in self._providers:
                return prefix

        provider = self._model_mappings.get(model)
        if not provider:
            raise ValueError(f"Model {model} not registered")
        return provider

    def get_provider_info(self, model: str) -> ProviderInfo:
        """Get provider information for a given model"""
        provider = self.get_provider(model)
        return self._providers[provider]

    def validate_provider_config(
        self, model: str, api_key: Optional[str], endpoint: Optional[str]
    ) -> bool:
        """Validate provider configuration for a given model"""
        provider_info = self.get_provider_info(model)

        if provider_info.requires_api_key and not api_key:
            logger.error(
                f"API key required for model {model} "
                f"(provider: {provider_info.provider})"
            )
            return False

        if provider_info.requires_endpoint and not endpoint:
            logger.error(
                f"Endpoint required for model {model} "
                f"(provider: {provider_info.provider})"
            )
            return False

        return True

    def register_model(
        self,
        model: str,
        provider: str,
        defaults: Optional[Dict[str, Any]] = None,
    ):
        """Register a new model with its provider"""
        if provider not in self._providers:
            raise ValueError(f"Provider {provider} not registered")

        self._model_mappings[model] = provider
        if defaults:
            self._providers[provider].defaults = defaults
        logger.info(f"Registered model {model} with provider {provider}")

    def is_streaming_supported(self, model: str) -> bool:
        """Check if streaming is supported for a given model"""
        provider_info = self.get_provider_info(model)
        return provider_info.supports_streaming


# Create singleton instance
model_provider_registry = ModelProviderRegistry()
