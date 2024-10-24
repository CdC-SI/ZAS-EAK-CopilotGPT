from sqlalchemy.orm import Session
from sqlalchemy import func, select

from .base import EmbeddingService
from utils.embedding import get_embedding


class MatchingService(EmbeddingService):
    """
    Class that provide services for matching text with database entries
    """

    def get_exact_match(self, db: Session, user_input: str, language: str = None, k: int = 0, tag: str = None):
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
        if tag:
            stmt = stmt.filter(self.model.tag.ilike(f'%{tag}%'))

        stmt = stmt.filter(self.model.text.like(search))
        if k > 0:
            stmt = stmt.limit(k)

        rows = db.scalars(stmt).all()
        return rows

    def get_fuzzy_match(self, db: Session, user_input: str, threshold: int = 150, language: str = None, k: int = 0, tag: str = None):
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
        if tag:
            stmt = stmt.filter(self.model.tag.ilike(f'%{tag}%'))

        stmt = (stmt
                .filter(func.levenshtein_less_equal(self.model.text, user_input, threshold) < threshold)
                .order_by(func.levenshtein(self.model.text, user_input).asc()))

        if k > 0:
            stmt = stmt.limit(k)

        rows = db.scalars(stmt).all()
        return rows

    def get_trigram_match(self, db: Session, user_input: str, threshold: int = 0.4, language: str = None, k: int = 0, tag: str = None):
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
        if tag:
            stmt = stmt.filter(self.model.tag.ilike(f'%{tag}%'))

        stmt = (stmt
                .filter(func.word_similarity(user_input, self.model.text) > threshold)
                .order_by(func.word_similarity(user_input, self.model.text).desc()))
        if k > 0:
            stmt = stmt.limit(k)

        rows = db.scalars(stmt).all()
        return rows

    async def get_semantic_match(self, db: Session, user_input: str, language: str = None, k: int = 0, symbol: str = "<=>", tag: str = None):
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

        Returns
        -------
        list of dict
        """
        q_embedding = await get_embedding(user_input)

        stmt = select(self.model)
        stmt = stmt.filter(self.model.embedding.isnot(None))  # filter out entries without embedding
        if language:
            stmt = stmt.filter(self.model.language == language)
        if tag:
            stmt = stmt.filter(self.model.tag.ilike(f'%{tag}%'))

        stmt = stmt.order_by(self.model.embedding.op(symbol)(q_embedding).asc())
        if k > 0:
            stmt = stmt.limit(k)

        rows = db.scalars(stmt).all()
        return rows

    async def semantic_similarity_match_l1(self, db: Session, user_input: str, language: str = None, k: int = 0, tag: str = None):
        """
        Get semantic similarity match from database using L1 distance
        """
        return self.get_semantic_match(db, user_input, language=language, k=k, symbol="<+>", tag=tag)

    async def semantic_similarity_match_l2(self, db: Session, user_input: str, language: str = None, k: int = 0, tag: str = None):
        """
        Get semantic similarity match from database using L2 distance
        """
        return self.get_semantic_match(db, user_input, language=language, k=k, symbol="<->", tag=tag)

    async def semantic_similarity_match_inner_prod(self, db: Session, user_input: str, language: str = None, k: int = 0, tag: str = None):
        """
        Get semantic similarity match from database using inner product
        """
        return self.get_semantic_match(db, user_input, language=language, k=k, symbol="<#>", tag=tag)
