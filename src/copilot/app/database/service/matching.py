from sqlalchemy.orm import Session
from sqlalchemy import func, select

from .base import EmbeddingService
from utils.embedding import get_embedding


class MatchingService(EmbeddingService):

    def get_exact_match(self, db: Session, user_input: str, language: str = None, k: int = 0):
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

        stmt = stmt.filter(self.model.text.like(search))
        if k > 0:
            stmt = stmt.limit(k)

        return db.scalars(stmt).all()

    def get_fuzzy_match(self, db: Session, user_input: str, threshold: int = 150, language: str = None, k: int = 0):
        """
        Get fuzzy match from database

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

        stmt = (stmt
                .filter(func.levenshtein_less_equal(self.model.text, user_input, threshold) < threshold)
                .order_by(func.levenshtein(self.model.text, user_input).asc()))

        if k > 0:
            stmt = stmt.limit(k)

        return db.scalars(stmt).all()

    def get_trigram_match(self, db: Session, user_input: str, threshold: int = 0.4, language: str = None, k: int = 0):
        """
        Get trigram match from database

        Parameters
        ----------
        db : Session
        user_input : str
            User input to match database entries
        threshold : int, optional
        language : str, optional
            Question and results language
        k : int, optional
            Number of results
        """
        stmt = select(self.model)
        if language:
            stmt = stmt.filter(self.model.language == language)

        stmt = (stmt
                .filter(func.word_similarity(user_input, self.model.text) > threshold)
                .order_by(func.word_similarity(user_input, self.model.text).desc()))
        if k > 0:
            stmt = stmt.limit(k)

        return db.scalars(stmt).all()

    def get_semantic_match(self, db: Session, user_input: str, symbol: str = "<=>", language: str = None, k: int = 0):
        """
        Get semantic match from database

        Parameters
        ----------
        db : Session
        user_input : str
            User input to match database entries
        symbol : str, optional
        language : str, optional
        k : int, optional

        Returns
        -------
        list of dict
        """
        q_embedding = get_embedding(user_input)

        stmt = select(self.model)
        stmt = stmt.filter(self.model.embedding.isnot(None))
        if language:
            stmt = stmt.filter(self.model.language == language)

        stmt = stmt.order_by(self.model.embedding.op(symbol)(q_embedding).asc())
        if k > 0:
            stmt = stmt.limit(k)

        return db.scalars(stmt).all()

    def semantic_similarity_match_l1(self, db: Session, user_input: str, language: str = None, k: int = 0):
        return self.get_semantic_match(db, user_input, symbol="<+>", language=language, k=k)

    def semantic_similarity_match_l2(self, db: Session, user_input: str, language: str = None, k: int = 0):
        return self.get_semantic_match(db, user_input, symbol="<->", language=language, k=k)

    def semantic_similarity_match_inner_prod(self, db: Session, user_input: str, language: str = None, k: int = 0):
        return self.get_semantic_match(db, user_input, symbol="<#>", language=language, k=k)
