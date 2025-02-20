import os
from typing import List, Dict
from llm.base import BaseLLM
from config.llm_config import DEFAULT_LLAMACPP_LLM_MODEL
from schemas.llm import ResponseModel, Choice, Delta, Message
import aiohttp
import json

# Setup logging
from utils.logging import get_logger

logger = get_logger(__name__)

LLM_GENERATION_ENDPOINT = os.environ.get("LOCAL_LLM_GENERATION_ENDPOINT", None)
ASYNC_GENERATE_ENDPOINT = os.path.join(LLM_GENERATION_ENDPOINT, "completion")


class LlamaCppLLM(BaseLLM):
    """Class for generating responses using an Open Source LLM via LlamaCpp server.

    Parameters
    ----------
    model : str, optional
        Name of the LLM model (format: llama-cpp:<model>), by default DEFAULT_LLAMACPP_LLM_MODEL
    stream : bool, optional
        Whether to stream the response, by default True
    temperature : float, optional
        Sampling temperature, by default 0.0
    top_p : float, optional
        Top-p sampling parameter, by default 0.95
    max_tokens : int, optional
        Maximum tokens to generate, by default 512
    """

    def __init__(
        self,
        model: str = DEFAULT_LLAMACPP_LLM_MODEL,
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
        """Format messages into a prompt string.

        Parameters
        ----------
        messages : List[Dict]
            List of message dictionaries containing role and content

        Returns
        -------
        str
            Formatted prompt string combining system and user messages
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
        """Generate a response asynchronously.

        Parameters
        ----------
        messages : List[Dict]
            List of message dictionaries to generate response from

        Returns
        -------
        str
            Generated response

        Raises
        ------
        Exception
            If generation fails
        """
        messages = self._format_prompt(messages)
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

    async def _astream(self, messages: List[Dict]):
        """Stream responses asynchronously.

        Parameters
        ----------
        messages : List[Dict]
            List of message dictionaries to generate streaming response from

        Yields
        ------
        ResponseModel
            Streamed response chunks
        """
        messages = self._format_prompt(messages)
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
