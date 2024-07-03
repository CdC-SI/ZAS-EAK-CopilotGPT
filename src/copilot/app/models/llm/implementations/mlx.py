"""
This module provides an implementation of the MLX LLM model.

Classes:
    MlxLLM: A class that encapsulates methods to interact with an MLX LLM deployed on a server.
"""
import os
import logging
from dotenv import load_dotenv
from typing import List
import requests

from models.llm.base import LLM
from models.config import SUPPORTED_MLX_LLM_MODELS, DEFAULT_MLX_LLM_MODEL

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import env vars
load_dotenv()
MLX_GENERATION_ENDPOINT = os.environ["MLX_GENERATION_ENDPOINT"]


class MlxLLM(LLM):
    """
    A class that encapsulates methods to interact with an MLX LLM deployed on a server.

    Attributes
    ----------
    model_name : str
        The name of the MLX LLM model.
    stream : bool
        Whether to stream the response.
    temperature : float
        The temperature to use for the generation.
    top_p : float
        The top_p value to use for the generation.
    client : None
        Currently not used.

    Methods
    -------
    generate(messages: List[dict]) -> Generator[str, None, None]:
        Generate a response using the MLX LLM model.
    stream():
        Placeholder method for streaming. Currently not implemented.
    """
    def __init__(self, model_name: str = DEFAULT_MLX_LLM_MODEL, stream: bool = True, temperature: float = 0.0, top_p: float = 0.95, top_k: int = 0, max_tokens: int = 512, verbose: bool = False):
        """
        Initialize an instance of the MlxLLM class.

        Parameters
        ----------
        model_name : str, optional
            The name of the MLX LLM model, by default DEFAULT_MLX_LLM_MODEL
        stream : bool, optional
            Whether to stream the response, by default True
        temperature : float, optional
            The temperature to use for the generation, by default 0.0
        top_p : float, optional
            The top_p value to use for the generation, by default 0.95
        """
        self.model_name = model_name if model_name is not None and model_name in SUPPORTED_MLX_LLM_MODELS else DEFAULT_MLX_LLM_MODEL
        self.stream = stream
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_tokens = max_tokens
        self.verbose = verbose
        self.client = None

    # TO DO: proper return type for generate
    def generate(self, messages: List[dict]) -> str:
        """
        Generate a response using the MLX LLM model.

        Parameters
        ----------
        messages : List[dict]
            The messages to generate a response for.

        Returns
        -------
        Generator[str, None, None]
            A generator that yields the generated responses line by line.

        Raises
        ------
        Exception
            If an error occurs during generation.
        """
        try:
            response = requests.get(MLX_GENERATION_ENDPOINT, params={'prompt': messages, 'stream': self.stream}, stream=self.stream)
            for line in response.iter_lines():
                if line:
                    yield line.decode('utf-8')
        except Exception as e:
            raise e

    def stream(self):
        """
        Placeholder method for streaming. Currently not implemented.
        """
        pass