import os
from typing import List, Dict
from llm.base import BaseLLM
from config.llm_config import DEFAULT_MLX_LLM_MODEL
from schemas.llm import ResponseModel, Choice, Delta, Message
import aiohttp

# Setup logging
from utils.logging import get_logger

logger = get_logger(__name__)

LLM_GENERATION_ENDPOINT = os.environ.get("LOCAL_LLM_GENERATION_ENDPOINT", None)
ASYNC_GENERATE_ENDPOINT = os.path.join(LLM_GENERATION_ENDPOINT, "agenerate")


class MLXLLM(BaseLLM):
    """
    Class used to generate responses using an an Open Source Large Language Model (LLM) via API to MLX server.

    Attributes
    ----------
    model : str
        The name of the OpenAI mlx-community LLM model to use for response generation (starts with mlx-community:<model>)
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
        Generates a single string async response for a list of messages using the MLXLLM model.
    _astream()
        Generates an async stream of events as response for a list of messages using the MLXLLM model.
    """

    def __init__(
        self,
        model: str = DEFAULT_MLX_LLM_MODEL,
        stream: bool = True,
        temperature: float = 0.0,
        top_p: float = 0.95,
        max_tokens: int = 512,
    ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = None
        super().__init__(stream)

    def _format_prompt(self, messages: List[Dict]) -> str:
        """Extract system and user prompts from messages list and format them."""
        system_prompt = ""
        query = ""

        for message in messages:
            if message.get("role") == "system":
                system_prompt = message.get("content", "")
            elif message.get("role") == "user":
                query = message.get("content", "")

        return (
            f"{system_prompt}\n\n{query}" if system_prompt and query else query
        )

    async def agenerate(self, messages: List[Dict]) -> str:
        """
        Generate a response using the MLXLLM model.

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
        messages = self._format_prompt(messages)
        async with aiohttp.ClientSession() as session:
            logger.info(messages)
            async with session.get(
                ASYNC_GENERATE_ENDPOINT,
                params={
                    "prompt": messages,
                    "stream": "false",
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "max_tokens": self.max_tokens,
                },
            ) as response:
                text = await response.text()
                return ResponseModel(
                    choices=[Choice(message=Message(content=text))]
                )

    async def _astream(self, messages: List[Dict]):
        messages = self._format_prompt(messages)
        async with aiohttp.ClientSession() as session:
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
            }
            async with session.get(
                ASYNC_GENERATE_ENDPOINT,
                params={
                    "prompt": messages,
                    "stream": "true",
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "max_tokens": self.max_tokens,
                },
                headers=headers,
            ) as response:
                async for line in response.content:
                    if line:
                        content = (
                            line.decode("utf-8")
                            .replace("data: ", "")
                            .replace("\n", "")
                        )
                        if content != "[DONE]":
                            yield ResponseModel(
                                choices=[Choice(delta=Delta(content=content))]
                            )
                        else:
                            yield ResponseModel(
                                choices=[Choice(delta=Delta(content=None))]
                            )
