"""
This module provides an implementation of the Llama-cpp LLM model.

Classes:
    LlamaCppLLM: A class that encapsulates methods to interact with a Llama-cpp LLM instanciated locally with llama-cpp-python.
"""

import logging

# NEED TO UPDATE LOGIC OF PROMPT BASED ON MODEL
from rag.prompts import OPENAI_RAG_SYSTEM_PROMPT_DE

from models.llm.base import LLM
from models.config import SUPPORTED_LLAMACPP_LLM_MODELS, DEFAULT_LLAMACPP_LLM_MODEL
from typing import List

from llama_cpp import Llama

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LlamaCppLLM(LLM):

    def __init__(self, model_name: str = DEFAULT_LLAMACPP_LLM_MODEL, stream: bool = True, temperature: float = 0.0, top_p: float = 0.95, top_k: int = 0, quantization: int = 8, max_tokens: int = 512, n_ctx: int = 8192, n_gpu_layers: int = -1, verbose: bool = False):
        self.model_name = model_name if model_name is not None and model_name in SUPPORTED_LLAMACPP_LLM_MODELS else DEFAULT_LLAMACPP_LLM_MODEL
        self.stream = stream
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.quantization = quantization
        self.max_tokens = max_tokens
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.verbose = verbose
        self.client  = Llama.from_pretrained(
            repo_id=self.model_name,
            filename=f"*q{self.quantization}_0.gguf",
            n_ctx=self.n_ctx,
            n_gpu_layers=self.n_gpu_layers,
            verbose=self.verbose
        )

    # TO DO: proper return type for generate
    def generate(self, messages: List[dict]) -> str:
        try:
            return self.client.create_chat_completion(
            messages=messages,
            stream=self.stream)
        except Exception as e:
            raise e

    def stream(self, messages: List[str]):
        pass

