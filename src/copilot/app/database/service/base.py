from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Base

from utils.embedding import get_embedding

from abc import ABCMeta, abstractmethod
from typing import Type, Union, Tuple

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseService(metaclass=ABCMeta):
    def __init__(self, model=Type[Base]):
        self.model = model

    def _create(self, db: Session, obj_in):
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        return db_obj

    def create(self, db: Session, obj_in):
        db_obj = self._create(db, obj_in)
        db.commit()
        return db_obj

    def create_all(self, db: Session, objs_in):
        db_objs = []
        for obj_in in objs_in.objects:
            db_objs.append(self._create(db, obj_in))
        db.commit()
        return db_objs

    def get(self, db: Session, id_: int):
        stmt = select(self.model).filter(self.model.id == id_)
        return db.execute(stmt).scalar_one()

    def _update(self, db: Session, db_obj, obj_in):
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        return db_obj

    def update(self, db: Session, db_obj, obj_in):
        db_obj = self._update(db, db_obj, obj_in)
        db.commit()
        return db_obj

    def update_all(self, db: Session, objs_in):
        db_objs = []
        for obj_in in objs_in:
            db_obj = self.get(db, obj_in.id)
            db_objs.append(self.update(db, db_obj, obj_in))
        db.commit()
        return db_objs

    def _delete(self, db: Session, id_: int):
        db_obj = self.get(db, id_)
        db.delete(db_obj)
        return db_obj

    def delete(self, db: Session, id_: int):
        db_obj = self._delete(db, id_)
        db.commit()
        return db_obj

    def delete_all(self, db: Session, ids: list[int]):
        db_objs = []
        for id_ in ids:
            db_objs.append(self._delete(db, id_))
        db.commit()
        return db_objs


class EmbeddingService(BaseService):

    def _embedding(self,db_obj, text: str):
        db_obj.embedding = get_embedding(text)
        return db_obj

    def _embed(self, db_obj):
        return self._embedding(db_obj, db_obj.text)

    def embed_one(self, db: Session, db_obj):
        db_obj = self._embed(db_obj)
        db.commit()
        return db_obj

    def embed_many(self, db: Session, embed_empty_only=True, k: int = 0):
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
    def _create(self, db: Session, obj_in, embed=False):
        pass

    def create(self, db: Session, obj_in, embed=False):
        db_obj = self._create(db, obj_in, embed=embed)
        db.commit()
        return db_obj

    def create_all(self, db: Session, objs_in, embed=False):
        db_objs = []
        for obj_in in objs_in.objects:
            db_objs.append(self._create(db, obj_in, embed=embed))
        db.commit()
        return db_objs

    def get_by_text(self, db: Session, text: str):
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

    def update(self, db: Session, db_obj, obj_in, embed=False):
        return self._update(db, db_obj, obj_in, embed=embed)

    def upsert(self, db: Session, obj_in, embed=False):
        db_obj = self.get_by_text(db, obj_in.text)
        if db_obj:
            db_obj = self._update(db, db_obj, obj_in, embed=embed)
        else:
            db_obj = self._create(db, obj_in, embed=embed)

        db.commit()
        return db_obj
