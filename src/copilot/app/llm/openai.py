from typing import List, Any
from llm.base import BaseLLM
from config.llm_config import DEFAULT_OPENAI_LLM_MODEL
from config.clients_config import config
from ai.sic import get_invalidite

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

    async def tool_called(self, events):
        res = False
        async for event in events:
            logger.info(event.choices[0].delta)
            if event.choices[0].delta.content is None:
                if event.choices[0].delta.tool_calls is not None:
                    res = True
                    break
            else:
                res = False
                break
        logger.info(f"\n+-------------\n\ntool is called ? {res}\n\n-------------+\n")
        return res
    
    async def info_complete(self, events):
        message = ""
        async for event in events:
            content = event.choices[0].delta.content
            message += content if content is not None else ""
        response = await self.llm_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "your goal is to determine if the message received from the user indicates that all of the information has been gathered. Your assesment should only focus on the actual information. Don't take into account messages adressed to the user like 'here are the information i've collected so far...' or 'if all the data is correct i will proceed'. if it has simply answer 'yes' else answer with 'no'. you answer should be stritly limited to yes or no and nothing else."},
                {"role": "user", "content": message}
                ],
            stream=False
        )
        logger.info(response.choices[0])
        if response.choices[0].message.content == 'yes':
            return message
        elif response.choices[0].message.content == 'no':
            return None
        else:
            return message if 'yes' in response.choices[0].content else None

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
                "stream": True,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
                "messages": [messages[-1]],
                "tools": tools,
                "tool_choice": 'auto'
            }
            params.update(kwargs)

            logger.info(f"\n+-------------\n\n{messages}\n\n-------------+\n")
                    
            if tools in [[], None, '']:
                # params['stream'] = True
                # params.update(kwargs)
                return await self.llm_client.chat.completions.create(**params)
            else:
            # is_called = await self.tool_called(response)
            # should_be_called = await self.info_complete(response)
            # if not is_called:
            #     if should_be_called is None:
            #         return response

            # params['stream'] = False
            # params['messages'] = should_be_called
            # params['tool_choice'] = {"type": "function", "function": {"name": "get_invalidite"}}
            # params.update(kwargs)
                response = await self.llm_client.chat.completions.create(**params)
                if await self.tool_called(response):
                    final_tool_calls = {}

                    async for chunk in response:
                        for tool_call in chunk.choices[0].delta.tool_calls or []:
                            index = tool_call.index

                            if index not in final_tool_calls:
                                final_tool_calls[index] = tool_call

                            final_tool_calls[index].function.arguments += tool_call.function.arguments if tool_call.function.arguments != final_tool_calls[index].function.arguments else ""
                    
                    final_tool_call = final_tool_calls[0]
                    # params['tools'] = tools
                    # params.update(kwargs)
                    logger.info(f"\n+-------------\n\n{len(params['messages'])}\n\n-------------+\n")
                    # response = await self.llm_client.chat.completions.create(**params)
                    logger.info(f"-----\n\n{final_tool_call}\n\n-----")

                    args = json.loads(final_tool_call.function.arguments)['benef']
                    logger.info(f"\n+-------------\n\n{args}\n\n-------------+\n")
                    # if tools[0]['function']['name'] == 'get_invalidite':
                    result = get_invalidite(args)

                    # alt_res = response.choices[0].message
                    # if len(alt_res.tool_calls) > 1:
                    #     alt_res.tool_calls = [final_tool_call]
                    
                    params['messages'].append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls":[{
                            "id": final_tool_call.id,
                            "function": {"arguments": args, "name": final_tool_call.function.name},
                            "type": "function"
                        }]
                    }) 
                    params['messages'].append({
                        "role": "tool",
                        "tool_call_id": final_tool_call.id,
                        "content": result
                    })
                    params['stream'] = True
                    params.update(kwargs)

                    return await self.llm_client.chat.completions.create(**params)
                else:
                    async for chunk in response:
                        logger.info(f"\n+-------------\n\n{chunk.choices[0]}\n\n-------------+\n")                 
                    return response
        except Exception as e:
            raise e
