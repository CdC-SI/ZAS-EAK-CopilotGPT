from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class DocumentBase(BaseModel):
    """
    Base class for Document
    """
    language: Optional[str] = None
    text: str
    url: str
    source_id: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True


class DocumentUpdate(DocumentBase):
    """
    Update class for Document
    """
    pass


class DocumentCreate(DocumentBase):
    """
    Create class for Document
    """
    source: str
    pass


class DocumentsCreate(BaseModel):
    """
    Create class for Documents
    """
    objects: list[DocumentCreate]
    source: Optional[str] = None


class Document(DocumentBase):
    """
    Class for Document
    """
    id: int
    embedding: Optional[list[float]] = None

    created_at: datetime
    modified_at: datetime

    class Config:
        from_orm = True


class QuestionBase(BaseModel):
    """
    Base class for QuestionBase
    """
    language: Optional[str] = None
    text: str
    url: str

    class Config:
        arbitrary_types_allowed = True


class QuestionCreate(QuestionBase):
    """
    Create class for ArticleFAQ
    """
    answer: str
    source: str


class QuestionsCreate(BaseModel):
    """
    Create class for ArticlesFAQ
    """
    objects: list[QuestionCreate]
    source: Optional[str] = None


class Question(QuestionBase):
    """
    Class for ArticleFAQ
    """
    id: int
    answer_id: int
    source_id: Optional[int] = None
    embedding: Optional[list[float]] = None

    created_at: datetime
    modified_at: datetime

    class Config:
        from_orm = True


class SourceBase(BaseModel):
    """
    Base class for Source
    """
    url: str


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

    questions: list[Question] = []
    documents: list[Document] = []

    class Config:
        from_orm = True
