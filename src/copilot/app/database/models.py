from typing import Optional
from sqlalchemy import Integer, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
# SQLAlchemy-2.0.30

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    embedding: Mapped[Vector] = mapped_column(Vector(1536))
    language: Mapped[Optional[str]] = mapped_column(String(3))

    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id"))

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"Document(id={self.id!r}, url={self.url!r}, text={self.text!r}, language={self.language!r})"


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    embedding: Mapped[Optional[Vector]] = mapped_column(Vector(1536))
    answer_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id"), nullable=False)
    answer: Mapped["Document"] = relationship("Document", back_populates="question")
    language: Mapped[Optional[str]] = mapped_column(String(3))

    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sources.id"))

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"Question(id={self.id!r}, url={self.url!r}, question={self.text!r}, answer_id={self.answer_id!r}, language={self.language!r})"


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    questions: Mapped[list["Question"]] = relationship("Question", order_by=Question.id, back_populates="source")
    documents: Mapped[list["Document"]] = relationship("Document", order_by=Document.id, back_populates="source")

    def __repr__(self) -> str:
        return f"Source(id={self.id!r}, url={self.url!r})"


# Init relationship mappers
Document.question = relationship("Question", back_populates="answer")
Document.source = relationship("Source", back_populates="documents")
Question.source = relationship("Source", back_populates="questions")
