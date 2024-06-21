from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
# SQLAlchemy-2.0.30


class Base(DeclarativeBase):
    pass


class ArticleFAQ(Base):
    __tablename__ = "data"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(256))
    question: Mapped[str] = mapped_column(String(256))
    q_embedding: Mapped[Vector] = mapped_column(Vector(1536))
    answer: Mapped[str] = mapped_column(String(1024))
    language: Mapped[str] = mapped_column(String(3))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    source: Mapped["Source"] = relationship(back_populates="articlesFAQ")
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"Article(id={self.id!r}, name={self.url!r}, question={self.question!r}, answer={self.answer!r}, language={self.language!r})"


class Document(Base):
    __tablename__ = "embeddings"
    id: Mapped[int] = mapped_column(primary_key=True)
    embedding: Mapped[Vector] = mapped_column(Vector(1536))
    text: Mapped[str] = mapped_column(String(1024))
    url: Mapped[str] = mapped_column(String(256))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    source: Mapped["Source"] = relationship(back_populates="documents")
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, url={self.url!r}, text={self.text!r})"


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    url: Mapped[str] = mapped_column(String(256))
    sitemap_url: Mapped[str] = mapped_column(String(256))
    articlesFAQ: Mapped[List["ArticleFAQ"]] = relationship(back_populates="source")
    documents: Mapped[List["Document"]] = relationship(back_populates="source")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, name={self.name!r}, url={self.url!r}, sitemap_url={self.sitemap_url!r})"


# Do we need a table for languages?
