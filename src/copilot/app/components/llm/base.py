from abc import ABC, abstractmethod
from typing import List

class LLM(ABC):

    @abstractmethod
    def generate(
        self,
        messages: List[dict],
    ) -> str:
        """Generate an answer based on input messages using an LLM."""

    @abstractmethod
    def stream(self):
        """Stream an answer based on input messages using an LLM."""
