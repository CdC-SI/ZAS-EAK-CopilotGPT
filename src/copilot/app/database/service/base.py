from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import Base

from abc import ABCMeta
from typing import Type


class Base(metaclass=ABCMeta):
    def __init__(self, model=Type[Base]):
        self.model = model

    def add(self, db: Session, obj_in):
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        return db_obj

    def get(self, db: Session, id_: int):
        stmt = select(self.model).filter(self.model.id == id_)
        return db.scalars(stmt).one()

    def update(self, db: Session, db_obj, obj_in):
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.commit()
        return db_obj

    def delete(self, db: Session, id_: int):
        db_obj = self.get(db, id_)
        db.delete(db_obj)
        db.commit()
