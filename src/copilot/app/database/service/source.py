from sqlalchemy import select

from .base import BaseService
from ..models import Source


class SourceService(BaseService):
    def __init__(self):
        super().__init__(Source)

    def get_by_url(self, db, url):
        stmt = select(self.model).filter(self.model.url == url)
        return db.scalars(stmt).one_or_none()

    def get_or_create(self, db, obj_in):
        db_obj = self.get_by_url(db, obj_in.url)
        if db_obj:
            return db_obj
        return self.create(db, obj_in)


source_service = SourceService()
