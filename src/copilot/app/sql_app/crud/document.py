from sqlalchemy.orm import Session

from .base import CRUDBase
from ..models import Document
from ..schemas import DocumentCreate, DocumentsCreate


class CRUDDocument(CRUDBase):
    def __init__(self):
        super().__init__(Document)

    def create(self, db, obj_in: DocumentCreate):
        db_obj = Document(**obj_in.dict())
        return super().create(db, db_obj)

    def create_all(self, db: Session, obj_in: DocumentsCreate):
        db_obj = [Document(**obj.dict()) for obj in obj_in.documents]
        return super().create_all(db, db_obj)


crud_document = CRUDDocument()
