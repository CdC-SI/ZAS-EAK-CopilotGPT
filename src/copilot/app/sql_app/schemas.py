from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class ArticleFAQBase(BaseModel):
    """
    Base class for ArticleFAQ
    """
    url: str
    question: str
    answer: str
    language: str

    class Config:
        arbitrary_types_allowed = True


class ArticleFAQCreate(ArticleFAQBase):
    """
    Create class for ArticleFAQ
    """
    q_embedding: Optional[List[float]] = None


class ArticlesFAQCreate(BaseModel):
    """
    Create class for ArticlesFAQ
    """
    articlesFAQ: List[ArticleFAQCreate]


class ArticleFAQ(ArticleFAQBase):
    """
    Class for ArticleFAQ
    """
    id: int
    source_id: Optional[int]
    created_at: datetime
    modified_at: datetime

    class Config:
        from_orm = True


class DocumentBase(BaseModel):
    """
    Base class for Document
    """
    text: str
    url: str

    class Config:
        arbitrary_types_allowed = True


class DocumentCreate(DocumentBase):
    """
    Create class for Document
    """
    embedding: Optional[List[float]] = None


class DocumentsCreate(BaseModel):
    """
    Create class for Documents
    """
    documents: List[DocumentCreate]


class Document(DocumentBase):
    """
    Class for Document
    """
    id: int
    source_id: int
    created_at: datetime
    modified_at: datetime

    class Config:
        from_orm = True


class SourceBase(BaseModel):
    """
    Base class for Source
    """
    sitemap_url: str


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
    articlesFAQ: List[ArticleFAQ] = []
    documents: List[Document] = []

    class Config:
        from_orm = True
