from pydantic import BaseModel

class EmbeddingRequest(BaseModel):
    text: str
