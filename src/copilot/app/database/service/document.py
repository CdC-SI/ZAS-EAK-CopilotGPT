from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import select

from .matching import MatchingService
from .source import source_service
from ..models import Document
from schemas.document import DocumentCreate, DocumentUpdate
from schemas.source import SourceCreate
from database.models import Source


class DocumentService(MatchingService):
    def __init__(self):
        super().__init__(Document)

    async def _create(self, db: Session, obj_in: DocumentCreate, embed=False):
        source = source_service.get_or_create(
            db, SourceCreate(url=obj_in.source)
        )

        db_document = Document(
            url=obj_in.url,
            language=obj_in.language,
            text=obj_in.text,
            tags=obj_in.tags,
            organization=obj_in.organization,
            user_uuid=obj_in.user_uuid,
            embedding=obj_in.embedding,
            source=source,
            source_id=source.id,
        )
        if embed:
            db_document = await self._embed(db_document)

        db.add(db_document)
        return db_document

    def get_by_url(self, db: Session, url: str):
        """
        Get a document by its URL field

        Parameters
        ----------
        db: Session
            Database session
        url: str
            Document

        Returns
        -------
        Document
        """
        return db.query(self.model).filter(self.model.url == url).one_or_none()

    async def _update(self, db: Session, db_obj, obj_in, embed=False):
        db_source = source_service.get_or_create(
            db, SourceCreate(url=obj_in.source)
        )

        exclude = await self._update_embed_exclude(db_obj, obj_in, embed)
        await super()._update(
            db,
            db_obj,
            DocumentUpdate(
                **obj_in.model_dump(exclude=exclude), source_id=db_source.id
            ),
        )

        return db_obj

    def get_count(self, db: Session):
        """
        Get the number of documents in the database

        Parameters
        ----------
        db: Session
            Database session

        Returns
        -------
        int
        """
        return db.query(self.model).count()

    def get_all_documents(
        self, db: Session, tags: List[str] = None, source: List[str] = None
    ):
        """
        Get all documents from the database

        Parameters
        ----------
        db: Session
            Database session

        Returns
        -------
        List[Model]
        """
        stmt = select(self.model)
        if tags:
            stmt = stmt.filter(self.model.tags.in_(tags))
        if source:
            stmt = stmt.join(self.model.source).filter(Source.url.in_(source))
        return db.scalars(stmt).all()


document_service = DocumentService()
