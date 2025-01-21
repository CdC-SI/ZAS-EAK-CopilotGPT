from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from .document import DocumentBase


class FaqQuestionBase(BaseModel):
    """
    Base class for Question
    """

    text: str
    """Content of the question"""

    url: str
    """URL where the question-answer was found"""

    language: Optional[str] = None
    """Language of the question and answer text"""

    tags: Optional[List[str]] = None
    """Tags of the document text"""

    subtopics: Optional[List[str]] = None
    """Subtopics of the document text"""

    summary: Optional[str] = None
    """Summary of the document text"""

    hyq: Optional[List[str]] = None
    """Hypothetical queries associated to the document text"""

    hyq_declarative: Optional[List[str]] = None
    """Declarative hypothetical queries associated to the document text"""

    doctype: Optional[str] = None
    """Type of the document"""

    organizations: Optional[List[str]] = None
    """Organizations to which the question belongs"""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FaqQuestionCreate(FaqQuestionBase):
    """
    Create class for Question
    """

    answer: str
    """Text of the answer to the question"""

    text_embedding: Optional[list[float]] = None
    answer_embedding: Optional[list[float]] = None
    subtopics_embedding: Optional[list[float]] = None
    tags_embedding: Optional[list[float]] = None
    summary_embedding: Optional[list[float]] = None
    hyq_embedding: Optional[list[float]] = None
    hyq_declarative_embedding: Optional[list[float]] = None

    source: str
    """How the question-answer was found, can be a URL or a file path for example"""


class FaqQuestionsCreate(BaseModel):
    """
    Create class for Question
    """

    objects: list[FaqQuestionCreate]
    """A list of questions to add to the database"""


class FaqQuestionItem(FaqQuestionCreate):
    """
    Upsert class for Question in Survey Pipeline
    """

    id: Optional[int] = None
    source: Optional[str] = None


class FaqQuestionUpdate(FaqQuestionBase):
    """
    Update class for Question
    """

    source_id: Optional[int] = None
    text_embedding: Optional[list[float]] = None
    subtopics_embedding: Optional[list[float]] = None
    tags_embedding: Optional[list[float]] = None
    text_embedding: Optional[list[float]] = None
    summary_embedding: Optional[list[float]] = None
    hyq_embedding: Optional[list[float]] = None
    hyq_declarative_embedding: Optional[list[float]] = None


class FaqQuestion(FaqQuestionBase):
    id: int

    answer: DocumentBase
    """Related answer from Document table"""

    model_config = ConfigDict(from_attributes=True)
