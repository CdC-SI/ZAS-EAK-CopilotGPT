from abc import ABCMeta, abstractmethod

from config.base_config import autocomplete_config
from . import queries

INF = 0


class Matching(metaclass=ABCMeta):
    def __init__(self, match_type: str):
        self.limit = autocomplete_config[match_type]["limit"]

    @abstractmethod
    async def match(self, question: str, language: str = None):
        pass


class ExactMatch(Matching):
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
    def __init__(self, threshold: int = 100):
        self.match_type = "exact_match"
        self.threshold = threshold
        Matching.__init__(self, self.match_type)

    async def match(self, question: str, language: str = None):

        return await queries.fuzzy_match(question, language=language, threshold=self.threshold, k=self.limit)


class SemanticMatch(Matching):
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
