from pydantic import BaseModel
from typing import Optional


class FaqItem(BaseModel):
    id: Optional[int] = None
    question: str
    answer: str
    url: str
    language: str
