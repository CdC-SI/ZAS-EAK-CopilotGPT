from .document import DocumentBase
from .question import QuestionBase

from pydantic import BaseModel


class SourceBase(BaseModel):
    """
    Base class for Source
    """
    url: str
    """Not necessarily a URL, but a string that identifies the source. Can be a pathfile or a user ID for example."""


class SourceCreate(SourceBase):
    """
    Create class for Source
    """
    pass


class Source(SourceBase):
    """
    Class for Source
    """
    id: int

    questions: list[QuestionBase] = []
    """A list of questions from this source"""

    documents: list[DocumentBase] = []
    """A list of documents from this source"""

    class Config:
        from_attributes = True
