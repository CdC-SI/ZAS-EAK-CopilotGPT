from .base import CRUDBase
from ..models import Source


class CRUDSource(CRUDBase):
    def __init__(self):
        super().__init__(Source)

    def create(self, db, obj_in):
        db_obj = Source(**obj_in.dict())
        return super().create(db, db_obj)

    def get_by_sitemap_url(self, db, url):
        return db.query(self.model).filter(self.model.sitemap_url == url).first()


crud_source = CRUDSource()
