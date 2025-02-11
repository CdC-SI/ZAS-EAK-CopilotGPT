from typing import Optional, List, ClassVar, Dict
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
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from pgvector.sqlalchemy import Vector
from sqlalchemy.inspection import inspect
from datetime import datetime

# SQLAlchemy-2.0.30

from sqlalchemy.orm import declarative_base


class EmbeddableField:
    """Represents a field that can be embedded with its corresponding embedding field."""

    def __init__(self, content_field: str, embedding_field: str):
        self.content_field = content_field
        self.embedding_field = embedding_field


class TextEmbeddingMixin:
    """Base mixin for text embeddings"""

    embeddable_fields: ClassVar[Dict[str, EmbeddableField]] = {
        "text": EmbeddableField("text", "text_embedding")
    }

    text_embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(1536), nullable=True
    )


class DocumentEmbeddingMixin(TextEmbeddingMixin):
    """Extended mixin for Document-specific embeddings"""

    embeddable_fields: ClassVar[Dict[str, EmbeddableField]] = {
        "text": EmbeddableField("text", "text_embedding"),
        "tags": EmbeddableField("tags", "tags_embedding"),
        "subtopics": EmbeddableField("subtopics", "subtopics_embedding"),
        "summary": EmbeddableField("summary", "summary_embedding"),
        "hyq": EmbeddableField("hyq", "hyq_embedding"),
        "hyq_declarative": EmbeddableField(
            "hyq_declarative", "hyq_declarative_embedding"
        ),
    }

    tags_embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(1536), nullable=True
    )
    subtopics_embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(1536), nullable=True
    )
    summary_embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(1536), nullable=True
    )
    hyq_embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(1536), nullable=True
    )
    hyq_declarative_embedding: Mapped[Optional[Vector]] = mapped_column(
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


class BaseContentModel(Base):
    """
    Abstract base model for content-based models with common fields and behavior.
    Not meant to be instantiated directly.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    subtopics: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    # keywords: Mapped[Optional[List[str]]] = mapped_column(
    #    ARRAY(String), nullable=True
    # )
    hyq: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    hyq_declarative: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    organizations: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
    doctype: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("source.id"), nullable=False
    )

    @declared_attr
    def source(cls) -> Mapped["Source"]:
        return relationship("Source")

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    modified_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    def to_dict(self) -> dict:
        """Convert model instance to dictionary with serializable fields."""
        serialized_data = {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }
        if self.source:
            serialized_data["source"] = self.source.to_dict()
        return serialized_data


class Document(BaseContentModel, DocumentEmbeddingMixin):
    """Documents used for RAG system."""

    __tablename__ = "document"

    user_uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source: Mapped["Source"] = relationship(
        "Source", back_populates="documents", overlaps="source"
    )

    __table_args__ = (
        # Text search optimizations
        Index(
            "idx_document_text_gin",
            "text",
            postgresql_using="gin",
            postgresql_ops={"text": "gin_trgm_ops"},
        ),
        # Common filter combinations
        Index("idx_document_language", "language"),
        Index("idx_document_tags", "tags", postgresql_using="gin"),
        Index(
            "idx_document_organizations",
            "organizations",
            postgresql_using="gin",
        ),
        # Vector search optimizations - IVFFlat with different list sizes based on expected data size
        Index(
            "idx_document_text_embedding",
            "text_embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
        ),
        Index(
            "idx_document_tags_embedding",
            "tags_embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 50},
        ),
        Index(
            "idx_document_subtopics_embedding",
            "subtopics_embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 50},
        ),
        # Combined indexes for common query patterns
        Index(
            "idx_document_language_user",
            "language",
            "user_uuid",
            postgresql_using="btree",
        ),
    )

    def __repr__(self) -> str:
        return f"Document(id={self.id!r}, url={self.url!r}, text={self.text!r}, language={self.language!r})"


class Question(BaseContentModel, DocumentEmbeddingMixin):
    """Questions for FAQ system, with answers stored in Document table."""

    __tablename__ = "question"

    answer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("document.id"), nullable=False
    )
    answer: Mapped["Document"] = relationship(
        "Document", back_populates="questions"
    )
    source: Mapped["Source"] = relationship(
        "Source", back_populates="questions", overlaps="source"
    )

    user_uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    __table_args__ = (
        # Text search optimizations
        Index(
            "idx_question_text_gin",
            "text",
            postgresql_using="gin",
            postgresql_ops={"text": "gin_trgm_ops"},
        ),
        # Common filter combinations
        Index("idx_question_language", "language"),
        Index("idx_question_tags", "tags", postgresql_using="gin"),
        # Vector search optimizations
        Index(
            "idx_question_text_embedding",
            "text_embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
        ),
        # Answer relationship optimization
        Index("idx_question_answer", "answer_id"),
    )

    def __repr__(self) -> str:
        return f"Question(id={self.id!r}, url={self.url!r}, question={self.text!r}, language={self.language!r}, answer_id={self.answer_id!r})"

    def to_dict(self) -> dict:
        """Extends base to_dict with answer data."""
        data = super().to_dict()
        data["answer"] = self.answer.to_dict() if self.answer else None
        return data


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


class Intentions(Base):
    __tablename__ = "intentions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=False)


class IntentDescriptions(Base):
    __tablename__ = "intent_descriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    intention_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("intentions.id", ondelete="CASCADE"),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String)


class Workflows(Base):
    __tablename__ = "workflows"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_uuid: Mapped[str] = mapped_column(String)
    conversation_uuid: Mapped[str] = mapped_column(String)
    message_uuid: Mapped[str] = mapped_column(String, unique=True)
    role: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    language: Mapped[str] = mapped_column(String)
    faq_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sources: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )
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
        String, ForeignKey("chat_history.message_uuid", ondelete="CASCADE")
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
