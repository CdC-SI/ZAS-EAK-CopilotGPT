"""
This module provides an implementation of the OpenAI LLM model.

Classes:
    OpenAILLM: A class that encapsulates methods to interact with OpenAI's language model APIs.
"""

import logging

from typing import List
from rag.llm.base import BaseLLM

from config.clients_config import Clients
from config.ai_models.supported import LLM

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
    temperature : float
        The temperature to use for response generation.
    top_p : float
        The top-p value to use for response generation.
    max_tokens : int
        The maximum number of tokens to generate.
    """
    def __init__(self, model: LLM, temperature: float, top_p: float, max_tokens: int):
        self.model_name = model.value.name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = Clients.LLM.value

    def generate(self, messages: List[dict], stream: bool) -> str:
        return self.llm_client.chat.completions.create(
            model=self.model_name,
            stream=stream,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            messages=messages
        )
