from pydantic import BaseModel
from typing import Optional, List


class ResponseBody(BaseModel):
    content: str


class RAGRequest(BaseModel):
    query: str
    language: Optional[str]
    tag: Optional[str]
    source: Optional[List[str]]
    llm_model: Optional[str]
    retrieval_method: Optional[List[str]]
    k_memory: Optional[int]
    response_style: Optional[str]
    autocomplete: bool
    rag: bool
    user_uuid: Optional[str]
    conversation_uuid: Optional[str]


class EmbeddingRequest(BaseModel):
    text: str
