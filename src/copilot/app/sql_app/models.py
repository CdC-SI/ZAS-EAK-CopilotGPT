from sqlalchemy import Integer, List, ForeignKey, String, Text, DateTime, func
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
    language: Mapped[str] = mapped_column(String(3))
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id"))
    source: Mapped["Source"] = relationship("Source", back_populates="articlesFAQ")
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"ArticleFAQ(id={self.id!r}, name={self.url!r}, question={self.question!r}, answer={self.answer!r}, language={self.language!r})"


class Document(Base):
    __tablename__ = "embeddings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    embedding: Mapped[Vector] = mapped_column(Vector(1536))
    text: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, unique=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id"))
    source: Mapped["Source"] = relationship("Source", back_populates="documents")
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"Document(id={self.id!r}, url={self.url!r}, text={self.text!r})"


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    url: Mapped[str] = mapped_column(String, unique=True)
    sitemap_url: Mapped[str] = mapped_column(String)
    articlesFAQ: Mapped[List["ArticleFAQ"]] = relationship("ArticleFAQ", order_by=ArticleFAQ.id, back_populates="source")
    documents: Mapped[List["Document"]] = relationship("Document", order_by=Document.id, back_populates="source")

    def __repr__(self) -> str:
        return f"Source(id={self.id!r}, name={self.name!r}, url={self.url!r}, sitemap_url={self.sitemap_url!r})"


class Language(Base):
    __tablename__ = "languages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    code: Mapped[str] = mapped_column(String(3), unique=True)
    articlesFAQ: Mapped[List["ArticleFAQ"]] = relationship("ArticleFAQ", order_by=ArticleFAQ.id, back_populates="source")
    documents: Mapped[List["Document"]] = relationship("Document", order_by=Document.id, back_populates="source")

    def __repr__(self) -> str:
        return f"Language(id={self.id!r}, name={self.name!r}, code={self.code!r})"
