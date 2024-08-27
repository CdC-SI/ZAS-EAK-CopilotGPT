"""
This module provides an implementation of the MLXLLM model.

Classes:
    MLXLLM: A class that encapsulates methods to interact with MLX server's language model APIs.
"""
import os
import logging
import requests
from typing import List, Any
from rag.llm.base import BaseLLM
from config.llm_config import DEFAULT_MLX_LLM_MODEL
from rag.models import ResponseModel, Choice, Delta


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MLX_GENERATION_ENDPOINT = os.environ.get("MLX_GENERATION_ENDPOINT", None)

class MLXLLM(BaseLLM):
    """
    Class used to generate responses using an MLX API Large Language Model (LLM).

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

    Methods
    -------
    _generate(messages: List[dict]) -> str
        Generates a single string response for a list of messages using the OpenAI LLM model.
    _stream()
        Generates a stream of events as response for a list of messages using the OpenAI LLM model.
    """
    def __init__(self, model_name: str = DEFAULT_MLX_LLM_MODEL, stream: bool = True, temperature: float = 0.0, top_p: float = 0.95, max_tokens: int = 512):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = None
        super().__init__(stream)

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
        raise NotImplementedError("Method not implemented.")

    def _stream(self, messages: List[Any]):
        try:
            response = requests.get(MLX_GENERATION_ENDPOINT, params={'prompt': messages, 'stream': self.stream}, stream=True)
            for line in response.iter_lines():
                if line:
                    content = line.decode('utf-8')
                    if "STOP" in content:
                        text = content.replace("STOP", "")
                        yield ResponseModel(choices=[Choice(delta=Delta(content=text))])
                        yield ResponseModel(choices=[Choice(delta=Delta(content=None))])
                    else:
                        yield ResponseModel(choices=[Choice(delta=Delta(content=content))])

        except Exception as e:
            raise e
