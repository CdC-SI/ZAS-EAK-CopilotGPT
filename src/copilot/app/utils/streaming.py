from abc import ABC, abstractmethod
from langfuse.decorators import observe
from dataclasses import dataclass
from typing import Optional

from config.llm_config import (
    SUPPORTED_OPENAI_LLM_MODELS,
    SUPPORTED_AZUREOPENAI_LLM_MODELS,
    SUPPORTED_ANTHROPIC_LLM_MODELS,
    SUPPORTED_GROQ_LLM_MODELS,
)

import logging

logger = logging.getLogger(__name__)


@dataclass
class Token:
    content: bytes
    is_source: bool = False
    is_status: bool = False
    metadata: Optional[dict] = None

    @classmethod
    def from_text(cls, text: str) -> "Token":
        text = text.replace("ß", "ss")
        return cls(content=text.encode("utf-8"))

    @classmethod
    def from_source(cls, url: str) -> "Token":
        content = f"\n\n<source><a href='{url}' target='_blank' class='source-link'>{url}</a></source>"
        return cls(
            content=content.encode("utf-8"),
            is_source=True,
            metadata={"url": url},
        )

    @classmethod
    def from_status(cls, status: str) -> "Token":
        return cls(content=status.encode("utf-8"), is_status=True)


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
                yield Token.from_text(event.choices[0].delta.content)
            elif event.choices[0].delta.content is None and content_received:
                yield Token.from_source(source_url)
                return


class AzureOpenAIStreaming(StreamingHandler):
    @observe()
    async def generate_stream(self, events, source_url):
        events = await events
        content_received = False
        async for event in events:
            if event.choices[0].delta.content is not None:
                content_received = True
                yield Token.from_text(event.choices[0].delta.content)
            elif event.choices[0].delta.content is None and content_received:
                yield Token.from_source(source_url)
                return
            elif not content_received:
                continue  # Skip initial None token


class AnthropicStreaming(StreamingHandler):
    @observe()
    async def generate_stream(self, events, source_url):
        events = await events
        async for event in events:
            if event.type == "content_block_delta":
                yield Token.from_text(event.delta.text)
            elif event.type == "content_block_stop":
                yield Token.from_source(source_url)
                return


class MLXStreaming(StreamingHandler):
    @observe()
    async def generate_stream(self, events, source_url):
        content_received = False
        async for event in events:
            if event.choices[0].delta.content is not None:
                content_received = True
                yield Token.from_text(event.choices[0].delta.content)
            elif event.choices[0].delta.content is None and content_received:
                yield Token.from_source(source_url)
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
                yield Token.from_text(event.choices[0].delta.content)
            elif event.choices[0].delta.content is None and content_received:
                yield Token.from_source(source_url)
                return


class OllamaStreaming(StreamingHandler):
    @observe()
    async def generate_stream(self, events, source_url):
        content_received = False
        async for event in events:
            if event.choices[0].delta.content is not None:
                content_received = True
                yield Token.from_text(event.choices[0].delta.content)
            elif event.choices[0].delta.content is None and content_received:
                yield Token.from_source(source_url)
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
        elif llm_model.startswith("ollama/"):
            return OllamaStreaming()
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")
