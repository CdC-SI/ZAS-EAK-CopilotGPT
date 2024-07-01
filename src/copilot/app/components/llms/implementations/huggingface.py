"""
This module provides an implementation of the HuggingFace LLM model.

Classes:
    HuggingFaceLLM: A class that encapsulates methods to interact with HuggingFace LLMs.
"""
import logging

from typing import List
from components.llms.base import LLM
from components.config import SUPPORTED_HUGGINGFACE_LLM_MODELS, DEFAULT_HUGGINGFACE_LLM_MODEL

from config.openai_config import openai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HuggingFaceLLM(LLM):

    def __init__(self, model_name: str = DEFAULT_HUGGINGFACE_LLM_MODEL, stream: bool = True, temperature: float = 0.0, top_p: float = 0.95):
        self.model_name = model_name if model_name is not None and model_name in SUPPORTED_HUGGINGFACE_LLM_MODELS else DEFAULT_HUGGINGFACE_LLM_MODEL
        self.stream = stream
        self.temperature = temperature
        self.top_p = top_p
        self.client = None

    def generate(self, messages: List[dict]) -> str:
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
        pass
