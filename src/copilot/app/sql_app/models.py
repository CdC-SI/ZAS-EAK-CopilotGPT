from typing import List
from sqlalchemy import Integer, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
# SQLAlchemy-2.0.30

from .database import Base


class ArticleFAQ(Base):
    __tablename__ = "data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(Text, unique=True,)
    question: Mapped[str] = mapped_column(Text, unique=True)
    q_embedding: Mapped[Vector] = mapped_column(Vector(1536), nullable=True)
    answer: Mapped[str] = mapped_column(Text)
    language: Mapped[int] = mapped_column(String(3), nullable=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id"), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"ArticleFAQ(id={self.id!r}, name={self.url!r}, question={self.question!r}, answer={self.answer!r}, language={self.language!r}, source_id={self.source_id!r})"


class Document(Base):
    __tablename__ = "embeddings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    embedding: Mapped[Vector] = mapped_column(Vector(1536), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, unique=True)
    language: Mapped[int] = mapped_column(String(3), nullable=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"Document(id={self.id!r}, url={self.url!r}, text={self.text!r})"


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sitemap_url: Mapped[str] = mapped_column(String)
    articlesFAQ: Mapped[List["ArticleFAQ"]] = relationship("ArticleFAQ", order_by=ArticleFAQ.id, back_populates="source")
    documents: Mapped[List["Document"]] = relationship("Document", order_by=Document.id, back_populates="source")

    def __repr__(self) -> str:
        return f"Source(id={self.id!r}, name={self.name!r}, url={self.url!r}, sitemap_url={self.sitemap_url!r})"


# Init relationship mappers
ArticleFAQ.source = relationship("Source", back_populates="articlesFAQ")
Document.source = relationship("Source", back_populates="documents")
