from typing import List, Union

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select
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
        """
        Get semantic similarity match from database

        Parameters
        ----------
        db : Session
        user_input : str
            User input to match database entries
        symbol : str, optional
            distance function symbol, default to `<=>` (cosine distance). For other options, see https://github.com/pgvector/pgvector
        language : str, optional
            Question and results language
        k : int, optional
            Number of results to return, default to 0 (return all results)
        tags : List[str], optional
            Filter by tags
        source : List[str], optional
            Filter by source
        organizations : List[str], optional
            Filter by organizations
        user_uuid : str, optional
            Filter by user_uuid
        embedding_field : Union[str, List[str]], optional
            Single field name or list of field names to match against

        Returns
        -------
        list of dict
        """
        # Handle both single field and multiple fields
        embedding_fields = (
            [embedding_field]
            if isinstance(embedding_field, str)
            else embedding_field
        )

        # Validate all fields exist
        for field in embedding_fields:
            if not hasattr(self.model, field):
                raise ValueError(
                    f"Model does not have embedding field: {field}"
                )

        q_embedding = await get_embedding(user_input)

        # Execute semantic match for each field concurrently
        async def get_matches_for_field(field):
            embedding_attr = getattr(self.model, field)
            stmt = select(self.model).filter(embedding_attr.isnot(None))

            # Start building the query
            if user_uuid:
                docs_with_uuid = select(self.model.id).where(
                    self.model.user_uuid == user_uuid
                )
                docs_without_uuid = select(self.model.id).where(
                    self.model.user_uuid.is_(None)
                )
                stmt = stmt.filter(
                    self.model.id.in_(docs_with_uuid.union(docs_without_uuid))
                )

            if language:
                stmt = stmt.filter(self.model.language == language)

            if source:
                stmt = stmt.join(self.model.source).filter(
                    Source.url.in_(source)
                )
                stmt = stmt.options(joinedload(self.model.source))

            if tags:
                stmt = stmt.filter(self.model.tags.op("&&")(tags))

            if organizations:
                docs_with_org = select(self.model.id).where(
                    self.model.organizations.op("&&")(organizations)
                )
                docs_without_org = select(self.model.id).where(
                    self.model.organizations.is_(None)
                )
                stmt = stmt.filter(
                    self.model.id.in_(docs_with_org.union(docs_without_org))
                )
            else:
                stmt = stmt.filter(self.model.organizations.is_(None))

            # Order by similarity
            stmt = stmt.order_by(embedding_attr.op(symbol)(q_embedding).asc())

            if k > 0:
                stmt = stmt.limit(k)

            rows = db.scalars(stmt).all()
            return [row.to_dict() for row in rows]

        # Get results for all fields concurrently
        results = await asyncio.gather(
            *[get_matches_for_field(field) for field in embedding_fields]
        )

        # Merge results and remove duplicates based on id
        seen = set()
        merged_results = []
        for result_set in results:
            for doc in result_set:
                if doc["id"] not in seen:
                    seen.add(doc["id"])
                    merged_results.append(doc)

        # Sort combined results by relevance
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
