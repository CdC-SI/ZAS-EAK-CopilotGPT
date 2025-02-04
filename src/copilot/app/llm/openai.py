from typing import List, Dict, Any
from llm.base import BaseLLM, LLMResponse, ConfigurationError, GenerationError
from config.llm_config import DEFAULT_OPENAI_LLM_MODEL
from config.clients_config import config

from utils.logging import get_logger

logger = get_logger(__name__)


class OpenAILLM(BaseLLM):
    """
    Class used to generate responses using an OpenAI API Large Language Model (LLM).

    Attributes
    ----------
    model : str
        The name of the LLM model to use for response generation.
    stream : bool
        Whether to stream the response generation.
    temperature : float
        The temperature to use for response generation.
    top_p : float
        The top-p value to use for response generation.
    max_tokens : int
        The maximum number of tokens to generate.
    """

    def __init__(
        self,
        model: str = DEFAULT_OPENAI_LLM_MODEL,
        stream: bool = True,
        temperature: float = 0.0,
        top_p: float = 0.95,
        max_tokens: int = 2048,
    ):
        self.model = model.replace("groq:", "")
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = config.factory.create_llm_client(model)
        super().__init__(stream)

    async def agenerate(self, messages: List[dict]) -> str:
        """
        Generate a response using the LLM model.

        Parameters
        ----------
        messages : List[dict]
            The messages to generate a response for.

        Returns
        -------
        str
            The generated response.

        Raises
        ------
        Exception
            If an error occurs during generation.
        """
        try:
            await self._validate_messages(messages)
            raw_response = await self.llm_client.chat.completions.create(
                model=self.model,
                stream=False,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                messages=messages,
            )
            return await self._format_response(raw_response)
        except Exception as e:
            await self._handle_error(e)

    async def _astream(self, messages: List[Any]):
        try:
            await self._validate_messages(messages)
            raw_response = await self.llm_client.chat.completions.create(
                model=self.model,
                stream=True,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                messages=messages,
            )
            return await self._format_response(raw_response)
        except Exception as e:
            await self._handle_error(e)

    async def _validate_messages(self, messages: List[Dict[str, Any]]) -> bool:
        """Validate OpenAI message format"""
        try:
            for message in messages:
                if not isinstance(message, dict):
                    raise ConfigurationError("Message must be a dictionary")
                if "role" not in message or "content" not in message:
                    raise ConfigurationError(
                        "Message must contain 'role' and 'content'"
                    )
                if message["role"] not in ["user", "assistant", "system"]:
                    raise ConfigurationError(
                        "Message role must be 'user', 'assistant', or 'system'"
                    )
            return True
        except Exception as e:
            raise ConfigurationError(f"Message validation failed: {str(e)}")

    async def _format_response(self, raw_response: Any) -> LLMResponse:
        """Format OpenAI response"""
        try:
            return LLMResponse(
                content=raw_response.choices[0].message.content,
                usage=(
                    raw_response.usage.dict() if raw_response.usage else None
                ),
                model=raw_response.model,
                finish_reason=raw_response.choices[0].finish_reason,
            )
        except Exception as e:
            raise GenerationError(f"Failed to format response: {str(e)}")

    async def _handle_error(self, error: Exception) -> None:
        """Handle OpenAI-specific errors"""
        import openai

        if isinstance(error, openai.APIError):
            logger.error(f"OpenAI API error: {str(error)}")
            raise GenerationError(f"OpenAI API error: {str(error)}")
        elif isinstance(error, openai.APIConnectionError):
            logger.error(f"OpenAI connection error: {str(error)}")
            raise GenerationError(f"Connection error: {str(error)}")
        elif isinstance(error, openai.RateLimitError):
            logger.error(f"OpenAI rate limit error: {str(error)}")
            raise GenerationError(f"Rate limit exceeded: {str(error)}")
        else:
            logger.error(f"Unexpected error: {str(error)}")
            raise
