from typing import Optional
from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    """
    Base class for Tag
    """

    tag_en: str = None
    """Content of the english tag"""

    description_en: str = None
    """English description of the tag"""

    description: str = None
    """Description of the tag"""

    language: str = None
    """Language of the tag"""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class TagCreate(TagBase):
    """
    Create class for Tag
    """

    embedding: Optional[list[float]] = None

    # source: str
    """How the tag was found, can be a URL or a file path for example"""


class TagsCreate(BaseModel):
    """
    Create class for Tags
    """

    objects: list[TagCreate]
    """A list of tags to add to the database"""


class TagUpdate(TagBase):
    """
    Update class for Tag
    """

    embedding: Optional[list[float]] = None
