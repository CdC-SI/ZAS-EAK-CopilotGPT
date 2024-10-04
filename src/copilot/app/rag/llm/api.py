"""
This module provides an implementation of API LLM models.
"""

import logging

from typing import List, Any
from rag.llm.base import BaseLLM
from config.llm_config import DEFAULT_OPENAI_LLM_MODEL, DEFAULT_ANTHROPIC_LLM_MODEL

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
        The name of the OpenAI LLM model to use for response generation.
    stream : bool
        Whether to stream the response generation.
    temperature : float
        The temperature to use for response generation.
    top_p : float
        The top-p value to use for response generation.
    max_tokens : int
        The maximum number of tokens to generate.
    """
    def __init__(self, model_name: str = DEFAULT_OPENAI_LLM_MODEL, stream: bool = True, temperature: float = 0.0, top_p: float = 0.95, max_tokens: int = 512):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = clientLLM
        super().__init__(stream)

    def generate(self, messages: List[dict]) -> str:
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
            return self.llm_client.chat.completions.create(
                model=self.model_name,
                stream=False,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                messages=messages
            )
        except Exception as e:
            raise e

    def _stream(self, messages: List[Any]):
        try:
            stream = self.llm_client.chat.completions.create(
                model=self.model_name,
                stream=True,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                messages=messages
            )

            return stream
        except Exception as e:
            raise e

class AnthropicLLM(BaseLLM):
    """
    Class used to generate responses using an Anthropic API Large Language Model (LLM).

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
    def __init__(self, model_name: str = DEFAULT_ANTHROPIC_LLM_MODEL, stream: bool = True, temperature: float = 0.0, top_p: float = 0.95, max_tokens: int = 512):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = clientLLM
        super().__init__(stream)

    def generate(self, messages: List[dict]) -> str:
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
            return self.llm_client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                messages=messages,
                top_p=self.top_p,
                temperature=self.temperature,
                stream=False
            )
        except Exception as e:
            raise e

    def _stream(self, messages: List[Any]):
        try:
            stream = self.llm_client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                messages=messages,
                top_p=self.top_p,
                temperature=self.temperature,
                stream=True
            )
            return stream
        except Exception as e:
            raise e
