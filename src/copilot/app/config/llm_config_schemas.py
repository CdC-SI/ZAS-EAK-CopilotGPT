from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class LLMConfiguration(BaseModel):
    """Base configuration for any LLM model"""

    model: str = Field(..., description="Name of the LLM model")
    temperature: float = Field(
        0.0, description="Controls randomness in responses", ge=0.0, le=2.0
    )
    max_tokens: int = Field(
        2048, description="Maximum number of tokens in the response"
    )
    top_p: float = Field(
        0.95,
        description="Nucleus sampling parameter",
        ge=0.0,
        le=1.0,
    )
    top_k: int = Field(
        50,
        description="Top-k sampling parameter",
        ge=0,
    )
    context_window: int = Field(
        32000, description="Maximum context window size in tokens"
    )
    stream: bool = Field(True, description="Whether to stream the response")


class LLMClientConfiguration(BaseModel):
    """Configuration for LLM providers"""

    provider: str = Field(..., description="Name of the LLM provider")
    api_key: Optional[str] = Field(
        None, description="API key for the provider"
    )
    api_endpoint: Optional[str] = Field(
        None, description="Custom API endpoint URL"
    )
    api_version: Optional[str] = Field(None, description="API version to use")
    organization_id: Optional[str] = Field(
        None, description="Organization ID if required"
    )
    input_cost: float = Field(0.0, description="Cost per token for input text")
    output_cost: float = Field(
        0.0, description="Cost per token for output text"
    )


class LLMStreamingConfiguration(BaseModel):
    """Configuration for streaming responses"""

    chunk_size: int = Field(
        1024, description="Size of chunks when streaming responses"
    )
    max_retries: int = Field(
        3, description="Maximum number of retries on failure"
    )
    retry_interval: float = Field(
        0.5, description="Time to wait between retries in seconds"
    )
    timeout: float = Field(60.0, description="Streaming timeout in seconds")


class LLMModelParamsDefaults(BaseModel):
    """Default configurations for specific models"""

    _DEFAULT_LLM = "gpt-4o-mini"

    openai_defaults: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "gpt-4o": {
                "temperature": 0.0,
                "max_tokens": 16384,
                "top_p": 0.95,
                "context_window": 128000,
                "input_cost": 2.5,
                "output_cost": 10,
                "n_params": "NA",
            },
            "gpt-4o-mini": {
                "temperature": 0.0,
                "max_tokens": 16384,
                "top_p": 0.95,
                "context_window": 128000,
                "input_cost": 0.15,
                "output_cost": 0.6,
                "n_params": "NA",
            },
            "o1": {
                "temperature": 0.0,
                "max_tokens": 100000,
                "top_p": 0.95,
                "context_window": 200000,
                "input_cost": 15,
                "output_cost": 60,
                "n_params": "NA",
            },
            "o1-mini": {
                "temperature": 0.0,
                "max_tokens": 65536,
                "top_p": 0.95,
                "context_window": 200000,
                "input_cost": 1.1,
                "output_cost": 4.4,
                "n_params": "NA",
            },
            "o3-mini": {
                "temperature": 0.0,
                "max_tokens": 100000,
                "top_p": 0.95,
                "context_window": 200000,
                "input_cost": 1.1,
                "output_cost": 4.4,
                "n_params": "NA",
            },
        }
    )

    anthropic_defaults: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "claude-3-5-sonnet-20241022": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 200000,
                "input_cost": 3,
                "output_cost": 15,
                "n_params": "NA",
            },
            "claude-3-5-haiku-20241022": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 200000,
                "input_cost": 0.8,
                "output_cost": 4,
                "n_params": "NA",
            },
            "claude-3-opus-20240229 ": {
                "temperature": 0.0,
                "max_tokens": 4096,
                "top_p": 0.95,
                "context_window": 200000,
                "input_cost": 15,
                "output_cost": 75,
                "n_params": "NA",
            },
        }
    )

    gemini_defaults: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "gemini-2.0-flash-exp": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 1048576,
                "input_cost": 0,
                "output_cost": 0,
                "n_params": "NA",
            },
            "gemini-1.5-flash": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 1048576,
                "input_cost": 0.15,
                "output_cost": 0.6,
                "n_params": "NA",
            },
            "gemini-1.5-flash-8b": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 1048576,
                "input_cost": 0.075,
                "output_cost": 0.3,
                "n_params": "8b",
            },
            "gemini-1.5-pro": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 2097152,
                "input_cost": 2.5,
                "output_cost": 10,
                "n_params": "NA",
            },
        }
    )

    groq_defaults: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "groq:llama-3.3-70b-versatile": {
                "temperature": 0.0,
                "max_tokens": 32768,
                "top_p": 0.95,
                "context_window": 128000,
                "input_cost": 0,
                "output_cost": 0,
                "n_params": "70b",
            },
            "groq:llama-3.1-8b-instant": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 128000,
                "input_cost": 0,
                "output_cost": 0,
                "n_params": "8b",
            },
        }
    )

    ollama_defaults: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "ollama:llama3.2:1b": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 128000,
                "input_cost": 0,
                "output_cost": 0,
                "n_params": "1b",
            },
            "ollama:llama3.2:3b": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 128000,
                "input_cost": 0,
                "output_cost": 0,
                "n_params": "3b",
            },
            "ollama:deepseek-r1:8b": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 64000,
                "input_cost": 0,
                "output_cost": 0,
                "n_params": "8b",
            },
            "ollama:mistral-small": {
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "context_window": 32000,
                "input_cost": 0,
                "output_cost": 0,
                "n_params": "24b",
            },
        }
    )


def get_model_defaults(model: str) -> Dict[str, Any]:
    """
    Get default configuration for a specific model.
    Falls back to base defaults if model-specific ones aren't found.
    """
    model_defaults = LLMModelParamsDefaults()
    base_defaults = {
        "temperature": 0.0,
        "max_tokens": 2048,
        "top_p": 0.95,
        "context_window": 32000,
    }

    if model in model_defaults.openai_defaults:
        return model_defaults.openai_defaults[model]
    elif model in model_defaults.anthropic_defaults:
        return model_defaults.anthropic_defaults[model]
    elif model in model_defaults.gemini_defaults:
        return model_defaults.gemini_defaults[model]
    elif model in model_defaults.groq_defaults:
        return model_defaults.groq_defaults[model]
    elif model in model_defaults.ollama_defaults:
        return model_defaults.ollama_defaults[model]

    return base_defaults


class LLMTaskConfiguration(BaseModel):
    """LLM Configuration for a specific task"""

    task: str = Field(..., description="Name of the task")
    llm_config: LLMConfiguration = Field(
        ..., description="Configuration for the LLM model"
    )
