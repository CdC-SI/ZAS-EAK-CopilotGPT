from abc import ABC, abstractmethod
from typing import List, Any, Dict


class BaseLLM(ABC):

    def __init__(self, stream: bool):
        self.stream = stream

    @abstractmethod
    def generate(self, messages: List[dict]) -> str:
        """
        Generate an answer based on input messages using an LLM.

        Parameters
        ----------
        messages : List[dict]
            A list of messages. Each message is a dictionary containing the necessary information for the LLM to generate an answer.

        Returns
        -------
        str
            The generated answer.
        """

    @abstractmethod
    def _stream(self, messages: List[dict]):
        """
        Stream an answer based on input messages using an LLM.

        This method should be implemented to handle streaming of answers.
        """

    def call(self, messages: List[dict]):
        """
        Call the appropriate method based on the 'stream' parameter.

        If 'self.stream' is True, the '_stream' method is called. If 'self.stream' is False, the '_generate' method is called.

        Parameters
        ----------
        messages : List[dict]
            A list of messages. Each message is a dictionary containing the necessary information for the LLM to generate an answer.

        Returns
        -------
        str
            The generated or streamed answer.
        """
        match self.stream:
            case True:
                return self._stream(messages)
            case False:
                return self.generate(messages)