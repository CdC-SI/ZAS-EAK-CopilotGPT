from config.clients_config import llm_client

agent_config = {
    "llm_client": llm_client,
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
