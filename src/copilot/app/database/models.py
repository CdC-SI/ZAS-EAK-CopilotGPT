from typing import Optional, List
from sqlalchemy import Integer, ForeignKey, String, Text, DateTime, func, Index, desc, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy.inspection import inspect
from datetime import datetime
# SQLAlchemy-2.0.30

from sqlalchemy.orm import declarative_base

class EmbeddedMixin (object):
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[Vector]] = mapped_column(Vector(1536), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    tag: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    url: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('text_tsv', 'text', postgresql_using='gin'),
    )

Base = declarative_base()

class Source(Base):
    """
    Source of the data stored in Document and Question tables. It can be URL, file path, user ID, etc.
    """

    __tablename__ = "source"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"Source(id={self.id!r}, url={self.url!r})"

class Document(Base, EmbeddedMixin):
    """
    Documents used for the RAG
    """

    __tablename__ = "document"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("source.id"), nullable=True)
    source: Mapped[Optional["Source"]] = relationship("Source", back_populates="documents")

    __table_args__ = (
        Index('text_tsv', 'text', postgresql_using='gin', postgresql_ops={'text': 'gin_trgm_ops'}),
    )

    def __repr__(self) -> str:
        return f"Document(id={self.id!r}, url={self.url!r}, text={self.text!r}, language={self.language!r})"

    def to_dict(self):
        """
        Convert the SQLAlchemy model instance to a dictionary
        that only includes serializable fields.
        """
        serialized_data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

        return serialized_data

class Question(Base, EmbeddedMixin):
    """
    Question used for Autocomplete, answers are stored in the Document table.
    """

    __tablename__ = "question"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    answer_id: Mapped[int] = mapped_column(Integer, ForeignKey("document.id"), nullable=False)
    answer: Mapped["Document"] = relationship("Document", back_populates="questions")

    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("source.id"), nullable=True)
    source: Mapped[Optional["Source"]] = relationship("Source", back_populates="questions")

    __table_args__ = (
        Index('idx_text_gin', 'text', postgresql_using='gin', postgresql_ops={'text': 'gin_trgm_ops'}),
    )

    def __repr__(self) -> str:
        return f"Question(id={self.id!r}, url={self.url!r}, question={self.text!r}, answer_id={self.answer_id!r}, language={self.language!r})"

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_uuid: Mapped[str] = mapped_column(String)
    conversation_uuid: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    retrieved_docs: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer), nullable=True)

class ChatTitle(Base):
    __tablename__ = "chat_title"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_uuid: Mapped[str] = mapped_column(String)
    conversation_uuid: Mapped[str] = mapped_column(String)
    chat_title: Mapped[str] = mapped_column(String)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)

# Init relationship mappers
Document.questions = relationship("Question", order_by=Question.id, back_populates="answer")
Source.questions = relationship("Question", order_by=Question.id, back_populates="source")
Source.documents = relationship("Document", order_by=Document.id, back_populates="source")
