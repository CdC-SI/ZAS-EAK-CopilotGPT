from config.base_config import autocomplete_config
from . import matching


class Autocompleter:
    """
    Completer for user input to the copilot
    """

    def __init__(self):
        self.exact_match = matching.ExactMatch()
        self.fuzzy_match = matching.FuzzyMatch()
        self.semantic_match = matching.SemanticMatch()

        k = autocomplete_config["results"]["limit"]
        self.limit = 'NULL' if k == matching.INF else k

        self.semantic_matches_cache = []

    async def get_autocomplete(self, question: str, language: str = None, k: int = 0):
        """
        Returns matching results according to a defined behaviour

        Parameters
        ----------
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
        k = self.limit if k is None else k

        # TODO: add exact match results if fuzzy with levenshtein
        exact_match = await self.exact_match.match(question, language)
        fuzzy_match = await self.fuzzy_match.match(question, language)

        unique_matches = exact_match + fuzzy_match

        # Remove duplicate matches and preserve order
        seen = []
        unique_matches = [seen.append(d) for d in unique_matches if d not in seen]
        unique_matches = seen

        # If the combined results from exact match and fuzzy match are more than 5, return results
        if len(unique_matches) >= 5:
            return unique_matches

        # If the combined results from exact match and fuzzy match are less than 5, and the question ends with a space or a question mark, perform semantic matching
        if question[-1] == " " or question[-1] == "?":

            semantic_match = await self.semantic_match.match(question, language)

            # Remove duplicates
            unique_matches = unique_matches + semantic_match
            unique_matches = [seen.append(d) for d in unique_matches if d not in seen]
            unique_matches = seen

            if k > 0:
                unique_matches = unique_matches[:k]

            #self.last_matches = unique_matches
            return unique_matches

        return unique_matches
