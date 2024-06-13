from autocomplete.app import queries

from config.base_config import autocomplete_config


class Autocompleter:

    def __init__(self):
        self.k_exact_match = autocomplete_config["exact_match"]["limit"]
        self.k_fuzzy_match = autocomplete_config["fuzzy_match"]["limit"]
        self.fuzzy_match_threshold = autocomplete_config["fuzzy_match"]["threshold"]
        self.k_semantic_match = autocomplete_config["semantic_similarity_match"]["limit"]
        self.k_autocomplete = autocomplete_config["results"]["limit"]

        self.last_matches = []

    async def get_exact_match(self, question: str, language: str = None, k: int = 0):
        """
        Search for questions that contain the exact specified string, case-insensitive.

        - **question**: string to be searched within the questions.

        Returns a list of questions that exactly match the search criteria.
        """
        k = self.k_exact_match if k == 0 else k

        # Convert both the 'question' column and the search string to lowercase to perform a case-insensitive search
        question = f"%{question.lower()}%"

        rows = await queries.exact_match(question, language=language, k=k)

        # Convert the results to a list of dictionaries
        matches = [dict(row) for row in rows]
        return matches

    async def get_fuzzy_match(self, question: str, language: str = None, threshold: int = None, k: int = 0):
        """
        Search for questions with fuzzy match (levenstein-damerau distance) based on threshold, case-insensitive.

        - **question**: string to be searched within the questions.

        Returns a list of questions that match the search criteria if within the specified threshold.
        """
        k = self.k_fuzzy_match if k == 0 else k
        threshold = threshold if threshold else self.fuzzy_match_threshold

        rows = await queries.fuzzy_match(question=question, threshold=threshold, language=language, k=k)

        matches = [dict(row) for row in rows]
        return matches

    async def get_semantic_similarity_match(self, question: str, language: str = None, k: int = 0):
        k = self.k_semantic_match if k == 0 else k

        rows = await queries.semantic_similarity_match(question=question, language=language, k=k)

        # Convert the results to a list of dictionaries
        matches = [{"question": row[0],
                    "answer": row[1],
                    "url": row[2]} for row in rows]

        return matches

    async def get_autocomplete(self, question: str, language: str = None, k: int = 0):
        k = self.k_autocomplete if k == 0 else k

        fuzzy_match = await queries.exact_or_fuzzy(question=question, threshold=self.fuzzy_match_threshold, language=language)

        # If the combined results from exact match and fuzzy match are less than 5, get semantic similarity matches
        if len(fuzzy_match) < 5 and (question[-1] == " " or question[-1] == "?"):

            semantic_match = await self.get_semantic_similarity_match(question, language)

            # Remove duplicates
            unique_matches = list(fuzzy_match)
            unique_matches.extend(q for q in semantic_match if q not in unique_matches)

            if k != 0:
                unique_matches = unique_matches[:k]

            self.last_matches = unique_matches
            return unique_matches

        else:

            return fuzzy_match
