from typing import Optional

from pydantic import BaseModel, ConfigDict

from .document import DocumentBase


class QuestionBase(BaseModel):
    """
    Base class for Question
    """

    language: Optional[str] = None
    """Language of the question and answer text"""

    tags: Optional[str] = None
    """Tags of the document text"""

    text: str
    """Content of the question"""

    url: str
    """URL where the question-answer was found"""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class QuestionCreate(QuestionBase):
    """
    Create class for Question
    """

    answer: str
    """Text of the answer to the question"""

    embedding: Optional[list[float]] = None

    source: str
    """How the question-answer was found, can be a URL or a file path for example"""


class QuestionsCreate(BaseModel):
    """
    Create class for Question
    """

    objects: list[QuestionCreate]
    """A list of questions to add to the database"""


class QuestionItem(QuestionCreate):
    """
    Upsert class for Question in Survey Pipeline
    """

    id: Optional[int] = None
    source: Optional[str] = None


class QuestionUpdate(QuestionBase):
    """
    Update class for Question
    """

    source_id: Optional[int] = None
    embedding: Optional[list[float]] = None


class Question(QuestionBase):
    id: int

    answer: DocumentBase
    """Related answer from Document table"""

    model_config = ConfigDict(from_attributes=True)
