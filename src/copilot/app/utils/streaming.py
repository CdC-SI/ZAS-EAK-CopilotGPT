from abc import ABC, abstractmethod
from langfuse.decorators import observe

from config.llm_config import (
    SUPPORTED_OPENAI_LLM_MODELS,
    SUPPORTED_AZUREOPENAI_LLM_MODELS,
    SUPPORTED_ANTHROPIC_LLM_MODELS,
    SUPPORTED_GROQ_LLM_MODELS,
)


class StreamingHandler(ABC):
    @abstractmethod
    async def generate_stream(self, stream, source_url):
        pass


class OpenAIStreaming(StreamingHandler):
    @observe()
    async def generate_stream(self, events, source_url):
        events = await events
        content_received = False
        async for event in events:
            if event.choices[0].delta.content is not None:
                content_received = True
                yield event.choices[0].delta.content.encode("utf-8")
            elif event.choices[0].delta.content is None and content_received:
                yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode(
                    "utf-8"
                )
                return


class AzureOpenAIStreaming(StreamingHandler):
    @observe()
    async def generate_stream(self, events, source_url):
        events = await events
        content_received = False
        async for event in events:
            if event.choices[0].delta.content is not None:
                content_received = True
                yield event.choices[0].delta.content.encode("utf-8")
            elif event.choices[0].delta.content is None and content_received:
                yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode(
                    "utf-8"
                )
                return
            elif not content_received:
                continue  # Skip initial None token


class AnthropicStreaming(StreamingHandler):
    @observe()
    async def generate_stream(self, events, source_url):
        events = await events
        async for event in events:
            if event.type == "content_block_delta":
                yield event.delta.text
            elif event.type == "content_block_stop":
                yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode(
                    "utf-8"
                )
                return


class MLXStreaming(StreamingHandler):
    @observe()
    async def generate_stream(self, events, source_url):
        content_received = False
        async for event in events:
            if event.choices[0].delta.content is not None:
                content_received = True
                yield event.choices[0].delta.content.encode("utf-8")
            elif event.choices[0].delta.content is None and content_received:
                yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode(
                    "utf-8"
                )
                return
            elif not content_received:
                continue  # Skip initial None token


class LlamaCppStreaming(StreamingHandler):
    @observe()
    async def generate_stream(self, events, source_url):
        content_received = False
        async for event in events:
            if event.choices[0].delta.content is not None:
                content_received = True
                yield event.choices[0].delta.content.encode("utf-8")
            elif event.choices[0].delta.content is None and content_received:
                yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode(
                    "utf-8"
                )
                return


class StreamingHandlerFactory:
    @staticmethod
    def get_streaming_strategy(llm_model):
        if (
            llm_model in SUPPORTED_OPENAI_LLM_MODELS
            or llm_model in SUPPORTED_GROQ_LLM_MODELS
        ):
            return OpenAIStreaming()
        elif llm_model in SUPPORTED_AZUREOPENAI_LLM_MODELS:
            return AzureOpenAIStreaming()
        elif llm_model in SUPPORTED_ANTHROPIC_LLM_MODELS:
            return AnthropicStreaming()
        elif llm_model.startswith("mlx-community/"):
            return MLXStreaming()
        elif llm_model.startswith("llama-cpp/"):
            return LlamaCppStreaming()
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")
