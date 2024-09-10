from .config import Client, Base as Model, Embedding as EmbeddingModel, LLM as LLMModel
from enum import Enum
import re

from utils.enum import GetItemUpper


class ModelEnum(GetItemUpper):
    def __getitem__(self, model: str):
        model = re.sub(r'[^a-zA-Z0-9]', '_', model)
        return super().__getitem__(model)


class Embedding(Enum, metaclass=ModelEnum):
    TEXT_EMBEDDING_ADA_002 = EmbeddingModel("text-embedding-ada-002", Client.OPENAI, 1536)
    TEXT_EMBEDDING_3_SMALL = EmbeddingModel("text-embedding-3-small", Client.OPENAI, 1536)
    TEXT_EMBEDDING_3_LARGE = EmbeddingModel("text-embedding-3-large", Client.OPENAI, 3072)

    # EMBED_ENGLISH_V3_0 = EmbeddingModel("embed-english-v3.0", Client.cohere, 1024)
    # EMBED_ENGLISH_LIGHT_V3_0 = EmbeddingModel("embed-english-light-v3.0", Client.cohere, 384)
    # EMBED_ENGLISH_V2_0 = EmbeddingModel("embed-english-v2.0", Client.cohere, 4096)
    # EMBED_ENGLISH_LIGHT_V2_0 = EmbeddingModel("embed-english-light-v2.0", Client.cohere, 1024)

    # EMBED_MULTILINGUAL_V3_0 = EmbeddingModel("embed-multilingual-v3.0", Client.cohere, 1024)
    # EMBED_MULTILINGUAL_LIGHT_V3_0 = EmbeddingModel("embed-multilingual-light-v3.0", Client.cohere, 384)
    # EMBED_MULTILINGUAL_V2_0 = EmbeddingModel("embed-multilingual-v2.0", Client.cohere, 768)


class Reranker(Enum, metaclass=ModelEnum):
    RERANK_MULTILINGUAL_V3_0 = Model("rerank-multilingual-v3.0", Client.COHERE)
    RERANK_MULTILINGUAL_V2_0 = Model("rerank-multilingual-v2.0", Client.COHERE)
    RERANK_ENGLISH_V3_0 = Model("rerank-english-v3.0", Client.COHERE)
    RERANK_ENGLISH_V2_0 = Model("rerank-english-v2.0", Client.COHERE)


class LLM(Enum, metaclass=ModelEnum):
    GPT_4O = LLMModel("gpt-4o", Client.OPENAI, 128000, 4096)
    GPT_4O_2024_05_13 = LLMModel("gpt-4o-2024-05-13", Client.OPENAI, 128000, 4096)
    GPT_4O_2024_08_06 = LLMModel("gpt-4o-2024-08-06", Client.OPENAI, 128000, 16384)
    GPT_4O_LATEST = LLMModel("gpt-4o-latest", Client.OPENAI, 128000, 16384)

    GPT_4O_MINI = LLMModel("gpt-4o-mini", Client.OPENAI, 128000, 16384)
    GPT_4O_MINI_2024_07_18 = LLMModel("gpt-4o-mini-2024-07-18", Client.OPENAI, 128000, 16384)

    GPT_4_TURBO = LLMModel("gpt-4-turbo", Client.OPENAI, 128000, 4096)
    GPT_4_TURB0_2024_04_09 = LLMModel("gpt-4-turbo-2024-04-09", Client.OPENAI, 128000, 4096)
    GPT_4_TURBO_PREVIEW = LLMModel("gpt-4-turbo-preview", Client.OPENAI, 128000, 4096)
    GPT_4_0125_PREVIEW = LLMModel("gpt-4-0125-preview", Client.OPENAI, 128000, 4096)
    GPT_4_1106_PREVIEW = LLMModel("gpt-4-1106-preview", Client.OPENAI, 128000, 4096)
    GPT_4 = LLMModel("gpt-4", Client.OPENAI, 8192, 8192)
    GPT_4_0613 = LLMModel("gpt-4-0613", Client.OPENAI, 8192, 8192)
    GPT_4_0314 = LLMModel("gpt-4-0314", Client.OPENAI, 8192, 8192)

    # GEMMA2_9B_IT = LLMModel("gemma2-9b-it", Client.groq, 8192, 8192)
    # GEMMA_7B_IT = LLMModel("gemma-7b-it", Client.groq, 8192, 8192)

    # LLAMA3_GROQ_70B_8192_TOOL_USE_PREVIEW = LLMModel("llama3-groq-70b-8192-tool-use-preview", Client.groq, 8192, 8192)
    # LLAMA3_GROQ_8B_8192_TOOL_USE_PREVIEW = LLMModel("llama3-groq-8b-8192-tool-use-preview", Client.groq, 8192, 8192)
    # LLAMA_3_1_70B_VERSATILE = LLMModel("llama-3.1-70b-versatile", Client.groq, 131072, 8192)
    # LLAMA_3_1_8B_INSTANT = LLMModel("llama-3.1-8b-instant", Client.groq, 131072, 8192)
    # LLAMA_GUARD_3_8B = LLMModel("llama-guard-3-8b", Client.groq, 8192, 8192)
    # LLAMA3_70B_8192 = LLMModel("llama3-70b-8192", Client.groq, 8192, 8192)
    # LLAMA3_8B_8192 = LLMModel("llama3-8b-8192", Client.groq, 8192, 8192)

    # MIXTRAL_8X7B_32768 = LLMModel("mixtral-8x7b-32768", Client.groq, 32768, 32768)

    # COMMAND_R_PLUS = LLMModel("command-r-plus", Client.cohere, 128000, 4000)
    # COMMAND_R = LLMModel("command-r", Client.cohere, 128000, 4000)

    # COMMAND = LLMModel("command", Client.cohere, 4000, 4000)
    # COMMAND_NIGHTLY = LLMModel("command-nightly", Client.cohere, 128000, 128000)
    # COMMAND_LIGHT = LLMModel("command-light", Client.cohere, 4000, 4000)
    # COMMAND_LIGHT_NIGHTLY = LLMModel("command-light-nightly", Client.cohere, 4000, 4000)

    # QWEN1_5_0_5B_CHAT-GGUF = LLMModel("Qwen/Qwen1.5-0.5B-Chat-GGUF", Client.local, 8192, 8192)
    # NOUS_HERMES_2_MISTRAL_7B_DPO_4BIT_MLX = LLMModel("mlx-community/Nous-Hermes-2-Mistral-7B-DPO-4bit-MLX", Client.local, 8192, 8192)
