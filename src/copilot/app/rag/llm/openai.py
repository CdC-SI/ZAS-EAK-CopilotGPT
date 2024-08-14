"""
This module provides an implementation of the OpenAI LLM model.

Classes:
    OpenAILLM: A class that encapsulates methods to interact with OpenAI's language model APIs.
"""

import logging

from typing import List
from rag.llm.base import BaseLLM
from config.llm_config import SUPPORTED_OPENAI_LLM_MODELS, DEFAULT_OPENAI_LLM_MODEL

from config.openai_config import clientAI

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
    top_k : int
        The top-k value to use for response generation.
    max_tokens : int
        The maximum number of tokens to generate.
    verbose : bool
        Whether to print verbose output.
    client : openai.OpenAI
        The OpenAI client used to generate responses.

    Methods
    -------
    generate(messages: List[dict]) -> str
        Generates a response for a list of messages using the OpenAI LLM model.
    stream()
        Placeholder method for streaming. Currently not implemented.
    """
    def __init__(self, model_name: str = DEFAULT_OPENAI_LLM_MODEL, stream: bool = True, temperature: float = 0.0, top_p: float = 0.95, max_tokens: int = 512, verbose: bool = False):
        self.model_name = model_name if model_name is not None and model_name in SUPPORTED_OPENAI_LLM_MODELS else DEFAULT_OPENAI_LLM_MODEL
        self.stream = stream
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = clientAI

    def generate_text(self, messages: List[dict], stream: bool = False) -> str:
        """
        Generate a response using the OpenAI LLM model.

        Parameters
        ----------
        messages : List[dict]
            The messages to generate a response for.

        stream : bool
            Whether to stream the response generation.

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
                stream=stream,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                messages=messages
            )
        except Exception as e:
            raise e

    def generate_stream(self, messages: List[dict]):
        """

        """
        try:
            return self.llm_client.chat.completions.create(
                model=self.model_name,
                stream=self.stream,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                messages=messages
            )
        except Exception as e:
            raise e