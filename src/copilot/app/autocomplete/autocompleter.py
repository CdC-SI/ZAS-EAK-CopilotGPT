import hashlib
from sqlalchemy.orm import Session

from config.base_config import autocomplete_config
from database.service.question import question_service


class Autocompleter:
    """
    Autocomplete user input to the CopilotChat
    """

    def __init__(self, limit: int, fuzzy_match_threshold: int, trigram_match_threshold: int):
        """
        Parameters
        ----------
        limit : int
            number of results to return
        fuzzy_match_threshold : int
            threshold for fuzzy matching with levenshtein, only results with a similarity score below this threshold will be returned
        trigram_match_threshold : int
            threshold for trigram matching, only results with a similarity score above this threshold will be returned
        """
        self.limit = limit
        self.fuzzy_match_threshold = fuzzy_match_threshold
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

    async def get_autocomplete(self, db: Session, question: str, language: str = None, k: int = 0):
        """
        Returns matching results according to a defined behaviour

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
        # Get fuzzy match
        unique_matches = question_service.get_trigram_match(db,
                                                            question,
                                                            threshold=self.trigram_match_threshold,
                                                            language=language,
                                                            k=self.limit)

        # If the combined results from exact match and fuzzy match are more than 5, return results
        # note: value should be parametrized
        if len(unique_matches) >= 5:
            return unique_matches

        # If the combined results from exact match and fuzzy match are less than 5, and the question ends with a space or a question mark, perform semantic matching
        if question[-1] == "?":

            # Get semantic matches from cached results
            cache_key = self._cache_key(question, language)
            if cache_key in self.semantic_matches_cache:
                semantic_match = self.semantic_matches_cache[cache_key]
            else:
                semantic_match = await question_service.get_semantic_match(db, question, language, k=self.limit)
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
    limit=autocomplete_config["results"]["limit"],
    fuzzy_match_threshold=autocomplete_config["fuzzy_match"]["limit"],
    trigram_match_threshold=autocomplete_config["trigram_match"]["threshold"])
