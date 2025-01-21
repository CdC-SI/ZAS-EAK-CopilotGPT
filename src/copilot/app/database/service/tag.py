from sqlalchemy.orm import Session

from .matching import MatchingService
from ..models import Tag
from schemas.tag import TagCreate


class TagService(MatchingService):
    def __init__(self):
        super().__init__(Tag)

    async def _create(self, db: Session, obj_in: TagCreate, embed=False):

        db_document = Tag(
            tag_en=obj_in.tag_en,
            description_en=obj_in.description_en,
            description=obj_in.description,
            language=obj_in.language,
            embedding=obj_in.embedding,
        )
        if embed:
            db_document = await self._embed(db_document)

        db.add(db_document)
        return db_document


tag_service = TagService()
