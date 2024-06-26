import logging

from typing import List
from components.llms.base import LLM

# Import env vars
from config.openai_config import openai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo-0125"
SUPPORTED_OPENAI_MODELS = ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview", "gpt-4o"]


class OpenAILLM(LLM):

    def __init__(self, model_name: str = DEFAULT_OPENAI_MODEL, stream: bool = True, temperature: float = 0.0, top_p: float = 0.95):
        self.model_name = model_name if model_name is not None and model_name in SUPPORTED_OPENAI_MODELS else DEFAULT_OPENAI_MODEL
        self.stream = stream
        self.temperature = temperature
        self.top_p = top_p
        self.client = openai.OpenAI()

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
