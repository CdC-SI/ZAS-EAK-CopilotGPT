from pydantic import BaseModel


class FaqItem(BaseModel):
    id: int
    question: str
    answer: str
    url: str
    language: str
