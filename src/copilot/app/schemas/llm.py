from pydantic import BaseModel
from typing import List, Optional


class Delta(BaseModel):
    content: Optional[str]


class Message(BaseModel):
    content: str


class Choice(BaseModel):
    delta: Optional[Delta] = None
    message: Optional[Message] = None


class ResponseModel(BaseModel):
    choices: List[Choice]


class TopicCheck(BaseModel):
    on_topic: bool
