from pydantic import BaseModel

class ResponseBody(BaseModel):
    content: str
