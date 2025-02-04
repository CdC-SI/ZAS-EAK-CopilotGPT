from dataclasses import dataclass

from config.clients_config import clientLLM


@dataclass
class AgentConfig:
    retries = 5


agent_config = {
    "llm_client": clientLLM,
    "system_prompt": "Assist with pension-related queries.",
    "max_iterations": 5,
    "tools": ["calculator", "knowledge_base"],  # Example tools
    "output_type": "stream",
    "reason": "financial analysis",
    "result_schema": {
        "type": "json",
        "fields": ["balance", "age", "retirement"],
    },
    "context_vars": {"region": "US"},
    "memory": None,
    "stream": True,
}
