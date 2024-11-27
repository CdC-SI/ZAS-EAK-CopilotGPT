"""
Configuration for Large Language Models (LLMs) and Embedding Models.
"""

# LLMs
# OpenAI
SUPPORTED_OPENAI_LLM_MODELS = ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview", "gpt-4o", "gpt-4o-mini", "gpt-4o-2024-05-13"]
DEFAULT_OPENAI_LLM_MODEL = "gpt-4o-2024-05-13"

# AzureOpenAI
SUPPORTED_AZUREOPENAI_LLM_MODELS = ["azure-gpt-4-32k"]
DEFAULT_AZUREOPENAI_LLM_MODEL = "azure-gpt-4-32k"

# Anthropic
SUPPORTED_ANTHROPIC_LLM_MODELS = ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
DEFAULT_ANTHROPIC_LLM_MODEL = "claude-3-5-sonnet-20240620"

# Groq
SUPPORTED_GROQ_LLM_MODELS = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma-7b-it", "gemma2-9b-it"]
DEFAULT_GROQ_LLM_MODEL = "llama-3.1-8b-instant"

# Open Source
SUPPORTED_MLX_LLM_MODELS = ["mlx-community/Nous-Hermes-2-Mistral-7B-DPO-4bit-MLX"]
DEFAULT_MLX_LLM_MODEL = "mlx-community/Nous-Hermes-2-Mistral-7B-DPO-4bit-MLX"

# Huggingface
SUPPORTED_HUGGINGFACE_LLM_MODELS = []
DEFAULT_HUGGINGFACE_LLM_MODEL = ""

# mlx
SUPPORTED_MLX_LLM_MODELS = ["mlx-community/Nous-Hermes-2-Mistral-7B-DPO-4bit-MLX"]
DEFAULT_MLX_LLM_MODEL = "mlx-community/Nous-Hermes-2-Mistral-7B-DPO-4bit-MLX"

# Llama-cpp
SUPPORTED_LLAMACPP_LLM_MODELS = ["Qwen/Qwen1.5-0.5B-Chat-GGUF"]
DEFAULT_LLAMACPP_LLM_MODEL = "Qwen/Qwen1.5-0.5B-Chat-GGUF"

# Embedding models
# OpenAI
SUPPORTED_OPENAI_EMBEDDING_MODELS = ["text-embedding-ada-002"]
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"

# OpenAI
SUPPORTED_AZUREOPENAI_EMBEDDING_MODELS = ["azure-text-embedding-ada-002"]
DEFAULT_AZUREOPENAI_EMBEDDING_MODEL = "azure-text-embedding-ada-002"

# Sentence-transformers
SUPPORTED_ST_EMBEDDING_MODELS = []
DEFAULT_ST_EMBEDDING_MODEL = ""
