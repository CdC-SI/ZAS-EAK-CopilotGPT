from sqlalchemy.orm import Session

from .matching import MatchingService
from .source import source_service
from ..models import Document, Source
from ..schemas import DocumentCreate, DocumentsCreate, SourceCreate, DocumentUpdate


class DocumentService(MatchingService):
    def __init__(self):
        super().__init__(Document)

    def _create(self, db: Session, obj_in: DocumentCreate, source: Source = None, embed=False):
        source = source_service.get_or_create(db, SourceCreate(url=obj_in.source))
        db_document = Document(url=obj_in.url, language=obj_in.language, text=obj_in.text, source=source, source_id=source.id)
        if embed:
            db_document = self._embed(db_document)

        db.add(db_document)
        return db_document

    def create(self, db: Session, obj_in: DocumentCreate, embed=False):
        db_document = self._create(db, obj_in, embed=embed)
        db.commit()
        return db_document

    def get_by_url(self, db: Session, url: str):
        return db.query(self.model).filter(self.model.url == url).one_or_none()

    def get_by_text(self, db: Session, text: str):
        return db.query(self.model).filter(self.model.text == text).one_or_none()

    def upsert(self, db: Session, obj_in: DocumentCreate, embed=False):
        db_document = self.get_by_text(db, obj_in.text)
        if db_document:
            db_document = self._update(db, db_document, obj_in, embed=embed)
        else:
            db_document = self._create(db, obj_in, embed=embed)
        db.commit()
        return db_document

    def upsert_all(self, db: Session, objs_in: DocumentsCreate, embed=False):
        db_documents = []
        for obj_in in objs_in.objects:
            db_documents.append(self.upsert(db, obj_in, embed=embed))
        db.commit()
        return db_documents

    def _update(self, db: Session, db_obj, obj_in, embed=False):
        db_source = source_service.get_or_create(db, SourceCreate(url=obj_in.source))
        obj_in.source_id = db_source.id

        if embed:
            db_obj = self._embed(db_obj)

        return super()._update(db, db_obj, DocumentUpdate(**obj_in.model_dump(exclude={'source'}), source=db_source))


document_service = DocumentService()
