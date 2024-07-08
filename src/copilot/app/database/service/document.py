from sqlalchemy.orm import Session

from .base import CRUDBase
from ..models import Document
from ..schemas import DocumentCreate, DocumentsCreate

from utils.embedding import get_embedding


class CRUDDocument(CRUDBase):
    def __init__(self):
        super().__init__()
        self.model = Document

    def create_all(self, db: Session, obj_in: DocumentsCreate):
        db_obj = [Document(**obj.dict()) for obj in obj_in.documents]
        return super().create_all(db, db_obj)

    def embed_all(self, db: Session):
        documents = db.query(Document).filter(Document.embedding.is_(None)).all()
        for document in documents:
            document.embedding = get_embedding(document.text)[0].embedding
            db.commit()
            db.refresh(document)
        return documents


crud_document = CRUDDocument()
