import queries

from config.base_config import autocomplete_config


class Autocompleter:

    def __init__(self):
        k = autocomplete_config["exact_match"]["limit"]
        self.k_exact_match = 'NULL' if k == -1 else k

        k = autocomplete_config["fuzzy_match"]["limit"]
        self.k_fuzzy_match = 'NULL' if k == -1 else k

        k = autocomplete_config["semantic_similarity_match"]["limit"]
        self.k_semantic_match = 'NULL' if k == -1 else k

        k = autocomplete_config["results"]["limit"]
        self.k_autocomplete = 'NULL' if k == -1 else k

        self.last_matches = []

    async def get_exact_match(self, question: str, language: str = '*', k: int = None):
        """
        Search for questions that contain the exact specified string, case-insensitive.

        - **question**: string to be searched within the questions.

        Returns a list of questions that exactly match the search criteria.
        """
        k = self.k_exact_match if k is None else k

        # Convert both the 'question' column and the search string to lowercase to perform a case-insensitive search
        question = f"%{question.lower()}%"

        rows = await queries.exact_match(question, language=language, k=k)

        # Convert the results to a list of dictionaries
        matches = [dict(row) for row in rows]
        return matches

    async def get_fuzzy_match(self, question: str, language: str = '*', threshold: int = 5, k: int = None):
        """
        Search for questions with fuzzy match (levenstein-damerau distance) based on threshold, case-insensitive.

        - **question**: string to be searched within the questions.

        Returns a list of questions that match the search criteria if within the specified threshold.
        """
        k = self.k_fuzzy_match if k is None else k

        return await queries.fuzzy_match(question, language=language, threshold=threshold, k=k)

    async def get_semantic_similarity_match(self, question: str, language: str = '*', k: int = -1):
        k = self.k_semantic_match if k is None else k

        rows = await queries.semantic_similarity_match(question, language=language, k=k)

        # Convert the results to a list of dictionaries
        matches = [{"question": row[0],
                    "answer": row[1],
                    "url": row[2]} for row in rows]

        return matches

    async def get_autocomplete(self, question: str, language: str = '*', k: int = -1):
        k = self.k_autocomplete if k is None else k

        fuzzy_match = await self.get_fuzzy_match(question, language)

        # If the combined results from exact match and fuzzy match are less than 5, get semantic similarity matches
        if len(fuzzy_match) < 5 and (question[-1] == " " or question[-1] == "?"):

            semantic_match = await self.get_semantic_similarity_match(question, language)

            # Remove duplicates
            unique_matches = list(fuzzy_match)
            unique_matches.extend(q for q in semantic_match if q not in unique_matches)

            if k != -1:
                unique_matches = unique_matches[:k]

            self.last_matches = unique_matches
            return unique_matches

        else:

            return self.last_matches
