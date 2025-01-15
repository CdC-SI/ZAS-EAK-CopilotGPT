from typing import Optional, List
from sqlalchemy import (
    Integer,
    ForeignKey,
    String,
    Text,
    DateTime,
    func,
    Index,
    ARRAY,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy.inspection import inspect
from datetime import datetime

# SQLAlchemy-2.0.30

from sqlalchemy.orm import declarative_base


class EmbeddedMixin:

    embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(1536), nullable=True
    )


Base = declarative_base()


class Source(Base):
    """
    Source of the data stored in Document and Question tables. It can be URL, file path, user ID, etc.
    """

    __tablename__ = "source"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("idx_source_url", "url"),)

    def __repr__(self) -> str:
        return f"Source(id={self.id!r}, url={self.url!r})"

    def to_dict(self):
        serialized_data = {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }
        return serialized_data


class Document(Base, EmbeddedMixin):
    """
    Documents used for the RAG
    """

    __tablename__ = "document"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    subtopics: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    hyq: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    hyq_declarative: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    doctype: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("source.id"), nullable=False
    )
    source: Mapped["Source"] = relationship(
        "Source", back_populates="documents"
    )

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index(
            "idx_document_text_tsv",
            "text",
            postgresql_using="gin",
            postgresql_ops={"text": "gin_trgm_ops"},
        ),
        Index(
            "idx_document_embedding", "embedding", postgresql_using="ivfflat"
        ),
        Index("idx_document_language", "language"),
        Index("idx_document_language_tag", "language", "tags"),
        Index("idx_document_language_source_id", "language", "source_id"),
    )

    def __repr__(self) -> str:
        return f"Document(id={self.id!r}, url={self.url!r}, text={self.text!r}, language={self.language!r})"

    def to_dict(self):
        serialized_data = {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }
        if self.source:
            serialized_data["source"] = self.source.to_dict()
        else:
            serialized_data["source"] = None
        return serialized_data


class Question(Base, EmbeddedMixin):
    """
    Question used for Autocomplete, answers are stored in the Document table.
    """

    __tablename__ = "question"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    answer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("document.id"), nullable=False
    )
    answer: Mapped["Document"] = relationship(
        "Document", back_populates="questions"
    )
    source_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("source.id"), nullable=True
    )
    source: Mapped[Optional["Source"]] = relationship(
        "Source", back_populates="questions"
    )

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index(
            "idx_text_gin",
            "text",
            postgresql_using="gin",
            postgresql_ops={"text": "gin_trgm_ops"},
        ),
        Index("idx_question_language", "language"),
        Index("idx_question_tag", "language", "tags"),
    )

    def __repr__(self) -> str:
        return f"Question(id={self.id!r}, url={self.url!r}, question={self.text!r}, answer_id={self.answer_id!r}, language={self.language!r})"

    def to_dict(self):
        """
        Convert the SQLAlchemy model instance to a dictionary
        that only includes serializable fields.
        """
        serialized_data = {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }
        serialized_data["answer"] = (
            self.answer.to_dict() if self.answer else None
        )

        return serialized_data


class Tag(Base):
    """
    Tags used for RAG context docs and user intent detection.
    """

    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    tag_en: Mapped[str] = mapped_column(String, nullable=False, unique=False)
    description_en: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(1536), nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    def to_dict(self):
        serialized_data = {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }
        return serialized_data


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_uuid: Mapped[str] = mapped_column(String)
    conversation_uuid: Mapped[str] = mapped_column(String)
    message_uuid: Mapped[str] = mapped_column(String, unique=True)
    role: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String)
    faq_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    retrieved_docs: Mapped[Optional[List[int]]] = mapped_column(
        ARRAY(Integer), nullable=True
    )


class ChatTitle(Base):
    __tablename__ = "chat_title"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_uuid: Mapped[str] = mapped_column(String)
    conversation_uuid: Mapped[str] = mapped_column(String)
    chat_title: Mapped[str] = mapped_column(String)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class ChatFeedback(Base):
    __tablename__ = "chat_feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_uuid: Mapped[str] = mapped_column(String)
    conversation_uuid: Mapped[str] = mapped_column(String)
    message_uuid: Mapped[str] = mapped_column(
        String, ForeignKey("chat_history.message_uuid")
    )
    score: Mapped[int] = mapped_column(Integer)
    comment: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


# class TokenUsage(Base):
#     __tablename__ = "token_usage"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     user_uuid: Mapped[str] = mapped_column(String)
#     conversation_uuid: Mapped[str] = mapped_column(String)
#     token_count: Mapped[int] = mapped_column(Integer)
#     token_cost: Mapped[float] = mapped_column(Float)
#     timestamp: Mapped[DateTime] = mapped_column(
#         DateTime, default=datetime.utcnow
#     )

# retrieve generations by user_uuid and conversation_uuid from db
# setup API (usage_api?)
# setup enums (see PR) for models, tokenizer and pricing

# Init relationship mappers
Document.questions = relationship(
    "Question", order_by=Question.id, back_populates="answer"
)
Source.questions = relationship(
    "Question", order_by=Question.id, back_populates="source"
)
Source.documents = relationship(
    "Document", order_by=Document.id, back_populates="source"
)
