from sqlalchemy.orm import Session

from .matching import MatchingService
from .source import source_service
from ..models import Document, Source
from ..schemas import DocumentCreate, DocumentsCreate, SourceCreate, DocumentUpdate


class DocumentService(MatchingService):
    def __init__(self):
        super().__init__(Document)

    def _create(self, db: Session, obj_in: DocumentCreate, embed=False):
        source = source_service.get_or_create(db, SourceCreate(url=obj_in.source))
        db_document = Document(url=obj_in.url, language=obj_in.language, text=obj_in.text, source=source, source_id=source.id)
        if embed:
            db_document = self._embed(db_document)

        db.add(db_document)
        return db_document

    def get_by_url(self, db: Session, url: str):
        return db.query(self.model).filter(self.model.url == url).one_or_none()

    def _update(self, db: Session, db_obj, obj_in, embed=False):
        db_source = source_service.get_or_create(db, SourceCreate(url=obj_in.source))

        exclude = self._update_embed_exclude(db_obj, obj_in, embed)
        super()._update(db, db_obj, DocumentUpdate(**obj_in.model_dump(exclude=exclude), source_id=db_source.id))

        return db_obj


document_service = DocumentService()
