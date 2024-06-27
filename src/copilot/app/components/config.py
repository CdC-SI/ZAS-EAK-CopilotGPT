"""
Configuration for Large Language Models (LLMs) and Embedding Models.

Constants
---------
SUPPORTED_OPENAI_LLM_MODELS : list
    A list of supported OpenAI LLM model names.
DEFAULT_OPENAI_MODEL : str
    The default OpenAI LLM model to be used if no model is specified.
SUPPORTED_HUGGINGFACE_LLM_MODELS : list
    A list of supported Hugging Face LLM model names.
DEFAULT_HUGGINGFACE_MODEL : str
    The default Hugging Face LLM model to be used if no model is specified.
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
SUPPORTED_OPENAI_LLM_MODELS = ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview", "gpt-4o"]

DEFAULT_OPENAI_LLM_MODEL = "gpt-3.5-turbo-0125"

SUPPORTED_HUGGINGFACE_LLM_MODELS = []

DEFAULT_HUGGINGFACE_MODEL = "test"

# Embedding models
SUPPORTED_OPENAI_EMBEDDING_MODELS = ["text-embedding-ada-002"]

DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"

SUPPORTED_ST_EMBEDDING_MODELS = []

DEFAULT_ST_EMBEDDING_MODEL = "sentence-transformers"
