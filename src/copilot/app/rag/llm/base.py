from abc import ABC, abstractmethod
from typing import List, Any, Dict


class BaseLLM(ABC):

    @abstractmethod
    def generate(self, messages: List[dict], stream: bool) -> str:
        """
        Generate an answer based on input messages using an LLM.

        Parameters
        ----------
        messages : List[dict]
            A list of messages. Each message is a dictionary containing the necessary information for the LLM to generate an answer.
        stream : bool
            A flag indicating whether to stream the answer.

        Returns
        -------
        str
            The generated answer.
        """