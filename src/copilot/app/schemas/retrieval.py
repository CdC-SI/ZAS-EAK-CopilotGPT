from typing import List
from pydantic import BaseModel


class QueryReformulation(BaseModel):
    reformulations: List[str]
