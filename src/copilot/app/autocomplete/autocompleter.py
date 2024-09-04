import hashlib
from sqlalchemy.orm import Session

from config.config import AutocompleteConfig
from database.service.question import question_service


class Autocompleter:
    """
    Autocomplete user input by providing matching questions from the database.

    Attributes
    ----------
        limit : int
            number of results to return
        levenshtein_match_threshold : int
            threshold for trigram matching with levenshtein, only results with a similarity score below this threshold will be returned
        trigram_match_threshold : int
            threshold for trigram matching, only results with a similarity score above this threshold will be returned
    """

    def __init__(self, limit: int, levenshtein_match_threshold: int, trigram_match_threshold: int):
        self.limit = limit
        self.levenshtein_match_threshold = levenshtein_match_threshold
        self.trigram_match_threshold = trigram_match_threshold

        self.semantic_matches_cache = {}

    def _cache_key(self, question, language):
        """
        Generate a cache key based on the question and language.

        Parameters
        ----------
        question : str
            question to match
        language : str
            question and results language

        Returns
        -------
        str
            a cache key encoded as a md5 hash
        """
        return hashlib.md5(f"{question}_{language}".encode()).hexdigest()

    async def get_autocomplete(self, db: Session, question: str, language: str = None, k: int = 0, tag: str = None):
        """
        Returns matching results according to a defined behaviour.

        If the user input ends with a "?" character, return a set of questions that may be relevant to the user.
        Else return the results stored in the cache from the previous query.

        If there are at lest 5 results from trigram matching, trigram matching returned. Otherwise, results of semantic
        similarity matching are returned alongside the trigram matching results.

        Parameters
        ----------
        db : Session
            database session
        question : str
            question to match
        language : str
            question and results language
        k : int
            number of results to return

        Returns
        -------
        list of str
            a list of matching results
        """
        # Get trigram match
        unique_matches = question_service.get_trigram_match(db,
                                                            question,
                                                            threshold=self.trigram_match_threshold,
                                                            language=language,
                                                            k=self.limit,
                                                            tag=tag)

        # If the combined results from exact match and trigram match are more than 5, return results
        # note: value should be parametrized
        if len(unique_matches) >= 5:
            return unique_matches

        # If the combined results from exact match and trigram match are less than 5, and the question
        # ends with a question mark, perform semantic matching
        if question[-1] == "?":

            # Get semantic matches from cached results
            cache_key = self._cache_key(question, language)
            if cache_key in self.semantic_matches_cache:
                semantic_match = self.semantic_matches_cache[cache_key]
            else:
                semantic_match = question_service.get_semantic_match(db, question, language, k=self.limit, tag=tag)
                self.semantic_matches_cache[cache_key] = semantic_match

            # Remove duplicates and preserve order
            seen = []
            unique_matches = unique_matches + semantic_match
            unique_matches = [seen.append(question) for question in unique_matches if question not in seen]
            unique_matches = seen

            if self.limit > 0:
                unique_matches = unique_matches[:self.limit]

            return unique_matches

        return unique_matches


autocompleter = Autocompleter(
    limit=AutocompleteConfig.limit,
    levenshtein_match_threshold=AutocompleteConfig.levenshtein_match.threshold,
    trigram_match_threshold=AutocompleteConfig.trigram_match.threshold)
