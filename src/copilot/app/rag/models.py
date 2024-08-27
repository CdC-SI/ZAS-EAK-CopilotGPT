from pydantic import BaseModel
from typing import List, Optional

class ResponseBody(BaseModel):
    content: str

class RAGRequest(BaseModel):
    query: str

class EmbeddingRequest(BaseModel):
    text: str

class Delta(BaseModel):
    content: Optional[str]

class Choice(BaseModel):
    delta: Delta

class ResponseModel(BaseModel):
    choices: List[Choice]
