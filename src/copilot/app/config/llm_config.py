"""
Configuration for Large Language Models (LLMs) and Embedding Models.

Constants
---------
SUPPORTED_OPENAI_LLM_MODELS : list
    A list of supported OpenAI LLM model names.
DEFAULT_OPENAI_LLM_MODEL : str
    The default OpenAI LLM model to be used if no model is specified.
SUPPORTED_HUGGINGFACE_LLM_MODELS : list
    A list of supported Hugging Face LLM model names.
DEFAULT_HUGGINGFACE_LLM_MODEL : str
    The default Hugging Face LLM model to be used if no model is specified.
SUPPORTED_MLX_LLM_MODELS : list
    A list of supported mlx LLM model names.
DEFAULT_MLX_LLM_MODEL : str
    The default mlx LLM model to be used if no model is specified.
SUPPORTED_LLAMACPP_LLM_MODELS : list
    A list of supported llama-cpp LLM model names.
DEFAULT_LLAMACPP_LLM_MODEL : str
    The default llama-cpp LLM model to be used if no model is specified.
SUPPORTED_OPENAI_EMBEDDING_MODELS : list
    A list of supported OpenAI embedding model names.
DEFAULT_OPENAI_EMBEDDING_MODEL : str
    The default OpenAI embedding model to be used if no model is specified.
SUPPORTED_ST_EMBEDDING_MODELS : list
    A list of supported Sentence Transformer embedding model names.
DEFAULT_ST_EMBEDDING_MODEL : str
    The default Sentence Transformer embedding model to be used if no model is specified.
"""

# LLMs
# OpenAI
SUPPORTED_OPENAI_LLM_MODELS = ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview", "gpt-4o", "gpt-4o-mini"]
DEFAULT_OPENAI_LLM_MODEL = "gpt-4o-mini"

# Groq
SUPPORTED_GROQ_LLM_MODELS = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma-7b-it", "gemma2-9b-it"]
DEFAULT_GROQ_LLM_MODEL = "llama-3.1-8b-instant"

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

# Sentence-transformers
SUPPORTED_ST_EMBEDDING_MODELS = []
DEFAULT_ST_EMBEDDING_MODEL = ""