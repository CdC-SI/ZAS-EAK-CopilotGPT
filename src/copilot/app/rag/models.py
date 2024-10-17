from pydantic import BaseModel
from typing import Optional, List


class ResponseBody(BaseModel):
    content: str


class RAGRequest(BaseModel):
    query: str
    language: Optional[str] = None
    tag: Optional[List[str]] = None
    source: Optional[List[str]] = None
    llm_model: Optional[str]
    retrieval_method: Optional[List[str]]
    k_memory: Optional[int]
    response_style: Optional[str] = None
    autocomplete: Optional[bool] = None
    rag: Optional[bool] = None
    user_uuid: Optional[str] = None
    conversation_uuid: Optional[str] = None


class EmbeddingRequest(BaseModel):
    text: str
