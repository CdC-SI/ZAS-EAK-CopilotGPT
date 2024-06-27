from typing import List, Optional
from pgvector.sqlalchemy import Vector
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
    q_embedding: Optional[List[float]]


class ArticleFAQ(ArticleFAQBase):
    """
    Class for ArticleFAQ
    """
    id: int
    source_id: Optional[int]
    created_at: datetime
    modified_at: datetime

    class Config:
        orm_mode = True


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
    embedding: Optional[List[float]]


class Document(DocumentBase):
    """
    Class for Document
    """
    id: int
    source_id: int
    created_at: datetime
    modified_at: datetime

    class Config:
        orm_mode = True


class SourceBase(BaseModel):
    """
    Base class for Source
    """
    name: str
    url: str
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
        orm_mode = True
