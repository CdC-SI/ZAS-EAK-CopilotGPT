from pydantic import BaseModel


class FunctionCall(BaseModel):
    function_call: str
