from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Base, EmbeddedMixin
from pydantic import BaseModel

from utils.embedding import get_embedding

from abc import ABCMeta, abstractmethod
from typing import Type

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        Get object by id

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
        Update db object

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
        Delete object by id

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

    def _embedding(self, db_obj: EmbeddedMixin, text: str):
        db_obj.embedding = get_embedding(text)
        return db_obj

    def _embed(self, db_obj: EmbeddedMixin):
        return self._embedding(db_obj, db_obj.text)

    def embed_one(self, db: Session, db_obj: EmbeddedMixin):
        """
        Embed a single object in the database

        Parameters
        ----------
        db : Session
            Database session
        db_obj : EmbeddedMixin
            Database object

        Returns
        -------
        EmbeddedMixin
            Embedded database object
        """
        db_obj = self._embed(db_obj)
        db.commit()
        return db_obj

    def embed_many(self, db: Session, embed_empty_only: bool = True, k: int = 0):
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
        list[EmbeddedMixin]
            List of embedded database objects
        """
        stmt = select(self.model)
        if embed_empty_only:
            stmt = stmt.filter(self.model.embedding.is_(None))
        db_objs = db.scalars(stmt).all()
        logger.info(f'Embedding {len(db_objs)} objects')
        i = 0
        for db_obj in db_objs:
            i += 1
            self._embed(db_obj)
            logger.info(f'Embedded: {db_obj}')
            if i == k:
                break
        db.commit()
        return db_objs

    @abstractmethod
    def _create(self, db: Session, obj_in: BaseModel, embed=False):
        pass

    def create(self, db: Session, obj_in: BaseModel, embed=False):
        db_obj = self._create(db, obj_in, embed=embed)
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
        return db.query(self.model).filter(self.model.text == text).one_or_none()

    def _update(self, db: Session, db_obj, obj_in, embed=False):
        super()._update(db, db_obj, obj_in)

    def _update_embed_exclude(self, db_obj, obj_in, embed=False):
        exclude = {'source'}
        # prevent from replacing existing embedding by None
        if obj_in.embedding is None:
            exclude.add('embedding')

            # specified embedding from obj_in has priority on requesting a new one
            # embed only if the text has changed
            if embed and ((db_obj.text != obj_in.text) or (db_obj.embedding is None)):
                logger.info(f'Embedding updated')
                self._embedding(db_obj, obj_in.text)
            else:
                logger.info(f'Embedding not updated')

        logger.info(f'Excluded fields: {exclude}')
        return exclude

    def update(self, db: Session, db_obj, obj_in: BaseModel, embed=False):
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
        return self._update(db, db_obj, obj_in, embed=embed)

    def upsert(self, db: Session, obj_in: BaseModel, embed=False):
        """
        Upsert object in the database

        Parameters
        ----------
        db : Session
            Database session
        obj_in : BaseModel
            Pydantic schema
        embed : bool, optional
            Whether to embed the object to upsert, default to False

        Returns
        -------
        Base
            Upserted database object
        """
        db_obj = self.get_by_text(db, obj_in.text)
        if db_obj:
            db_obj = self._update(db, db_obj, obj_in, embed=embed)
        else:
            db_obj = self._create(db, obj_in, embed=embed)

        db.commit()
        return db_obj
