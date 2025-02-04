from typing import Dict, Optional, Any
from functools import lru_cache
import yaml
from pathlib import Path

from .llm_config_schemas import (
    LLMConfiguration,
    LLMClientConfiguration,
    LLMStreamingConfiguration,
    LLMModelParamsDefaults,
    LLMTaskConfiguration,
    get_model_defaults,
)
from .tasks_config import Tasks
from utils.logging import get_logger
from .configuration_validator import config_validator
from .model_provider_registry import model_provider_registry

logger = get_logger(__name__)


class LLMConfigManager:
    """Manages configurations for LLM models"""

    def __init__(
        self,
        config_file: Optional[str] = None,
    ):
        self._llm_configs: Dict[str, LLMConfiguration] = {}
        self._task_configs: Dict[str, LLMTaskConfiguration] = {}
        self._llm_client_configs: Dict[str, LLMClientConfiguration] = {}
        self._llm_streaming_config = LLMStreamingConfiguration()
        self._config_cache = {}

        self._load_llm_defaults()
        if config_file:
            self._load_yaml_config(config_file)
        else:
            self._load_default_config()

    def _load_llm_defaults(self):
        """Load default configurations from schema definitions"""
        model_defaults = LLMModelParamsDefaults()

        # Load OpenAI defaults
        for model, defaults in model_defaults.openai_defaults.items():
            self._llm_configs[model] = LLMConfiguration(
                model=model, **defaults
            )

        # Load Anthropic defaults
        for model, defaults in model_defaults.anthropic_defaults.items():
            self._llm_configs[model] = LLMConfiguration(
                model=model, **defaults
            )

        # Load Gemini defaults
        for model, defaults in model_defaults.gemini_defaults.items():
            self._llm_configs[model] = LLMConfiguration(
                model=model, **defaults
            )

        # Load Groq defaults
        for model, defaults in model_defaults.groq_defaults.items():
            self._llm_configs[model] = LLMConfiguration(
                model=model, **defaults
            )

        # Load Ollama defaults
        for model, defaults in model_defaults.ollama_defaults.items():
            self._llm_configs[model] = LLMConfiguration(
                model=model, **defaults
            )

    def _load_yaml_config(self, config_file: str):
        """Load configurations from YAML file"""

        model_defaults = LLMModelParamsDefaults()

        try:
            config_path = Path(config_file)
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_file}")
                return

            with open(config_path, "r") as f:
                yaml_config = yaml.safe_load(f)

            if not yaml_config or "llm" not in yaml_config:
                logger.warning("No LLM configuration found in YAML")
                return

            current_llm_config = yaml_config["llm"]

            # Update task configs
            for task, config in current_llm_config.items():

                model_name = config.get("model", model_defaults._DEFAULT_LLM)

                # Get default params for model
                model_default_params = get_model_defaults(model_name)

                # Merge defaults with provided config
                merged_config = {
                    **model_default_params,  # Base model defaults
                    **{
                        k: v for k, v in config.items() if k != "model"
                    },  # YAML config without model
                }

                # Create final config
                self._task_configs[task] = LLMTaskConfiguration(
                    task=task,
                    llm_config=LLMConfiguration(
                        model=model_name, **merged_config
                    ),
                )

            task_values = {task.value for task in Tasks}

            configured_tasks = set(current_llm_config.keys())

            # Find missing tasks
            missing_tasks = task_values - configured_tasks
            if missing_tasks:
                for task in missing_tasks:
                    self._task_configs[task] = LLMTaskConfiguration(
                        task=task,
                        llm_config=self._llm_configs[
                            model_defaults._DEFAULT_LLM
                        ],
                    )

            # Load client configurations
            if "providers" in current_llm_config:
                for provider, config in current_llm_config[
                    "providers"
                ].items():
                    self._llm_client_configs[provider] = (
                        LLMClientConfiguration(
                            provider=provider,
                            **config,
                        )
                    )

            # Load streaming configuration
            if "streaming" in current_llm_config:
                self._streaming_config = LLMStreamingConfiguration(
                    **current_llm_config["streaming"]
                )

        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise

    def get_config(self, model: str) -> LLMConfiguration:
        """Get configuration for a specific model"""
        if model not in self._llm_configs:
            # Create new config with defaults
            defaults = get_model_defaults(model)
            self._llm_configs[model] = LLMConfiguration(
                model=model, **defaults
            )
        return self._llm_configs[model]

    def get_client_config(
        self, provider: str
    ) -> Optional[LLMClientConfiguration]:
        """Get configuration for a specific provider"""
        return self._llm_client_configs.get(provider)

    def get_streaming_config(self) -> LLMStreamingConfiguration:
        """Get streaming configuration"""
        return self._llm_streaming_config

    @lru_cache(maxsize=128)
    def _get_cached_config(
        self, model: str, config_hash: str
    ) -> Dict[str, Any]:
        """Cache frequently used configurations"""
        return self._config_cache.get((model, config_hash))

    def _hash_config(self, config: Dict[str, Any]) -> str:
        """Create a hash of the configuration for caching"""
        return str(hash(frozenset(config.items())))

    def get_merged_config(
        self, model: str, runtime_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get merged configuration combining model, provider, and runtime configs.

        Parameters
        ----------
        model : str
            The model identifier
        runtime_overrides : Optional[Dict[str, Any]]
            Runtime configuration overrides

        Returns
        -------
        Dict[str, Any]
            Merged and validated configuration
        """
        # Get provider information
        provider = model_provider_registry.get_provider(model)

        # Try to get from cache if no runtime overrides
        if not runtime_overrides:
            cached = self._get_cached_config(model, "base")
            if cached:
                return cached

        # Get base configurations
        model_config = self.get_config(model).dict()
        provider_config = self.get_provider_config(provider)
        if provider_config:
            provider_config = provider_config.dict()

        # Merge configurations with priority
        merged_config = {
            **(provider_config or {}),  # Provider defaults (lowest priority)
            **model_config,  # Model-specific settings
            **(
                runtime_overrides or {}
            ),  # Runtime overrides (highest priority)
        }

        # Validate merged configuration
        validation_result = config_validator.validate_merged_config(
            merged_config, model, provider
        )

        if not validation_result.is_valid:
            raise ValueError(
                f"Invalid configuration for {model}: {validation_result.message}\n"
                f"Details: {validation_result.details}"
            )

        # Cache the base configuration (without runtime overrides)
        if not runtime_overrides:
            base_config = {**(provider_config or {}), **model_config}
            self._config_cache[(model, "base")] = base_config

        return merged_config

    def update_config(self, model: str, **kwargs):
        """Update configuration for a specific model"""
        if model not in self._llm_configs:
            raise ValueError(f"No configuration found for model: {model}")

        current_config = self._llm_configs[model].dict()
        updated_config = {**current_config, **kwargs}

        # Create new config object for validation
        new_config = LLMConfiguration(**updated_config)

        # Get provider and validate
        provider = model_provider_registry.get_provider(model)
        validation_result = config_validator.validate_llm_config(
            new_config, provider
        )

        if not validation_result.is_valid:
            raise ValueError(
                f"Invalid configuration: {validation_result.message}\n"
                f"Details: {validation_result.details}"
            )

        self._llm_configs[model] = new_config
        logger.info(f"Updated config for model {model} with {kwargs}")

    def update_provider_config(self, provider: str, **kwargs):
        """Update configuration for a specific provider"""
        if provider not in self._llm_client_configs:
            self._llm_client_configs[provider] = LLMClientConfiguration(
                provider=provider
            )

        current_config = self._llm_client_configs[provider].dict()
        updated_config = {**current_config, **kwargs}

        # Create new config object for validation
        new_config = LLMClientConfiguration(**updated_config)

        # Validate provider config
        validation_result = config_validator.validate_provider_config(
            new_config, provider
        )

        if not validation_result.is_valid:
            raise ValueError(
                f"Invalid provider configuration: {validation_result.message}\n"
                f"Details: {validation_result.details}"
            )

        self._llm_provider_configs[provider] = new_config
        logger.info(f"Updated provider config for {provider}")

    def update_streaming_config(self, **kwargs):
        """Update streaming configuration"""
        current_config = self._llm_streaming_config.dict()
        updated_config = {**current_config, **kwargs}

        # Create new config object for validation
        new_config = LLMStreamingConfiguration(**updated_config)

        # Validate streaming config
        validation_result = config_validator.validate_streaming_config(
            new_config
        )

        if not validation_result.is_valid:
            raise ValueError(
                f"Invalid streaming configuration: {validation_result.message}\n"
                f"Details: {validation_result.details}"
            )

        self._llm_streaming_config = new_config
        logger.info("Updated streaming config")


# Create singleton instance
llm_config_manager = LLMConfigManager(
    config_file="config/config.yaml",
)
