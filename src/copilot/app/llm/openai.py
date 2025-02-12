from typing import List, Any
from llm.base import BaseLLM
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

    async def agenerate(self, messages: List[dict], **kwargs) -> str:
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
            params = {
                "model": self.model,
                "stream": False,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
                "messages": messages,
            }
            params.update(kwargs)
            return await self.llm_client.chat.completions.create(**params)
        except Exception as e:
            raise e

    async def _astream(self, messages: List[Any], **kwargs):
        try:
            params = {
                "model": self.model,
                "stream": True,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
                "messages": messages,
            }
            params.update(kwargs)
            return await self.llm_client.chat.completions.create(**params)
        except Exception as e:
            raise e
