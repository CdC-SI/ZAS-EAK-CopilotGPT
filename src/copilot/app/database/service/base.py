from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from ..models import Base, TextEmbeddingMixin, EmbeddableField
from pydantic import BaseModel

from utils.embedding import get_embedding

from abc import ABCMeta, abstractmethod
from typing import Type

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BaseService(metaclass=ABCMeta):
    """
    Base class for database services

    Parameters
    ----------
    model
        Database model
    """

    def __init__(self, model=Type[Base]):
        self.model = model

    def _create(self, db: Session, obj_in):
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        return db_obj

    def create(self, db: Session, obj_in: BaseModel):
        """
        Create a new object in the database

        Parameters
        ----------
        db : Session
            Database session
        obj_in
            Pydantic schema

        Returns
        -------
        Base
            Database object
        """
        db_obj = self._create(db, obj_in)
        db.commit()
        return db_obj

    def create_all(self, db: Session, objs_in: BaseModel):
        """
        Create multiple objects in the database

        Parameters
        ----------
        db: Session
            Database session
        objs_in
            Pydantic schema with list of objects to create

        Returns
        -------
        list[Base]
            List of database objects
        """
        db_objs = []
        for obj_in in objs_in.objects:
            db_objs.append(self._create(db, obj_in))
        db.commit()
        return db_objs

    def get(self, db: Session, id_: int):
        """
        Get an object by id

        Parameters
        ----------
        db: Session
            Database session
        id_: int
            Object id

        Returns
        -------
        Base
            Database object
        """
        stmt = select(self.model).filter(self.model.id == id_)
        return db.execute(stmt).scalar_one()

    def update(self, db: Session, db_obj: Base, obj_in: BaseModel):
        """
        Update a database object

        Parameters
        ----------
        db : Session
            Database session
        db_obj : Base
            Database object
        obj_in : BaseModel
            Pydantic schema

        Returns
        -------
        Base
            Updated database object
        """
        db_obj = self._update(db, db_obj, obj_in)
        db.commit()
        return db_obj

    def _update(self, db: Session, db_obj: Base, obj_in: BaseModel):
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        return db_obj

    def _delete(self, db: Session, id_: int):
        db_obj = self.get(db, id_)
        db.delete(db_obj)
        return db_obj

    def delete(self, db: Session, id_: int):
        """
        Delete an object by id

        Parameters
        ----------
        db : Session
            Database session
        id_ : int
            Object id

        Returns
        -------
        Base
            Deleted database object
        """
        db_obj = self._delete(db, id_)
        db.commit()
        return db_obj

    def delete_all(self, db: Session, ids: list[int]):
        """
        Delete multiple objects by id

        Parameters
        ----------
        db : Session
            Database session
        ids : list[int]
            List of object ids

        Returns
        -------
        list[Base]
            List of deleted database objects
        """
        db_objs = []
        for id_ in ids:
            db_objs.append(self._delete(db, id_))
        db.commit()
        return db_objs


class EmbeddingService(BaseService):
    """
    Base class for embedding services
    """

    async def _embed_field(
        self, db_obj: TextEmbeddingMixin, field: EmbeddableField
    ) -> bool:
        """
        Embed a single field if it exists and has content.
        Returns True if embedding was performed, False otherwise.
        """
        content = getattr(db_obj, field.content_field, None)
        if content:
            if isinstance(content, list):
                # For fields like tags, hyq that are lists, join them
                content = " ".join(content)
            if isinstance(content, str) and content.strip():
                embedding = await get_embedding(content)
                setattr(db_obj, field.embedding_field, embedding)
                return True
        return False

    async def _embed(self, db_obj: TextEmbeddingMixin) -> TextEmbeddingMixin:
        """Embed all available fields in the object"""
        embedded_count = 0
        for field in db_obj.embeddable_fields.values():
            if await self._embed_field(db_obj, field):
                embedded_count += 1
                logger.info(
                    f"Embedded field {field.content_field} for {db_obj}"
                )

        if embedded_count == 0:
            logger.warning(f"No fields were embedded for {db_obj}")

        return db_obj

    async def embed_one(self, db: Session, db_obj: TextEmbeddingMixin):
        """
        Embed a single object in the database

        Parameters
        ----------
        db : Session
            Database session
        db_obj : TextEmbeddingMixin
            Database object

        Returns
        -------
        TextEmbeddingMixin
            Embedded database object
        """
        db_obj = await self._embed(db_obj)
        db.commit()
        return db_obj

    async def embed_many(
        self, db: Session, embed_empty_only: bool = True, k: int = 0
    ):
        """
        Embed multiple objects in the database

        Parameters
        ----------
        db : Session
            Database session
        embed_empty_only : bool, optional
            Whether to embed only objects with empty embeddings (set to None) or all objects without distinction, default to True
        k : int, optional
            Number of objects to embed, with 0 meaning all objects, default to 0

        Returns
        -------
        list[TextEmbeddingMixin]
            List of embedded database objects
        """
        stmt = select(self.model)
        if embed_empty_only:
            # Create a filter that checks if any embedding field is null
            null_conditions = [
                getattr(self.model, field.embedding_field).is_(None)
                for field in self.model.embeddable_fields.values()
            ]
            stmt = stmt.filter(or_(*null_conditions))

        db_objs = db.scalars(stmt).all()
        logger.info(f"Embedding {len(db_objs)} objects")

        for i, db_obj in enumerate(db_objs, 1):
            await self._embed(db_obj)
            if k > 0 and i >= k:
                break

        db.commit()
        return db_objs

    @abstractmethod
    async def _create(self, db: Session, obj_in: BaseModel, embed=False):
        pass

    async def create(self, db: Session, obj_in: BaseModel, embed=False):
        db_obj = await self._create(db, obj_in, embed=embed)
        db.commit()
        return db_obj

    def create_all(self, db: Session, objs_in: BaseModel, embed=False):
        """
        Create multiple objects in the database

        Parameters
        ----------
        db : Session
            Database session
        objs_in : BaseModel
            Pydantic schema with list of objects to create
        embed : bool, optional
            Whether to embed the objects to create, default to False

        Returns
        -------
        list[Base]
            List of database objects
        """
        db_objs = []
        for obj_in in objs_in.objects:
            db_objs.append(self._create(db, obj_in, embed=embed))
        db.commit()
        return db_objs

    def get_by_text(self, db: Session, text: str):
        """
        Get object by text

        Parameters
        ----------
        db : Session
            Database session
        text : str
            Object text

        Returns
        -------
        Base
            Database object
        """
        return db.query(self.model).filter(self.model.text == text).first()

    # TO DO: update this
    def get_by_tag(self, db: Session, tag: str):
        """
        Get object by tag

        Parameters
        ----------
        db : Session
            Database session
        tag : str
            Object text

        Returns
        -------
        Base
            Database object
        """
        return db.query(self.model).filter(self.model.tag_en == tag).first()

    async def _update(self, db: Session, db_obj, obj_in, embed=False):
        exclude = await self._update_embed_exclude(db_obj, obj_in, embed=embed)
        obj_data = obj_in.model_dump(exclude_unset=True, exclude=exclude)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        return db_obj

    async def _update_embed_exclude(self, db_obj, obj_in, embed=False):
        """
        Return fields to exclude when updating an object

        Parameters
        ----------
        db_obj
            Database object
        obj_in
            Pydantic schema
        embed
            Whether to embed the object

        Returns
        -------
        set[str]
            fields to exclude
        """
        exclude = {"source"}

        if embed:
            changed_fields = []
            for field_name, field in db_obj.embeddable_fields.items():
                old_content = getattr(db_obj, field.content_field, None)
                new_content = getattr(obj_in, field.content_field, None)
                new_embedding = getattr(obj_in, field.embedding_field, None)

                if new_embedding is None:
                    exclude.add(field.embedding_field)
                    if (
                        new_content != old_content
                        or getattr(db_obj, field.embedding_field, None) is None
                    ):
                        changed_fields.append(field)

            if changed_fields:
                logger.info(
                    f"Fields to be embedded: {[f.content_field for f in changed_fields]}"
                )
                for field in changed_fields:
                    await self._embed_field(db_obj, field)

        logger.info(f"Excluded fields: {exclude}")
        return exclude

    async def update(
        self, db: Session, db_obj, obj_in: BaseModel, embed=False
    ):
        """
        Update db object

        Parameters
        ----------
        db : Session
            Database session
        db_obj
            Database object
        obj_in : BaseModel
            Pydantic schema
        embed : bool, optional
            Whether to embed the object to update, default to False

        Returns
        -------
        Base
            Updated database object
        """
        # return await self._update(db, db_obj, obj_in, embed=embed)
        try:
            db_obj = await self._update(db, db_obj, obj_in, embed=embed)
            db.commit()
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Update failed due to {e}")
            raise

    # TO DO: update this
    async def upsert(self, db: Session, obj_in: BaseModel, embed=False):
        if hasattr(obj_in, "text"):
            db_obj = self.get_by_text(db, obj_in.text)
        elif hasattr(obj_in, "tag_en"):
            db_obj = self.get_by_tag(db, obj_in.tag_en)
        else:
            db_obj = None

        if db_obj and hasattr(obj_in, "text"):
            db_obj = await self._update(
                db, db_obj, obj_in, embed=embed
            )  # update for duplicate docs
        elif db_obj and hasattr(obj_in, "tag_en"):
            db_obj = await self._create(
                db, obj_in, embed=embed
            )  # create for duplicate tags (normal)
        else:
            db_obj = await self._create(db, obj_in, embed=embed)

        db.commit()
        return db_obj
