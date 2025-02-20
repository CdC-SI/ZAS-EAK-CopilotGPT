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
    Interface for generating responses using MLX models via API.

    Parameters
    ----------
    model : str, optional
        MLX model identifier, by default DEFAULT_MLX_LLM_MODEL
    stream : bool, optional
        Enable response streaming, by default True
    temperature : float, optional
        Sampling temperature, by default 0.0
    top_p : float, optional
        Top-p sampling parameter, by default 0.95
    max_tokens : int, optional
        Maximum tokens to generate, by default 512
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
        """
        Format messages into a single prompt string.

        Parameters
        ----------
        messages : List[Dict]
            List of message dictionaries containing role and content

        Returns
        -------
        str
            Formatted prompt combining system and user messages
        """
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
        Generate a complete response asynchronously.

        Parameters
        ----------
        messages : List[Dict]
            List of message dictionaries to generate response from

        Returns
        -------
        ResponseModel
            Model containing the generated response

        Raises
        ------
        Exception
            If generation fails
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
        """
        Stream response tokens asynchronously.

        Parameters
        ----------
        messages : List[Dict]
            List of message dictionaries to generate response from

        Yields
        ------
        ResponseModel
            Model containing each generated token or completion signal
        """
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
