import logging

from rag.prompts import OPENAI_RAG_SYSTEM_PROMPT_DE

from components.llms.base import LLM
from typing import List

from llama_cpp import Llama

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_QWEN_MODEL = "text-embedding-ada-002"
SUPPORTED_QWEN_MODELS = ["text-embedding-ada-002"]

class QwenLLM(LLM):

    def __init__(self, model_name: str = DEFAULT_QWEN_MODEL):
        self.model_name = model_name
        self.llm  = Llama.from_pretrained(
            repo_id="Qwen/Qwen1.5-0.5B-Chat-GGUF",
            filename="*q8_0.gguf",
            verbose=False
        )

    def generate(
        self,
        prompt: List[str],
    ) -> str:
        pass

    def create_messages(self, context_docs: List[str], query: str) -> str:

        qwen_rag_system_prompt = QWEN_RAG_SYSTEM_PROMPT_DE.format(context_docs=context_docs, query=query)
        messages = [{"role": "system", "content": qwen_rag_system_prompt}]

        return messages


    def stream(self, messages: List[str]):

        messages = self.create_messages(context_docs, query)
        output = llm.create_chat_completion(
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Write a joyful poem about spring"
                }
            ],
            stream=True
)
