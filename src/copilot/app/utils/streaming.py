from abc import ABC, abstractmethod
from langfuse.decorators import observe
from dataclasses import dataclass
from typing import Optional, AsyncGenerator, Dict
import asyncio

from config.llm_config_schemas import LLMStreamingConfiguration
from config.model_provider_registry import model_provider_registry
from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Token:
    content: bytes
    is_text: bool = False
    is_source: bool = False
    is_status: bool = False
    metadata: Optional[dict] = None

    @classmethod
    def from_text(cls, text: str) -> "Token":
        text = text.replace("ß", "ss")
        return cls(content=text.encode("utf-8"), is_text=True)

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
    """Base class for streaming handlers"""

    def __init__(self, config: LLMStreamingConfiguration):
        self.config = config

    @abstractmethod
    async def generate_stream(
        self, events: AsyncGenerator
    ) -> AsyncGenerator[Token, None]:
        pass

    async def handle_error(self, error: Exception) -> Token:
        """Handle streaming errors gracefully"""
        logger.error(f"Streaming error: {str(error)}")
        return Token.from_status(f"Error: {str(error)}")

    async def process_stream(
        self, events: AsyncGenerator
    ) -> AsyncGenerator[Token, None]:
        """Common stream processing with error handling and retries"""
        retry_count = 0
        while retry_count < self.config.max_retries:
            try:
                async for token in self.generate_stream(events):
                    yield token
                return
            except Exception as e:
                retry_count += 1
                if retry_count >= self.config.max_retries:
                    yield await self.handle_error(e)
                    return
                await asyncio.sleep(self.config.retry_interval)


class OpenAIStreaming(StreamingHandler):
    @observe(as_type="generation", name="openai_output_stream")
    async def generate_stream(self, events):
        events = await events
        content_received = False
        async for event in events:
            if event.choices[0].delta.content is not None:
                content_received = True
                yield Token.from_text(event.choices[0].delta.content)
            elif event.choices[0].delta.content is None and content_received:
                return


class AnthropicStreaming(StreamingHandler):
    @observe(as_type="generation", name="anthropic_output_stream")
    async def generate_stream(self, events):
        events = await events
        async for event in events:
            if event.type == "content_block_delta":
                yield Token.from_text(event.delta.text)
            elif event.type == "content_block_stop":
                return


class MLXStreaming(StreamingHandler):
    @observe(as_type="generation", name="mlx_output_stream")
    async def generate_stream(self, events):
        async for event in events:
            if event.text:
                yield Token.from_text(event.text)


class LocalModelStreaming(StreamingHandler):
    """Base handler for local model streaming (Llama.cpp, Ollama)"""

    @observe(as_type="generation", name="local_model_output_stream")
    async def generate_stream(self, events):
        async for event in events:
            if event.choices[0].delta.content is not None:
                yield Token.from_text(event.choices[0].delta.content)


# Map providers to their streaming handlers
STREAMING_HANDLERS = {
    "openai": OpenAIStreaming,
    "azure": OpenAIStreaming,
    "anthropic": AnthropicStreaming,
    "groq": OpenAIStreaming,  # Groq uses OpenAI-compatible streaming
    "mlx": MLXStreaming,
    "llama-cpp": LocalModelStreaming,
    "ollama": LocalModelStreaming,
}


class StreamingHandlerFactory:
    _config_cache: Dict[str, LLMStreamingConfiguration] = {}

    @classmethod
    def get_streaming_strategy(
        cls, model: str, config: Optional[LLMStreamingConfiguration] = None
    ) -> StreamingHandler:
        """
        Get appropriate streaming handler for a model

        Parameters
        ----------
        model : str
            Model identifier
        config : Optional[StreamingConfiguration]
            Optional streaming configuration override

        Returns
        -------
        StreamingHandler
            Configured streaming handler for the model
        """
        try:
            provider = model_provider_registry.get_provider(model)

            if config is None:
                if model not in cls._config_cache:
                    cls._config_cache[model] = LLMStreamingConfiguration()
                config = cls._config_cache[model]

            handler_class = STREAMING_HANDLERS.get(provider)
            if not handler_class:
                raise ValueError(
                    f"No streaming handler for provider: {provider}"
                )

            return handler_class(config)

        except Exception as e:
            logger.error(f"Error creating streaming handler: {str(e)}")
            raise
