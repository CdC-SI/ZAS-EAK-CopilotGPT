from abc import ABC, abstractmethod
from typing import List, Any, Dict


class BaseLLM(ABC):

    def __init__(self, stream: bool):
        self.stream = stream

    @abstractmethod
    def agenerate(self, messages: List[dict]) -> str:
        """
        Asynchronously generate an answer based on input messages using an LLM.
        """

    @abstractmethod
    def _astream(self, messages: List[dict]):
        """
        Asynchronously stream an answer based on input messages using an LLM.
        """

    def call(self, messages: List[dict]):
        """
        Call the appropriate method based on the 'stream' parameter.
        """
        if self.stream:
            return self._astream(messages)
        else:
            return self.agenerate(messages)