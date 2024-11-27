import os
import logging
from rag.llm.base import BaseLLM
from config.llm_config import DEFAULT_LLAMACPP_LLM_MODEL
from schemas.llm import ResponseModel, Choice, Delta, Message
import aiohttp
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

LLM_GENERATION_ENDPOINT = os.environ.get("LLM_GENERATION_ENDPOINT", None)
ASYNC_GENERATE_ENDPOINT = os.path.join(LLM_GENERATION_ENDPOINT, "completion")


class LlamaCppLLM(BaseLLM):
    """
    Class used to generate responses using an an Open Source Large Language Model (LLM) via API to LlamaCpp server.

    Attributes
    ----------
    model_name : str
        The name of the OpenAI mlx-community LLM model to use for response generation (starts with mlx-community/<model_name>)
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
        Generates a single string async response for a list of messages using the LlamaCppLLM model.
    _astream()
        Generates an async stream of events as response for a list of messages using the LlamaCppLLM model.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_LLAMACPP_LLM_MODEL,
        stream: bool = True,
        temperature: float = 0.0,
        top_p: float = 0.95,
        max_tokens: int = 512,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = None
        super().__init__(stream)

    async def agenerate(self, messages: str) -> str:
        """
        Generate a response using the LlamaCppLLM model.

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
        async with aiohttp.ClientSession() as session:
            logger.info(messages)
            async with session.post(
                ASYNC_GENERATE_ENDPOINT,
                json={
                    "prompt": messages,
                    "stream": "false",
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "n_predict": self.max_tokens,
                },
            ) as response:
                data = await response.json()
                return ResponseModel(
                    choices=[
                        Choice(
                            message=Message(content=data.get("content", ""))
                        )
                    ]
                )

    async def _astream(self, messages: str):
        async with aiohttp.ClientSession() as session:
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
            }
            async with session.post(
                ASYNC_GENERATE_ENDPOINT,
                json={
                    "prompt": messages,
                    "stream": True,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "n_predict": self.max_tokens,
                },
                headers=headers,
            ) as response:
                async for line in response.content:
                    if line:
                        content = (
                            line.decode("utf-8").replace("data: ", "").strip()
                        )
                        if content:
                            try:
                                data = json.loads(content)
                                if data.get("stop") is True:
                                    yield ResponseModel(
                                        choices=[
                                            Choice(delta=Delta(content=None))
                                        ]
                                    )
                                yield ResponseModel(
                                    choices=[
                                        Choice(
                                            delta=Delta(
                                                content=data.get("content", "")
                                            )
                                        )
                                    ]
                                )
                            except json.JSONDecodeError as e:
                                logger.warning(
                                    f"Failed to parse streaming response: {e}"
                                )
                                continue
