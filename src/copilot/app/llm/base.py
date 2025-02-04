from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from utils.logging import get_logger
from config.llm_config_manager import llm_config_manager
from clients.client_manager import client_manager

logger = get_logger(__name__)


@dataclass
class LLMResponse:
    """Structured response from LLM"""

    content: str
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    finish_reason: Optional[str] = None


class LLMError(Exception):
    """Base exception for LLM-related errors"""

    pass


class ConfigurationError(LLMError):
    """Raised when configuration is invalid"""

    pass


class GenerationError(LLMError):
    """Raised when generation fails"""

    pass


class BaseLLM(ABC):
    """Abstract base class for LLM implementations"""

    def __init__(self, model: str, stream: bool = True, **kwargs):
        self.model = model
        self.stream = stream
        self._client = None
        self._config = None

    @abstractmethod
    async def _validate_messages(self, messages: List[Dict[str, Any]]) -> bool:
        """
        Validate message format for specific provider.
        Should raise ConfigurationError if invalid.
        """
        pass

    @abstractmethod
    async def _format_response(self, raw_response: Any) -> LLMResponse:
        """Format raw response into standard LLMResponse"""
        pass

    @abstractmethod
    async def _handle_error(self, error: Exception) -> None:
        """Provider-specific error handling"""
        pass

    async def _get_client(self):
        """Get or create client instance"""
        if not self._client:
            self._client = await client_manager.get_llm_client(
                self.model, self._config
            )
        return self._client

    async def _ensure_configuration(self):
        """Ensure valid configuration exists"""
        if not self._config:
            self._config = llm_config_manager.get_merged_config(self.model)

    async def agenerate(self, messages: List[Dict[str, Any]]) -> LLMResponse:
        """
        Generate response from messages.

        Parameters
        ----------
        messages : List[Dict[str, Any]]
            List of message dictionaries

        Returns
        -------
        LLMResponse
            Structured response object

        Raises
        ------
        ConfigurationError
            If configuration or messages are invalid
        GenerationError
            If generation fails
        """
        try:
            await self._ensure_configuration()
            await self._validate_messages(messages)

            client = await self._get_client()
            raw_response = await client.chat.completions.create(
                messages=messages,
                model=self.model,
                stream=False,
                **self._config,
            )

            return await self._format_response(raw_response)

        except ConfigurationError as e:
            logger.error(f"Configuration error for {self.model}: {str(e)}")
            raise
        except Exception as e:
            await self._handle_error(e)
            raise GenerationError(f"Generation failed: {str(e)}")

    async def _astream(self, messages: List[Dict[str, Any]]):
        """
        Stream response from messages.

        Parameters
        ----------
        messages : List[Dict[str, Any]]
            List of message dictionaries

        Yields
        ------
        Dict[str, Any]
            Stream of tokens/chunks

        Raises
        ------
        ConfigurationError
            If configuration or messages are invalid
        GenerationError
            If streaming fails
        """
        try:
            await self._ensure_configuration()
            await self._validate_messages(messages)

            client = await self._get_client()
            async for chunk in client.chat.completions.create(
                messages=messages,
                model=self.model,
                stream=True,
                **self._config,
            ):
                yield chunk

        except ConfigurationError as e:
            logger.error(f"Configuration error for {self.model}: {str(e)}")
            raise
        except Exception as e:
            await self._handle_error(e)
            raise GenerationError(f"Streaming failed: {str(e)}")

    async def call(self, messages: List[Dict[str, Any]]):
        """Route to streaming or non-streaming generation"""
        if self.stream:
            return self._astream(messages)
        return await self.agenerate(messages)

    async def cleanup(self):
        """Cleanup resources"""
        if self._client:
            await client_manager.cleanup()
            self._client = None
