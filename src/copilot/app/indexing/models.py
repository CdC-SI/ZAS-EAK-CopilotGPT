from pydantic import BaseModel


class FaqItem(BaseModel):
    question: str
    answer: str
    url: str
    language: str
