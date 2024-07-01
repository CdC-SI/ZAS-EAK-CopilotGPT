"""
This module provides an implementation of the OpenAI LLM model.

Classes:
    OpenAILLM: A class that encapsulates methods to interact with OpenAI's language model APIs.
"""

import logging

from typing import List
from components.llm.base import LLM
from components.config import SUPPORTED_OPENAI_LLM_MODELS, DEFAULT_OPENAI_LLM_MODEL

from config.openai_config import openai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OpenAILLM(LLM):
    """
    A class that encapsulates methods to interact with OpenAI's language model APIs.

    Attributes
    ----------
    model_name : str
        The name of the OpenAI LLM model.
    stream : bool
        Whether to stream the response.
    temperature : float
        The temperature to use for the generation.
    top_p : float
        The top_p value to use for the generation.
    client : openai.OpenAI
        The OpenAI client.

    Methods
    -------
    generate(messages: List[dict]) -> str:
        Generate a response using the OpenAI LLM model.
    stream():
        Placeholder method for streaming. Currently not implemented.
    """
    def __init__(self, model_name: str = DEFAULT_OPENAI_LLM_MODEL, stream: bool = True, temperature: float = 0.0, top_p: float = 0.95, top_k: int = 0, max_tokens: int = 512, verbose: bool = False):
        """
        Initialize an instance of the OpenAILLM class.

        Parameters
        ----------
        model_name : str, optional
            The name of the OpenAI LLM model, by default DEFAULT_OPENAI_LLM_MODEL
        stream : bool, optional
            Whether to stream the response, by default True
        temperature : float, optional
            The temperature to use for the generation, by default 0.0
        top_p : float, optional
            The top_p value to use for the generation, by default 0.95
        """
        self.model_name = model_name if model_name is not None and model_name in SUPPORTED_OPENAI_LLM_MODELS else DEFAULT_OPENAI_LLM_MODEL
        self.stream = stream
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_tokens = max_tokens
        self.verbose = verbose
        self.client = openai.OpenAI()

    def generate(self, messages: List[dict]) -> str:
        """
        Generate a response using the OpenAI LLM model.

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
            return self.client.chat.completions.create(
                model=self.model_name,
                stream=self.stream,
                temperature=self.temperature,
                top_p=self.top_p,
                messages=messages
            )
        except Exception as e:
            raise e

    def stream(self):
        """
        Placeholder method for streaming. Currently not implemented.
        """
        pass
