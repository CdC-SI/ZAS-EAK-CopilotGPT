from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class SourceBase(BaseModel):
    """
    Base class for Source
    """
    url: str


class DocumentBase(BaseModel):
    """
    Base class for Document
    """
    language: Optional[str] = None
    text: str
    url: str

    class Config:
        arbitrary_types_allowed = True


class QuestionBase(BaseModel):
    """
    Base class for QuestionBase
    """
    text: str
    url: str

    class Config:
        arbitrary_types_allowed = True


class SourceCreate(SourceBase):
    """
    Create class for Source
    """
    pass


class DocumentCreate(DocumentBase):
    """
    Create class for Document
    """
    embedding: Optional[list[float]] = None
    source: str


class DocumentsCreate(BaseModel):
    """
    Create class for Documents
    """
    objects: list[DocumentCreate]


class QuestionCreate(QuestionBase):
    """
    Create class for ArticleFAQ
    """
    language: Optional[str] = None
    answer: str
    embedding: Optional[list[float]] = None
    source: str


class QuestionsCreate(BaseModel):
    """
    Create class for ArticlesFAQ
    """
    objects: list[QuestionCreate]


class DocumentUpdate(DocumentBase):
    """
    Update class for Document
    """
    source_id: Optional[int] = None
    embedding: Optional[list[float]] = None


class QuestionUpdate(QuestionBase):
    """
    Update class for Document
    """
    source_id: Optional[int] = None
    embedding: Optional[list[float]] = None


class QuestionItem(QuestionBase):
    """
    Upsert class for Question in Survey Pipeline
    """
    id: Optional[int] = None
    language: Optional[str] = None
    answer: str


class Source(SourceBase):
    """
    Class for Source
    """
    id: int

    questions: list[QuestionBase] = []
    documents: list[DocumentBase] = []

    class Config:
        from_orm = True


class Document(DocumentBase):
    """
    Class for Document
    """
    id: int
    source: SourceBase

    class Config:
        from_orm = True


class Question(QuestionBase):
    """
    Class for ArticleFAQ
    """
    id: int
    answer: DocumentBase
    source: SourceBase

    class Config:
        from_orm = True
