from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    """
    Base class for Document
    """

    text: str
    """Content of the document"""

    url: str
    """URL where the document was found"""

    language: str = None
    """Language of the document text"""

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
    """Organizations to which the document belongs"""

    user_uuid: Optional[str] = None
    """UUID of the user who added the document"""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DocumentCreate(DocumentBase):
    """
    Create class for Document
    """

    text_embedding: Optional[list[float]] = None
    tags_embedding: Optional[list[float]] = None
    subtopics_embedding: Optional[list[float]] = None
    summary_embedding: Optional[list[float]] = None
    hyq_embedding: Optional[list[float]] = None
    hyq_declarative_embedding: Optional[list[float]] = None

    source: str
    """How the document was found, can be a URL or a file path for example"""


class DocumentsCreate(BaseModel):
    """
    Create class for Documents
    """

    objects: list[DocumentCreate]
    """A list of documents to add to the database"""


class DocumentUpdate(DocumentBase):
    """
    Update class for Document
    """

    source_id: Optional[int] = None

    text_embedding: Optional[list[float]] = None
    subtopics_embedding: Optional[list[float]] = None
    tags_embedding: Optional[list[float]] = None
    text_embedding: Optional[list[float]] = None
    summary_embedding: Optional[list[float]] = None
    hyq_embedding: Optional[list[float]] = None
    hyq_declarative_embedding: Optional[list[float]] = None


class Document(DocumentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
