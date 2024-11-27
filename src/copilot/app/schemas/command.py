from pydantic import BaseModel


class CommandRequest(BaseModel):
    input_text: str
