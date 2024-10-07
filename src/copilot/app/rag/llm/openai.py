"""
This module provides an implementation of the OpenAI LLM model.

Classes:
    OpenAILLM: A class that encapsulates methods to interact with OpenAI's language model APIs.
"""

import logging

from typing import List, Any
from rag.llm.base import BaseLLM
from config.llm_config import DEFAULT_OPENAI_LLM_MODEL

from config.clients_config import clientLLM

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAILLM(BaseLLM):
    """
    Class used to generate responses using an OpenAI API Large Language Model (LLM).

    Attributes
    ----------
    model_name : str
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
    def __init__(self, model_name: str = DEFAULT_OPENAI_LLM_MODEL, stream: bool = True, temperature: float = 0.0, top_p: float = 0.95, max_tokens: int = 2048):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = clientLLM
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
            return await self.llm_client.chat.completions.create(
                model=self.model_name,
                stream=False,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                messages=messages
            )
        except Exception as e:
            raise e

    async def _astream(self, messages: List[Any]):
        try:
            return await self.llm_client.chat.completions.create(
                model=self.model_name,
                stream=True,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                messages=messages
            )
        except Exception as e:
            raise e
