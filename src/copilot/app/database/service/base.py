import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Base

from utils.embedding import get_embedding

from abc import ABCMeta
from typing import Type


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

    def _embed(self, db_obj):
        db_obj.embedding = get_embedding(db_obj.text)
        return db_obj

    def embed(self, db: Session, db_obj):
        db_obj = self._embed(db_obj)
        db.commit()
        return db_obj

    def embed_all(self, db: Session):
        objs = db.scalars(select(self.model)).all()
        for obj in objs:
            self._embed(obj)
        db.commit()
        return objs

    def embed_missing(self, db: Session):
        questions = db.scalars(select(self.model).filter(self.model.embedding.is_(None))).all()
        for question in questions:
            self._embed(question)
        db.commit()
        return questions
