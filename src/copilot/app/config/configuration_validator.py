from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from config.llm_config_schemas import (
    LLMConfiguration,
    LLMClientConfiguration,
    LLMStreamingConfiguration,
)
from config.model_provider_registry import model_provider_registry
from utils.logging import get_logger

logger = get_logger(__name__)


class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Represents the result of a configuration validation"""

    is_valid: bool
    message: str
    level: ValidationLevel
    details: Optional[Dict[str, Any]] = None


class ConfigurationValidator:
    """Validates LLM configurations"""

    # Provider-specific constraints
    PROVIDER_CONSTRAINTS = {
        "openai": {
            "temperature": {"min": 0.0, "max": 2.0},
            "max_tokens": {"min": 1, "max": 4096},
            "top_p": {"min": 0.0, "max": 1.0},
            "context_window": {"max": 128000},
        },
        "anthropic": {
            "temperature": {"min": 0.0, "max": 1.0},
            "max_tokens": {"min": 1, "max": 4096},
            "top_p": {"min": 0.0, "max": 1.0},
            "context_window": {"max": 200000},
        },
        "groq": {
            "temperature": {"min": 0.0, "max": 1.0},
            "max_tokens": {"min": 1, "max": 4096},
            "top_p": {"min": 0.0, "max": 1.0},
            "context_window": {"max": 32768},
        },
    }

    @classmethod
    def validate_llm_config(
        cls, config: LLMConfiguration, provider: str
    ) -> ValidationResult:
        """
        Validate LLM configuration against provider constraints

        Parameters
        ----------
        config : LLMConfiguration
            Configuration to validate
        provider : str
            Provider name

        Returns
        -------
        ValidationResult
            Validation result with status and details
        """
        try:
            constraints = cls.PROVIDER_CONSTRAINTS.get(provider, {})
            if not constraints:
                return ValidationResult(
                    is_valid=True,
                    message=f"No specific constraints for provider {provider}",
                    level=ValidationLevel.INFO,
                )

            violations = []

            # Check temperature
            if "temperature" in constraints:
                if not (
                    constraints["temperature"]["min"]
                    <= config.temperature
                    <= constraints["temperature"]["max"]
                ):
                    violations.append(
                        f"Temperature {config.temperature} outside "
                        f"allowed range {constraints['temperature']}"
                    )

            # Check max_tokens
            if "max_tokens" in constraints:
                if not (
                    constraints["max_tokens"]["min"]
                    <= config.max_tokens
                    <= constraints["max_tokens"]["max"]
                ):
                    violations.append(
                        f"Max tokens {config.max_tokens} outside "
                        f"allowed range {constraints['max_tokens']}"
                    )

            # Check top_p
            if "top_p" in constraints:
                if not (
                    constraints["top_p"]["min"]
                    <= config.top_p
                    <= constraints["top_p"]["max"]
                ):
                    violations.append(
                        f"Top-p {config.top_p} outside "
                        f"allowed range {constraints['top_p']}"
                    )

            # Check context window
            if (
                "context_window" in constraints
                and config.context_window
                > constraints["context_window"]["max"]
            ):
                violations.append(
                    f"Context window {config.context_window} exceeds "
                    f"maximum {constraints['context_window']['max']}"
                )

            if violations:
                return ValidationResult(
                    is_valid=False,
                    message="Configuration validation failed",
                    level=ValidationLevel.ERROR,
                    details={"violations": violations},
                )

            return ValidationResult(
                is_valid=True,
                message="Configuration validation successful",
                level=ValidationLevel.INFO,
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Validation error: {str(e)}",
                level=ValidationLevel.ERROR,
                details={"error": str(e)},
            )

    @classmethod
    def validate_provider_config(
        cls, config: LLMClientConfiguration, provider: str
    ) -> ValidationResult:
        """Validate provider configuration"""
        try:
            provider_info = model_provider_registry._providers.get(provider)
            if not provider_info:
                return ValidationResult(
                    is_valid=False,
                    message=f"Unknown provider: {provider}",
                    level=ValidationLevel.ERROR,
                )

            violations = []

            # Check API key requirement
            if provider_info.requires_api_key and not config.api_key:
                violations.append(f"API key required for provider {provider}")

            # Check endpoint requirement
            if provider_info.requires_endpoint and not config.api_endpoint:
                violations.append(
                    f"API endpoint required for provider {provider}"
                )

            # Validate timeout
            if config.timeout <= 0:
                violations.append(f"Invalid timeout value: {config.timeout}")

            if violations:
                return ValidationResult(
                    is_valid=False,
                    message="Provider configuration validation failed",
                    level=ValidationLevel.ERROR,
                    details={"violations": violations},
                )

            return ValidationResult(
                is_valid=True,
                message="Provider configuration validation successful",
                level=ValidationLevel.INFO,
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Validation error: {str(e)}",
                level=ValidationLevel.ERROR,
                details={"error": str(e)},
            )

    @classmethod
    def validate_streaming_config(
        cls, config: LLMStreamingConfiguration
    ) -> ValidationResult:
        """Validate streaming configuration"""
        try:
            violations = []

            # Validate chunk size
            if config.chunk_size <= 0:
                violations.append(f"Invalid chunk size: {config.chunk_size}")

            # Validate max retries
            if config.max_retries < 0:
                violations.append(f"Invalid max retries: {config.max_retries}")

            # Validate retry interval
            if config.retry_interval <= 0:
                violations.append(
                    f"Invalid retry interval: {config.retry_interval}"
                )

            # Validate timeout
            if config.timeout <= 0:
                violations.append(f"Invalid timeout: {config.timeout}")

            if violations:
                return ValidationResult(
                    is_valid=False,
                    message="Streaming configuration validation failed",
                    level=ValidationLevel.ERROR,
                    details={"violations": violations},
                )

            return ValidationResult(
                is_valid=True,
                message="Streaming configuration validation successful",
                level=ValidationLevel.INFO,
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Validation error: {str(e)}",
                level=ValidationLevel.ERROR,
                details={"error": str(e)},
            )


# Create singleton instance
config_validator = ConfigurationValidator()
