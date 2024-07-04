from sqlalchemy.orm import Session
from sqlalchemy import func

from .question import CRUDQuestion
from utils.embedding import get_embedding


class CRUDMatching(CRUDQuestion):

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

        results = db.query(self.model)
        if language:
            results = results.filter(self.model.language == language)

        results = results.filter(self.model.question.like(search))
        if k > 0:
            results = results.limit(k)

        return results.all()

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
        results = db.query(self.model)
        if language:
            results = results.filter(self.model.language == language)

        results = (results
                   .filter(func.levenshtein_less_equal(self.model.question, user_input, threshold) < threshold)
                   .order_by(func.levenshtein(self.model.question, user_input).asc()))

        if k > 0:
            results = results.limit(k)

        return results.all()

    def get_trigram_match(self, db: Session, user_input: str, threshold: int = 0.5, language: str = None, k: int = 0):
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
        results = db.query(self.model)
        if language:
            results = results.filter(self.model.language == language)

        results = (results
                   .filter(func.word_similarity(user_input, self.model.question) > threshold)
                   .order_by(func.word_similarity(user_input, self.model.question).desc()))
        if k > 0:
            results = results.limit(k)

        return results.all()

    def get_semantic_match(self, db: Session, user_input: str, symbol: str = '<=>', language: str = None, k: int = 0):
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
        q_embedding = get_embedding(user_input)[0].embedding

        results = db.query(self.model)
        if language:
            results = results.filter(self.model.language == language)

        results = results.order_by(func.op(symbol)(q_embedding).asc())
        if k > 0:
            results = results.limit(k)

        return results.all()

    def semantic_similarity_match_l1(self, db: Session, user_input: str, language: str = None, k: int = 0):
        return self.get_semantic_match(db, user_input, symbol='<+>', language=language, k=k)

    def semantic_similarity_match_l2(self, db: Session, user_input: str, language: str = None, k: int = 0):
        return self.get_semantic_match(db, user_input, symbol='<->', language=language, k=k)

    def semantic_similarity_match_inner_prod(self, db: Session, user_input: str, language: str = None, k: int = 0):
        return self.get_semantic_match(db, user_input, symbol='<#>', language=language, k=k)


crud_matching = CRUDMatching()
