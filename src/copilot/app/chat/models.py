from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.inspection import inspect

class ChatRequest(BaseModel):
    query: str
    language: Optional[str] = None
    tag: Optional[List[str]] = None
    source: Optional[List[str]] = None
    llm_model: Optional[str] = None
    retrieval_method: Optional[List[str]] = None
    k_memory: Optional[int] = None
    response_style: Optional[str] = None
    command: Optional[str] = None
    command_args: Optional[List[str]] = None
    autocomplete: Optional[bool] = None
    rag: Optional[bool] = None
    user_uuid: Optional[str] = None
    conversation_uuid: Optional[str] = None
