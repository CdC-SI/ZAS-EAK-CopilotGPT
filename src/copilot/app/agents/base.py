from abc import abstractmethod
from typing import List, Callable
from pydantic import BaseModel

from config import AgentConfig

# from schemas.agents import FollowupQuestion
from llm.base import BaseLLM


class BaseAgent(BaseModel):

    def __init__(
        self,
        llm_client,
        name: str,
        system_prompt: str,
        tools: List[Callable],
        max_iterations: int = AgentConfig.retries,
    ):

        self.llm_client = llm_client
        self.name = name
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.tools = tools

    @abstractmethod
    async def run(self, query: str, conversational_memory: List[str]):
        pass


class Agent:

    # What should an agent do?
    # What methods?
    # Access to conversational memory, have memory (state), llm_client, message_builder, tools (eg. functions, rag)
    # input: query, language
    # output: (stream of) tokens

    def __init__(
        self,
        model: BaseLLM,
        system_prompt: str,
        max_loops: int = 3,
        tools=None,
        output_type=None,
        reason=None,
        result_schema=None,
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.max_loops = max_loops
        self.tools = tools
        self.output_type = output_type  # stream or single
        self.reason = reason  # will setup plan itself
        self.result_schema = result_schema  # structured schema -> you must return this schema and fill in the values
        self.context_vars = {}
        self.memory = None
        self.llm_client = None
        self.stream = True

    async def run(self) -> str:
        pass

    async def run_stream(self):  # -> AsyncIterator[Token]:
        pass

    def _register_tool(self, tool) -> None:
        pass

    def _prepare_messages(self, query: str) -> str:
        pass
