import os
from dotenv import load_dotenv
import itertools
from enum import Enum
from langfuse import Langfuse
import tiktoken

from prompts.rag import RAG_SYSTEM_PROMPT_FR

load_dotenv()

LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY", None)
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY", None)
# LANGFUSE_HOST = "http://localhost:3000"
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST", None)

langfuse = Langfuse(
    secret_key=LANGFUSE_SECRET_KEY,
    public_key=LANGFUSE_PUBLIC_KEY,
    host=LANGFUSE_HOST,
)


class ModelProvider(Enum):
    OPENAI = "openai"
    AZUREOPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    GEMINI = "gemini"
    MISTRAL = "mistral"


class ModelPricingService:

    _PRICING = {
        ModelProvider.OPENAI: {
            "IN": 0.15 / 1_000_0000,
            "IN_CACHED": 0.075 / 1_000_0000,
            "OUT": 0.6 / 1_000_0000,
        },
        ModelProvider.AZUREOPENAI: {
            "IN": 0.15 / 1_000_0000,
            "IN_CACHED": 0.075 / 1_000_0000,
            "OUT": 0.6 / 1_000_0000,
        },
        ModelProvider.ANTHROPIC: {
            "IN": 0.15 / 1_000_0000,
            "IN_CACHED": 0.075 / 1_000_0000,
            "OUT": 0.6 / 1_000_0000,
        },
        ModelProvider.GROQ: {
            "IN": 0.15 / 1_000_0000,
            "IN_CACHED": 0.075 / 1_000_0000,
            "OUT": 0.6 / 1_000_0000,
        },
        ModelProvider.GEMINI: {
            "IN": 0.15 / 1_000_0000,
            "IN_CACHED": 0.075 / 1_000_0000,
            "OUT": 0.6 / 1_000_0000,
        },
        ModelProvider.MISTRAL: {
            "IN": 0.15 / 1_000_0000,
            "IN_CACHED": 0.075 / 1_000_0000,
            "OUT": 0.6 / 1_000_0000,
        },
    }

    @classmethod
    def get_input_cost(
        cls, n_tokens: int, model_provider: ModelProvider, **kwargs
    ) -> float:
        input_cost = cls._PRICING[model_provider].get("IN") * n_tokens
        return input_cost

    @classmethod
    def get_input_cached_cost(
        cls, n_tokens: int, model_provider: ModelProvider, **kwargs
    ) -> float:
        input_cost = cls._PRICING[model_provider].get("IN_CACHED") * n_tokens
        return input_cost

    @classmethod
    def get_output_cost(
        cls, n_tokens: int, model_provider: ModelProvider, **kwargs
    ) -> float:
        input_cost = cls._PRICING[model_provider].get("OUT") * n_tokens
        return input_cost

    @classmethod
    def get_total_cost(
        cls,
        n_input_tokens: int,
        n_input_cached_tokens: int,
        n_output_tokens: int,
        model_provider: ModelProvider,
        **kwargs,
    ) -> float:
        n_input_tokens_cost = cls.get_input_cost(
            n_input_tokens, model_provider
        )
        n_input_cached_tokens_cost = cls.get_input_cached_cost(
            n_input_cached_tokens, model_provider
        )
        n_output_tokens_cost = cls.get_output_cost(
            n_output_tokens, model_provider
        )

        cost = {
            "n_input_tokens_cost": n_input_tokens_cost,
            "n_input_cached_tokens_cost": n_input_cached_tokens_cost,
            "n_output_tokens_cost": n_output_tokens_cost,
            "total_cost": n_input_tokens_cost
            + n_input_cached_tokens_cost
            + n_output_tokens_cost,
        }
        return cost


def longest_common_prefix(str1, str2):
    # Use itertools to find the longest common prefix
    return "".join(
        x[0]
        for x in itertools.takewhile(lambda x: x[0] == x[1], zip(str1, str2))
    )


def get_input_tokens(messages):
    for message in messages.data[0].output:
        if message["role"] == "system":

            # find longest commong prefix
            prefix = longest_common_prefix(
                message["content"], RAG_SYSTEM_PROMPT_FR
            )

            # get input cached tokens
            n_input_cached_tokens = len(tokenizer.encode(prefix))

            # get input tokens
            input_tokens = message["content"].replace(prefix, "")
            n_input_tokens = len(tokenizer.encode(input_tokens))

        elif message["role"] == "user":
            # get query input tokens
            n_query_input_tokens = len(tokenizer.encode(message["content"]))

    n_input_tokens = {
        "n_input_cached_tokens": n_input_cached_tokens,
        "n_input_tokens": n_input_tokens + n_query_input_tokens,
    }

    return n_input_tokens


def get_output_tokens(output_stream):
    output_tokens = [
        tok for tok in output_stream.data[0].output if tok["content"]
    ]
    n_output_tokens = len(output_tokens)

    return {"n_output_tokens": n_output_tokens}


if __name__ == "__main__":

    # need to set llm_model --> tokenizer, ModelPricingService
    # need to compute embedding cost
    # need to fetch messages/output stream by user_uuid/conversation_uuid

    tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")

    messages = langfuse.fetch_observations(
        name="MessageBuilder_build_chat_prompt"
    )

    input_tokens = get_input_tokens(messages)

    output_stream = langfuse.fetch_observations(name="openai_output_stream")

    output_tokens = get_output_tokens(output_stream)

    ModelPricingService.get_total_cost(
        n_input_tokens=input_tokens["n_input_tokens"],
        n_input_cached_tokens=input_tokens["n_input_cached_tokens"],
        n_output_tokens=output_tokens["n_output_tokens"],
        model_provider=ModelProvider.OPENAI,
    )
