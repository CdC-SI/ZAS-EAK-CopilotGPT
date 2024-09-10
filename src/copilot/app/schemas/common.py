from typing import Optional

from pydantic import BaseModel, ConfigDict


class RAGRequest(BaseModel):
    """
    Class for RAG request
    """
    query: str
    """The query to process"""

    language: Optional[str] = None
    """The language of the query"""

    tag: Optional[str] = None
    """The tag of the query"""
