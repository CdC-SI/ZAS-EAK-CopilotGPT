import logging
from typing import List, Any
from config.clients_config import create_llm_client
from llm.base import BaseLLM
from config.llm_config import DEFAULT_OLLAMA_LLM_MODEL
from schemas.llm import ResponseModel, Choice, Delta, Message


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class OllamaLLM(BaseLLM):
    """
    Class used to generate responses using an an Open Source Large Language Model (LLM) via API to Ollama server.

    Attributes
    ----------
    model_name : str
        The name of the Ollama LLM model to use for response generation (starts with ollama/<model_name>)
    stream : bool
        Whether to stream the response generation.
    temperature : float
        The temperature to use for response generation.
    top_p : float
        The top-p value to use for response generation.
    max_tokens : int
        The maximum number of tokens to generate.

    Methods
    -------
    agenerate(messages: List[dict]) -> str
        Generates a single string async response for a list of messages using the Ollama model.
    _astream()
        Generates an async stream of events as response for a list of messages using the Ollama model.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_OLLAMA_LLM_MODEL,
        stream: bool = True,
        temperature: float = 0.0,
        top_p: float = 0.95,
        max_tokens: int = 512,
    ):
        self.model_name = model_name.replace("ollama/", "")
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = create_llm_client(model_name)
        super().__init__(stream)

    async def agenerate(self, messages: List[Any]) -> str:
        """
        Generate a response using the Ollama model.

        Parameters
        ----------
        messages : List[dict]
            The messages to generate a response for.

        Returns
        -------
        str
            The generated response.

        Raises
        ------
        Exception
            If an error occurs during generation.
        """
        try:
            response = await self.llm_client.chat(
                model=self.model_name,
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
        try:
            async for event in await self.llm_client.chat(
                model=self.model_name,
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
