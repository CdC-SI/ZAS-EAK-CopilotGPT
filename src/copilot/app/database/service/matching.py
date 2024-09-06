from sqlalchemy.orm import Session
from sqlalchemy import func, select

from config.config import AutocompleteConfig

from .base import EmbeddingService, Embedder


class MatchingService(EmbeddingService):
    """
    Class that provide services for matching text with database entries
    """

    def get_exact_match(self,
                        db: Session,
                        user_input: str,
                        language: str = None,
                        tag: str = None,
                        k: int = AutocompleteConfig.exact_match.limit):
        """
        Get exact match from database

        Parameters
        ----------
        db : Session
        user_input : str
            User input to match database entries
        language : str, optional
            Question and results language
        tag : str, optional
            Tag of the document text
        k : int, optional
            Number of results to return, default to config settings (10)

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

        return db.scalars(stmt).all()

    def get_levenshtein_match(self,
                              db: Session,
                              user_input: str,
                              language: str = None,
                              tag: str = None,
                              k: int = AutocompleteConfig.levenshtein_match.limit,
                              threshold: int = AutocompleteConfig.levenshtein_match.threshold):
        """
        Get levenshtein match from database using levenshtein distance

        Parameters
        ----------
        db : Session
        user_input : str
            User input to match database entries
        language : str, optional
            Question and results language
        tag : str, optional
            Tag of the document text
        k : int, optional
            Number of results to return, default to config settings (10)
        threshold : int, optional
            Levenshtein distance threshold, default to config settings (150)

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

        return db.scalars(stmt).all()

    def get_trigram_match(self,
                          db: Session,
                          user_input: str,
                          language: str = None,
                          tag: str = None,
                          k: int = AutocompleteConfig.trigram_match.limit,
                          threshold: int = AutocompleteConfig.trigram_match.threshold):
        """
        Get trigram match from database

        Parameters
        ----------
        db : Session
        user_input : str
            User input to match database entries
        language : str, optional
            Question and results language
        tag : str, optional
            Tag of the document text
        k : int, optional
            Number of results to return, default to config settings (0, return all results)
        threshold : int, optional
            Trigram similarity threshold, default to config settings (0.4)
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

        return db.scalars(stmt).all()

    def get_semantic_match(self,
                           db: Session,
                           user_input: str,
                           language: str = None,
                           tag: str = None,
                           k: int = AutocompleteConfig.semantic_match.limit,
                           symbol: str = AutocompleteConfig.semantic_match.metric.value):
        """
        Get semantic similarity match from database

        Parameters
        ----------
        db : Session
        user_input : str
            User input to match database entries
        language : str, optional
            Question and results language
        tag : str, optional
            Tag of the document text
        k : int, optional
            Number of results to return, default to config settings (return all results)
        symbol : str, optional
            distance function symbol, default to config settings. For other options, see https://github.com/pgvector/pgvector

        Returns
        -------
        list of dict
        """
        q_embedding = Embedder.embed(user_input)

        stmt = select(self.model)
        stmt = stmt.filter(self.model.embedding.isnot(None))  # filter out entries without embedding
        if language:
            stmt = stmt.filter(self.model.language == language)
        if tag:
            stmt = stmt.filter(self.model.tag.ilike(f'%{tag}%'))

        stmt = stmt.order_by(self.model.embedding.op(symbol)(q_embedding).asc())
        if k > 0:
            stmt = stmt.limit(k)

        return db.scalars(stmt).all()

    def semantic_similarity_match_cosine(self, db: Session, user_input: str, language: str = None, k: int = 0, tag: str = None):
        """
        Get semantic similarity match from database using cosine distance
        """
        return self.get_semantic_match(db, user_input, language=language, k=k, symbol="<=>", tag=tag)

    def semantic_similarity_match_l1(self, db: Session, user_input: str, language: str = None, k: int = 0, tag: str = None):
        """
        Get semantic similarity match from database using L1 distance
        """
        return self.get_semantic_match(db, user_input, language=language, k=k, symbol="<+>", tag=tag)

    def semantic_similarity_match_l2(self, db: Session, user_input: str, language: str = None, k: int = 0, tag: str = None):
        """
        Get semantic similarity match from database using L2 distance
        """
        return self.get_semantic_match(db, user_input, language=language, k=k, symbol="<->", tag=tag)

    def semantic_similarity_match_inner_prod(self, db: Session, user_input: str, language: str = None, k: int = 0, tag: str = None):
        """
        Get semantic similarity match from database using inner product
        """
        return self.get_semantic_match(db, user_input, language=language, k=k, symbol="<#>", tag=tag)
