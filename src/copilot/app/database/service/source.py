from .base import CRUDBase
from ..models import Source


class CRUDSource(CRUDBase):
    def __init__(self):
        super().__init__(Source)

    def get_by_url(self, db, url):
        return db.query(self.model).filter(self.model.url == url).first()

    def get_or_create(self, db, obj_in):
        db_obj = self.get_by_url(db, obj_in.url)
        if db_obj:
            return db_obj
        return self.create(db, obj_in)


crud_source = CRUDSource()
