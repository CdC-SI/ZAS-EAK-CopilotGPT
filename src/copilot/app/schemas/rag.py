from pydantic import BaseModel


class AgentHandoff(BaseModel):
    agent: str
