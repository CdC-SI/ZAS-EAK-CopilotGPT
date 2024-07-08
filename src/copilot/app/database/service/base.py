from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Base

from abc import ABCMeta
from typing import Type


class CRUDBase(metaclass=ABCMeta):
    def __init__(self, model=Type[Base]):
        self.model = model

    def get(self, db: Session, id_: int):
        return select(self.model).filter(self.model.id == id_)

    def _create(self, db: Session, obj_in):
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        return db_obj

    def create(self, db: Session, obj_in):
        db_obj = self._create(db, obj_in)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def _create_all(self, db: Session, obj_in):
        db.add_all(obj_in)

    def create_all(self, db: Session, obj_in):
        self._create_all(db, obj_in)
        db.commit()
        for obj in obj_in:
            db.refresh(obj)
        return obj_in

    def _update(self, db, db_obj, obj_in):
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        return db_obj

    def update(self, db: Session, db_obj, obj_in):
        self._update(db_obj, obj_in)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_all(self, db: Session, db_objs, objs_in):
        for db_obj, obj_in in zip(db_objs, objs_in):
            for field, value in obj_in.dict(exclude_unset=True).items():
                setattr(db_obj, field, value)
        db.commit()
        for db_obj in db_objs:
            db.refresh(db_obj)
        return db_objs

    def _delete(self, db: Session, id_):
        obj = db.query(self.model).filter(self.model.id == id_).first()
        if obj:
            db.delete(obj)
        return obj

    def delete(self, db: Session, id_: int):
        obj = self._delete(db, id_)
        db.commit()
        return obj
