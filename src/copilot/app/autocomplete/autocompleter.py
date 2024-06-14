from config.base_config import autocomplete_config
from . import matching


class Autocompleter:

    def __init__(self):
        self.exact_match = matching.ExactMatch()
        self.fuzzy_match = matching.FuzzyMatch()
        self.semantic_match = matching.SemanticMatch()

        k = autocomplete_config["results"]["limit"]
        self.limit = 'NULL' if k == matching.INF else k

        self.last_matches = []

    async def get_autocomplete(self, question: str, language: str = None, k: int = 0):
        k = self.limit if k is None else k

        # TODO: add exact match results if fuzzy with levenshtein
        fuzzy_match = await self.fuzzy_match.match(question, language)

        # If the combined results from exact match and fuzzy match are less than 5, get semantic similarity matches
        if len(fuzzy_match) >= 5:
            return fuzzy_match

        if question[-1] == " " or question[-1] == "?":

            semantic_match = await self.semantic_match.match(question, language)

            # Remove duplicates
            unique_matches = list(fuzzy_match)
            unique_matches.extend(q for q in semantic_match if q not in unique_matches)

            if k > 0:
                unique_matches = unique_matches[:k]

            self.last_matches = unique_matches
            return unique_matches

        else:

            return self.last_matches
