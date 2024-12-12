from typing import List
from pydantic import BaseModel


class TopicCheck(BaseModel):
    on_topic: bool


class FunctionCall(BaseModel):
    function_call: str


class MultipleSourceValidation(BaseModel):
    sources: List[str]
    is_valid: bool


class UniqueSourceValidation(BaseModel):
    is_partial: bool
    is_valid: bool
    reason: str
