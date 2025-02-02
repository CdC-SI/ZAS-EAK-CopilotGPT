from typing import List, Any
from llm.base import BaseLLM
from config.clients_config import config
from config.llm_config import DEFAULT_ANTHROPIC_LLM_MODEL
from schemas.llm import ResponseModel, Choice, Message
from utils.logging import get_logger

logger = get_logger(__name__)


class AnthropicLLM(BaseLLM):
    """
    Class used to generate responses using an Anthropic API Large Language Model (LLM).

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
        model: str = DEFAULT_ANTHROPIC_LLM_MODEL,
        stream: bool = True,
        temperature: float = 0.0,
        top_p: float = 0.95,
        max_tokens: int = 2048,
    ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = config.factory.create_llm_client(model)
        super().__init__(stream)

    def _extract_system_prompt(self, messages: List[dict]) -> str:
        """Extract system prompt from messages list."""
        for message in messages:
            if message.get("role") == "system":
                return message.get("content", "")
        return ""

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
            system_prompt = self._extract_system_prompt(messages)
            response = await self.llm_client.messages.create(
                model=self.model,
                stream=False,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[m for m in messages if m.get("role") != "system"],
            )
            return ResponseModel(
                choices=[
                    Choice(message=Message(content=response.content[0].text))
                ]
            )
        except Exception as e:
            raise e

    async def _astream(self, messages: List[Any]):
        try:
            system_prompt = self._extract_system_prompt(messages)
            return await self.llm_client.messages.create(
                model=self.model,
                stream=True,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[m for m in messages if m.get("role") != "system"],
            )
        except Exception as e:
            raise e
