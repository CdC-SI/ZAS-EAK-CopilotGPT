from dataclasses import dataclass
from typing import Optional

from config.ai_models.supported import LLM
from .retrieval import RetrievalConfig


@dataclass
class LLMConfig:
    model: Optional[LLM] = LLM.GPT_4O_MINI
    temperature: float = 0
    max_tokens: int = 2048
    top_p: float = 0.95

    def __post_init__(self):
        if not isinstance(self.model, LLM):
            self.model = LLM[str(self.model)]

        if self.temperature < 0:
            self.temperature = 0

        if self.max_tokens < 1:
            self.max_tokens = 2048

        if not 0 <= self.top_p <= 1:
            self.top_p = 0.95


@dataclass
class RAGConfig:
    enabled: bool = True
    stream: bool = True

    Retrieval: RetrievalConfig = RetrievalConfig()
    LLM: LLMConfig = LLMConfig()

    def __post_init__(self):
        if not isinstance(self.Retrieval, RetrievalConfig):
            params = {}
            if isinstance(self.Retrieval, dict):
                params = self.Retrieval
            elif isinstance(self.Retrieval, list):
                params = {'retrievers': self.Retrieval}
            elif isinstance(self.Retrieval, str):
                params = {'retrievers': [self.Retrieval]}
            self.Retrieval = RetrievalConfig(**params)

        if not isinstance(self.LLM, LLMConfig):
            params = self.LLM if isinstance(self.LLM, dict) else {}
            self.LLM = LLMConfig(**params)
