from typing import List, Any
from llm.base import BaseLLM
from config.llm_config import DEFAULT_OPENAI_LLM_MODEL
from config.clients_config import config

from utils.logging import get_logger
import json

logger = get_logger(__name__)


class OpenAILLM(BaseLLM):
    """
    OpenAI API Large Language Model (LLM) implementation.

    Parameters
    ----------
    model : str, optional
        Name of the LLM model, by default DEFAULT_OPENAI_LLM_MODEL
    stream : bool, optional
        Enable response streaming, by default True
    temperature : float, optional
        Sampling temperature, by default 0.0
    top_p : float, optional
        Nucleus sampling parameter, by default 0.95
    max_tokens : int, optional
        Maximum tokens in response, by default 2048

    Attributes
    ----------
    model : str
        Current model name
    temperature : float
        Sampling temperature
    top_p : float
        Nucleus sampling parameter
    max_tokens : int
        Maximum token limit
    llm_client : object
        OpenAI API client instance
    """

    def __init__(
        self,
        model: str = DEFAULT_OPENAI_LLM_MODEL,
        stream: bool = True,
        temperature: float = 0.0,
        top_p: float = 0.95,
        max_tokens: int = 2048,
    ):
        self.model = model.replace("groq:", "")
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.llm_client = config.factory.create_llm_client(model)
        super().__init__(stream)

    async def agenerate(self, messages: List[dict], tools: list = [], **kwargs) -> str:
        """
        Generate a response asynchronously using the LLM model.

        Parameters
        ----------
        messages : List[dict]
            List of message dictionaries containing conversation history
        **kwargs : dict
            Additional parameters to pass to the API call

        Returns
        -------
        str
            Generated response text

        Raises
        ------
        Exception
            If API call fails or other errors occur
        """
        try:
            params = {
                "model": self.model,
                "stream": False,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
                "messages": messages,
                # "tools": tools,
            }
            params.update(kwargs)
            if tools in [[], None, '']:
                return await self.llm_client.chat.completions.create(**params)
            else:
                params['tools'] = tools
                params.update(kwargs)

                response = await self.llm_client.chat.completions.create(**params)

                tool_call = response.choices[0].message.tool_calls[0]
                args = json.loads(tool_call.function.arguments)

                if tools['function']['name'] == 'mise_en_parallele_des_revenus':
                    result = mise_en_parallele_des_revenus(args)

                alt_res = response.choices[0].message
                if len(alt_res.tool_calls) > 1:
                    alt_res.tool_calls = [tool_calls]
                
                params['messages'].append(altered_res) 
                params['messages'].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
                params.update(kwargs)

                return client.chat.completions.create(**params)
        except Exception as e:
            raise e

    async def _astream(self, messages: List[Any], tools: list = [], **kwargs):
        """
        Stream responses asynchronously from the LLM model.

        Parameters
        ----------
        messages : List[Any]
            List of messages for the conversation
        **kwargs : dict
            Additional parameters to pass to the API call

        Returns
        -------
        AsyncIterator
            Stream of response chunks

        Raises
        ------
        Exception
            If streaming fails or other errors occur
        """
        try:
            params = {
                "model": self.model,
                "stream": False,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
                "messages": messages,
                # "tools": tools,
            }
            params.update(kwargs)
            if tools in [[], None, '']:
                return await self.llm_client.chat.completions.create(**params)
            else:
                params['tools'] = tools
                params.update(kwargs)

                response = await self.llm_client.chat.completions.create(**params)

                tool_call = response.choices[0].message.tool_calls[0]
                args = json.loads(tool_call.function.arguments)

                if tools['function']['name'] == 'mise_en_parallele_des_revenus':
                    result = mise_en_parallele_des_revenus(args)

                alt_res = response.choices[0].message
                if len(alt_res.tool_calls) > 1:
                    alt_res.tool_calls = [tool_calls]
                
                params['messages'].append(altered_res) 
                params['messages'].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
                params['stream'] = True
                params.update(kwargs)

                return client.chat.completions.create(**params)
        except Exception as e:
            raise e
