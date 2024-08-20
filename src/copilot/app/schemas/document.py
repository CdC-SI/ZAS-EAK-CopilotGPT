from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    """
    Base class for Document
    """
    language: Optional[str] = None
    """Language of the document text"""

    tag: Optional[str] = None
    """Tag of the document text"""

    text: str
    """Content of the document"""

    url: str
    """URL where the document was found"""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DocumentCreate(DocumentBase):
    """
    Create class for Document
    """
    embedding: Optional[list[float]] = None

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

    embedding: Optional[list[float]] = None


class Document(DocumentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


