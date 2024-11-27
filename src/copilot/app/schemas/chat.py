from pydantic import BaseModel
from typing import Optional, List

from config.base_config import rag_config
from config.base_config import chat_config


class ChatRequest(BaseModel):
    query: str
    language: Optional[str] = None
    tag: Optional[List[str]] = None
    source: Optional[List[str]] = None
    llm_model: Optional[str] = rag_config["llm"]["model"]
    temperature: Optional[float] = rag_config["llm"]["temperature"]
    top_p: Optional[float] = rag_config["llm"]["top_p"]
    max_output_tokens: Optional[int] = rag_config["llm"]["max_output_tokens"]
    retrieval_method: Optional[List[str]] = rag_config["retrieval"][
        "retrieval_method"
    ]
    k_retrieve: Optional[int] = rag_config["retrieval"]["top_k"]
    k_memory: Optional[int] = chat_config["memory"]["k_memory"]
    response_style: Optional[str] = None
    command: Optional[str] = None
    command_args: Optional[str] = None
    autocomplete: Optional[bool] = True
    rag: Optional[bool] = True
    agentic_rag: Optional[bool] = False
    isFollowUpQ: Optional[bool] = False
    user_uuid: Optional[str] = None
    conversation_uuid: Optional[str] = None
