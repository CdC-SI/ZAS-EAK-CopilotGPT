from typing import List, Any
from config.clients_config import config
from llm.base import BaseLLM
from config.llm_config import DEFAULT_OLLAMA_LLM_MODEL
from schemas.llm import ResponseModel, Choice, Delta, Message


# Setup logging
from utils.logging import get_logger

logger = get_logger(__name__)


class OllamaLLM(BaseLLM):
    """
    Generates responses using Ollama server API.

    Parameters
    ----------
    model : str, optional
        Name of the Ollama model (default: DEFAULT_OLLAMA_LLM_MODEL)
    stream : bool, optional
        Enable response streaming (default: True)
    temperature : float, optional
        Sampling temperature (default: 0.0)
    top_p : float, optional
        Nucleus sampling parameter (default: 0.95)
    max_tokens : int, optional
        Maximum tokens to generate (default: 512)
    """

    def __init__(
        self,
        model: str = DEFAULT_OLLAMA_LLM_MODEL,
        stream: bool = True,
        temperature: float = 0.0,
        top_p: float = 0.95,
        max_tokens: int = 512,
    ):
        self.model = model.replace("ollama:", "")
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = config.factory.create_llm_client(model)
        super().__init__(stream)

    async def agenerate(self, messages: List[Any]) -> str:
        """
        Generate a single response using the Ollama model.

        Parameters
        ----------
        messages : List[Any]
            List of message dictionaries for the conversation

        Returns
        -------
        ResponseModel
            Model containing the generated response

        Raises
        ------
        Exception
            If generation fails
        """
        try:
            response = await self.llm_client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "num_predict": self.max_tokens,
                },
                stream=False,
            )
            return ResponseModel(
                choices=[
                    Choice(
                        message=Message(
                            content=response.message.get("content", "")
                        )
                    )
                ]
            )
        except Exception as e:
            raise e

    async def _astream(self, messages: List[Any]):
        """
        Stream responses from the Ollama model.

        Parameters
        ----------
        messages : List[Any]
            List of message dictionaries for the conversation

        Yields
        ------
        ResponseModel
            Model containing response deltas or completion signal

        Raises
        ------
        Exception
            If streaming fails
        """
        try:
            async for event in await self.llm_client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "num_predict": self.max_tokens,
                },
                stream=True,
            ):
                if event.done is True:
                    yield ResponseModel(
                        choices=[Choice(delta=Delta(content=None))]
                    )
                else:
                    yield ResponseModel(
                        choices=[
                            Choice(
                                delta=Delta(
                                    content=event.message.get("content", "")
                                )
                            )
                        ]
                    )
        except Exception as e:
            raise e
