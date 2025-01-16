from sqlalchemy import select
from sqlalchemy.orm import Session

from .base import BaseService
from ..models import Source, Document
from schemas.source import SourceCreate
from utils.logging import get_logger

logger = get_logger(__name__)


class SourceService(BaseService):
    """
    Class that provide services for source database operations
    """

    def __init__(self):
        super().__init__(Source)

    def get_by_url(self, db: Session, url: str):
        """
        Get a source item by its url. If it does not exist, return None.

        Parameters
        ----------
        db : Session
            Database session
        url : str
            Source url

        Returns
        -------
        database.models.Source or None
        """
        stmt = select(self.model).filter(self.model.url == url)
        return db.scalars(stmt).one_or_none()

    def get_or_create(self, db: Session, obj_in: SourceCreate):
        """
        Get a source item if it exists, otherwise create it

        Parameters
        ----------
        db : Session
            Database session
        obj_in : SourceCreate
            Source schema to create a new source

        Returns
        -------
        database.models.Source
        """
        db_obj = self.get_by_url(db, obj_in.url)

        # if the source already exists, return it
        if db_obj:
            return db_obj

        # otherwise, create a new source
        return self.create(db, obj_in)

    def delete_expired_sources(self, db: Session):
        """
        Delete all sources that have no associated documents.

        Parameters
        ----------
        db: Session
            Database session
        """
        try:
            subquery = select(Document.url).distinct()
            deleted_count = (
                db.query(Source)
                .filter(~Source.url.in_(subquery))
                .delete(synchronize_session=False)
            )
            db.commit()
            logger.info("Deleted %i orphaned sources.", deleted_count)
        except Exception as e:
            db.rollback()
            logger.error(
                "An error occurred while deleting orphaned sources: %s", e
            )
            raise


source_service = SourceService()
