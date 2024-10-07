from abc import ABC, abstractmethod
import logging
from langfuse.decorators import observe

from config.llm_config import SUPPORTED_OPENAI_LLM_MODELS, SUPPORTED_AZUREOPENAI_LLM_MODELS, SUPPORTED_ANTHROPIC_LLM_MODELS, SUPPORTED_GROQ_LLM_MODELS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StreamingHandler(ABC):
    @abstractmethod
    def generate_stream(self, stream, source_url):
        pass

class OpenAIStreaming(StreamingHandler):
    @observe()
    def generate_stream(self, events, source_url):
        content_received = False
        for event in events:
            logger.info("-------EVENT: %s", event)
            if event.choices[0].delta.content is not None:
                content_received = True
                yield event.choices[0].delta.content.encode("utf-8")
            elif event.choices[0].delta.content is None and content_received:
                yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode("utf-8")
                return

class AzureOpenAIStreaming(StreamingHandler):
    @observe()
    def generate_stream(self, events, source_url):
        content_received = False
        for event in events:
            logger.info("-------EVENT: %s", event)
            if event.choices[0].delta.content is not None:
                content_received = True
                yield event.choices[0].delta.content.encode("utf-8")
            elif event.choices[0].delta.content is None and content_received:
                yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode("utf-8")
                return
            elif not content_received:
                continue  # Skip initial None token

class AnthropicStreaming(StreamingHandler):
    @observe()
    def generate_stream(self, events, source_url):
        for event in events:
            logger.info("-------EVENT: %s", event)
            if event.type == "content_block_delta":
                yield event.delta.text
            elif event.type == "content_block_stop":
                yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode("utf-8")
                return

class StreamingHandlerFactory:
    @staticmethod
    def get_streaming_strategy(llm_model):
        if llm_model in SUPPORTED_OPENAI_LLM_MODELS or llm_model in SUPPORTED_GROQ_LLM_MODELS:
            return OpenAIStreaming()
        elif llm_model in SUPPORTED_AZUREOPENAI_LLM_MODELS:
            return AzureOpenAIStreaming()
        elif llm_model in SUPPORTED_ANTHROPIC_LLM_MODELS:
            return AnthropicStreaming()
        else:
            raise ValueError(f"Unsupported LLM model: {llm_model}")
