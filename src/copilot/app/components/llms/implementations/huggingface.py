from abc import ABC, abstractmethod
from typing import List

class LLM(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: List[str],
    ) -> str:
        """Generate an answer based on an input prompt using an LLM."""

    @abstractmethod
    def stream():
        pass
