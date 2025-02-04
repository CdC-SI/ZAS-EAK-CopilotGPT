from typing import List, Union

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select, or_
import asyncio

from .base import EmbeddingService
from database.models import Source
from utils.embedding import get_embedding

from utils.logging import get_logger

logger = get_logger(__name__)


class MatchingService(EmbeddingService):
    """
    Class that provide services for matching text with database entries
    """

    def get_exact_match(
        self,
        db: Session,
        user_input: str,
        language: str = None,
        k: int = 0,
        tags: List[str] = None,
    ):
        """
        Get exact match from database

        Parameters
        ----------
        db : Session
        user_input : str
            User input to match database entries
        language : str, optional
            Question and results language
        k : int, optional
            Number of results to return

        Returns
        -------
        list of dict
        """
        search = "%{}%".format(user_input)

        stmt = select(self.model)
        if language:
            stmt = stmt.filter(self.model.language == language)
        if tags:
            stmt = stmt.filter(self.model.tags.op("&&")(tags))

        stmt = stmt.filter(self.model.text.like(search))
        if k > 0:
            stmt = stmt.limit(k)

        rows = db.scalars(stmt).all()
        return [row.to_dict() for row in rows]

    def get_fuzzy_match(
        self,
        db: Session,
        user_input: str,
        threshold: int = 150,
        language: str = None,
        k: int = 0,
        tags: List[str] = None,
    ):
        """
        Get fuzzy match from database using levenshtein distance

        Parameters
        ----------
        db : Session
        user_input : str
            User input to match database entries
        threshold : int, optional
        language : str, optional
            Question and results language
        k : int, optional
            Number of results to return

        Returns
        -------
        list of dict
        """
        stmt = select(self.model)
        if language:
            stmt = stmt.filter(self.model.language == language)
        if tags:
            stmt = stmt.filter(self.model.tags.op("&&")(tags))

        stmt = stmt.filter(
            func.levenshtein_less_equal(self.model.text, user_input, threshold)
            < threshold
        ).order_by(func.levenshtein(self.model.text, user_input).asc())

        if k > 0:
            stmt = stmt.limit(k)

        rows = db.scalars(stmt).all()
        return [row.to_dict() for row in rows]

    def get_trigram_match(
        self,
        db: Session,
        user_input: str,
        threshold: int = 0.4,
        language: str = None,
        k: int = 0,
        tags: List[str] = None,
    ):
        """
        Get trigram match from database

        Parameters
        ----------
        db : Session
        user_input : str
            User input to match database entries
        threshold : int, optional
            Trigram similarity threshold, default to 0.4
        language : str, optional
            Question and results language
        k : int, optional
            Number of results to return, default to 0 (return all results)
        """
        stmt = select(self.model)
        if language:
            stmt = stmt.filter(self.model.language == language)
        if tags:
            stmt = stmt.filter(self.model.tags.op("&&")(tags))

        stmt = stmt.filter(
            func.word_similarity(user_input, self.model.text) > threshold
        ).order_by(func.word_similarity(user_input, self.model.text).desc())
        if k > 0:
            stmt = stmt.limit(k)

        rows = db.scalars(stmt).all()
        return [row.to_dict() for row in rows]

    async def get_semantic_match(
        self,
        db: Session,
        user_input: str,
        language: str = None,
        k: int = 0,
        symbol: str = "<=>",
        tags: List[str] = None,
        source: List[str] = None,
        organizations: List[str] = None,
        user_uuid: str = None,
        embedding_field: Union[str, List[str]] = "text_embedding",
    ):
        """Get semantic similarity match from database"""
        embedding_fields = self._validate_and_get_embedding_fields(
            embedding_field
        )
        q_embedding = await get_embedding(user_input)

        # Get results for all fields concurrently
        results = await asyncio.gather(
            *[
                self._get_matches_for_field(
                    db,
                    q_embedding,
                    field,
                    language,
                    k,
                    symbol,
                    tags,
                    source,
                    organizations,
                    user_uuid,
                )
                for field in embedding_fields
            ]
        )

        merged_results = self._merge_and_sort_results(results, k)
        return merged_results

    def _validate_and_get_embedding_fields(
        self, embedding_field: Union[str, List[str]]
    ) -> List[str]:
        """Validate and return list of embedding fields"""
        embedding_fields = (
            [embedding_field]
            if isinstance(embedding_field, str)
            else embedding_field
        )

        for field in embedding_fields:
            if not hasattr(self.model, field):
                raise ValueError(
                    f"Model does not have embedding field: {field}"
                )

        return embedding_fields

    async def _get_matches_for_field(
        self,
        db: Session,
        q_embedding: List[float],
        field: str,
        language: str,
        k: int,
        symbol: str,
        tags: List[str],
        source: List[str],
        organizations: List[str],
        user_uuid: str,
    ) -> List[dict]:
        """Get matches for a specific embedding field"""
        embedding_attr = getattr(self.model, field)

        user_docs = await self._get_user_documents(
            db, user_uuid, embedding_attr, q_embedding, symbol
        )
        public_docs = await self._get_public_documents(
            db,
            embedding_attr,
            q_embedding,
            symbol,
            language,
            tags,
            source,
            organizations,
        )

        all_docs = [doc.to_dict() for doc in user_docs]
        all_docs.extend([doc.to_dict() for doc in public_docs])

        return all_docs[:k] if k > 0 else all_docs

    async def _get_user_documents(
        self,
        db: Session,
        user_uuid: str,
        embedding_attr,
        q_embedding: List[float],
        symbol: str,
    ) -> List[dict]:
        """Get user-specific documents"""
        if not user_uuid:
            return []

        user_stmt = (
            select(self.model)
            .filter(
                self.model.user_uuid == user_uuid,
                embedding_attr.isnot(None),
            )
            .order_by(embedding_attr.op(symbol)(q_embedding).asc())
        )
        return db.scalars(user_stmt).all()

    async def _get_public_documents(
        self,
        db: Session,
        embedding_attr,
        q_embedding: List[float],
        symbol: str,
        language: str,
        tags: List[str],
        source: List[str],
        organizations: List[str],
    ) -> List[dict]:
        """Get public documents with applied filters"""
        public_stmt = self._build_public_query(
            embedding_attr, language, tags, source, organizations
        )

        public_stmt = public_stmt.order_by(
            embedding_attr.op(symbol)(q_embedding).asc()
        )
        return db.scalars(public_stmt).all()

    def _build_public_query(
        self,
        embedding_attr,
        language: str,
        tags: List[str],
        source: List[str],
        organizations: List[str],
    ):
        """Build query for public documents with filters"""
        stmt = select(self.model).filter(
            self.model.user_uuid.is_(None),
            embedding_attr.isnot(None),
        )

        if language:
            stmt = stmt.filter(self.model.language == language)
        if source:
            stmt = (
                stmt.join(self.model.source)
                .filter(Source.url.in_(source))
                .options(joinedload(self.model.source))
            )
        if tags:
            stmt = stmt.filter(self.model.tags.op("&&")(tags))
        if organizations:
            stmt = stmt.filter(
                or_(
                    self.model.organizations.op("&&")(organizations),
                    self.model.organizations.is_(None),
                )
            )
        else:
            stmt = stmt.filter(self.model.organizations.is_(None))

        return stmt

    def _merge_and_sort_results(
        self, results: List[List[dict]], k: int
    ) -> List[dict]:
        """Merge and sort results, removing duplicates"""
        seen = set()
        merged_results = []

        for result_set in results:
            for doc in result_set:
                if doc["id"] not in seen:
                    seen.add(doc["id"])
                    merged_results.append(doc)

        return merged_results

    async def semantic_similarity_match_l1(
        self,
        db: Session,
        user_input: str,
        language: str = None,
        k: int = 0,
        tags: str = None,
    ):
        """
        Get semantic similarity match from database using L1 distance
        """
        return self.get_semantic_match(
            db,
            user_input,
            language=language,
            k=k,
            symbol="<+>",
            tags=tags,
            embedding_field="text_embedding",
        )

    async def semantic_similarity_match_l2(
        self,
        db: Session,
        user_input: str,
        language: str = None,
        k: int = 0,
        tags: str = None,
    ):
        """
        Get semantic similarity match from database using L2 distance
        """
        return self.get_semantic_match(
            db,
            user_input,
            language=language,
            k=k,
            symbol="<->",
            tags=tags,
            embedding_field="text_embedding",
        )

    async def semantic_similarity_match_inner_prod(
        self,
        db: Session,
        user_input: str,
        language: str = None,
        k: int = 0,
        tags: str = None,
    ):
        """
        Get semantic similarity match from database using inner product
        """
        return self.get_semantic_match(
            db,
            user_input,
            language=language,
            k=k,
            symbol="<#>",
            tags=tags,
            embedding_field="text_embedding",
        )
