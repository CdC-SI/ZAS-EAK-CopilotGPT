from pydantic import BaseModel
from typing import Optional, List

from config.base_config import rag_config
from config.base_config import chat_config

class ResponseBody(BaseModel):
    content: str


class RAGRequest(BaseModel):
    query: str
    language: Optional[str] = None
    tag: Optional[List[str]] = None
    source: Optional[List[str]] = None
    llm_model: Optional[str] = "gpt-4o-2024-05-13"
    retrieval_method: Optional[List[str]] = ["top_k_retriever", "reranking"]
    k_memory: Optional[int] = 3
    response_style: Optional[str] = None
    command: Optional[str] = None
    command_args: Optional[List[str]] = None
    autocomplete: Optional[bool] = None
    rag: Optional[bool] = None
    user_uuid: Optional[str] = None
    conversation_uuid: Optional[str] = None


class EmbeddingRequest(BaseModel):
    text: str
