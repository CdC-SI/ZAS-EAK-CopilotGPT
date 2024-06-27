from .base import CRUDBase
from ..models import Language


class CRUDLanguage(CRUDBase):
    def __init__(self):
        super().__init__(Language)

    def get_by_code(self, db, code: str):
        return db.query(self.model).filter(self.model.code == code).first()


crud_language = CRUDLanguage()
