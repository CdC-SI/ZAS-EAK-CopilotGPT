from typing import Optional

from pydantic import BaseModel, ConfigDict


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
    language: Optional[str] = None
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


class QuestionItem(QuestionCreate):
    """
    Upsert class for Question in Survey Pipeline
    """
    id: Optional[int] = None


class Source(SourceBase):
    """
    Class for Source
    """
    id: int

    questions: list[QuestionBase] = []
    documents: list[DocumentBase] = []

    class Config:
        from_attributes = True


class Document(DocumentBase):
    """
    Class for Document
    """
    id: int

    class Config:
        from_attributes = True


class Question(QuestionBase):
    """
    Class for ArticleFAQ
    """
    id: int
    answer: DocumentBase

    class Config:
        from_attributes = True
