from sqlalchemy.orm import Session
from ..database import Base


class CRUDBase:
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, id_: int):
        return db.query(self.model).filter(self.model.id == id_).first()

    def add(self, db: Session, obj_in):
        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)
        return obj_in

    def update(self, db: Session, db_obj, obj_in):
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id_: int):
        obj = db.query(self.model).filter(self.model.id == id_).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
