from abc import ABCMeta, abstractmethod

from config.base_config import autocomplete_config
from . import queries

INF = 0
"""Value for matches limit, equivalent to infinity (return all results)"""


class Matching(metaclass=ABCMeta):
    """
    Abstract class for matching classes
    """
    def __init__(self, match_type: str):
        self.limit = autocomplete_config[match_type]["limit"]

    @abstractmethod
    async def match(self, question: str, language: str = None):
        """
        Return a list of results obtained by applying the matching process.

        Parameters
        ----------
        question : str
            User input to match with database entries
        language : str, optional
            Language of the question and answers

        Returns
        -------
        list of dict
            List of dictionaries containing the matching results

        """
        pass


class ExactMatch(Matching):
    """
    A class that implements exact matching, looking for results that contains the exact question sample.
    """
    def __init__(self):
        self.match_type = "exact_match"
        Matching.__init__(self, self.match_type)

    async def match(self, question: str, language: str = None):

        # Convert both the 'question' column and the search string to lowercase to perform a case-insensitive search
        question = f"%{question.lower()}%"

        rows = await queries.exact_match(question, language=language, k=self.limit)

        # Convert the results to a list of dictionaries
        matches = [dict(row) for row in rows]
        return matches


class FuzzyMatch(Matching):
    """
    A class that implements fuzzy matching through levenshtein, return results with the lowest distance first. The
    levenshtein distance is defined as the number of changes required to get to the target string.
    """
    def __init__(self, threshold: int = 100):
        self.match_type = "exact_match"
        self.threshold = threshold
        Matching.__init__(self, self.match_type)

class TrigramMatch(Matching):
    """
    A class that implements fuzzy matching through trigram matching, return results with the highest similarity score
    first.
    A trigram is a group of three consecutive characters taken from a string. We can measure the similarity of two
    strings by counting the number of trigrams they share.
    """
    def __init__(self, threshold: int = 0.5):
        self.match_type = "exact_match"
        self.threshold = threshold
        Matching.__init__(self, self.match_type)

    async def match(self, question: str, language: str = None):

        return await queries.trigram_match(question, language=language, threshold=self.threshold, k=self.limit)


class SemanticMatch(Matching):
    """
    A class that implements semantic similarity matching, return results with the lowest distance first. The
    distance is defined as the cosine distance between question and results embedding.
    """
    def __init__(self):
        self.match_type = "semantic_similarity_match"
        Matching.__init__(self, self.match_type)

    async def match(self, question: str, language: str = None):

        rows = await queries.semantic_similarity_match(question, language=language, k=self.limit)

        # Convert the results to a list of dictionaries
        matches = [{"question": row[0],
                    "answer": row[1],
                    "url": row[2]} for row in rows]

        return matches
