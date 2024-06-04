

from typing import List, Union
from database import connect

import asyncpg
import httpx
from config.base_config import autocomplete_config

# Load utility functions
from utils.db import get_db_connection
from utils.embedding import get_embedding


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

    async def get_exact_match(self, question: str, language: str = '*', k: int = None):
        """
        Search for questions that contain the exact specified string, case-insensitive.

        - **question**: string to be searched within the questions.

        Returns a list of questions that exactly match the search criteria.
        """
        conn = await get_db_connection()

        if k is None:
            k = self.k_exact_match
        elif k == -1:
            k = 'NULL'

        # Convert both the 'question' column and the search string to lowercase to perform a case-insensitive search
        search_query = f"%{question.lower()}%"
        rows = await conn.fetch(f"""
            SELECT * 
            FROM data 
            WHERE language='{language}' AND LOWER(question) LIKE '{search_query}'
            LIMIT {k}
        """)
        await conn.close()

        # Convert the results to a list of dictionaries
        matches = [dict(row) for row in rows]
        return matches

    @staticmethod
    async def get_fuzzy_match(self, question: str, language: str = '*', threshold: int = 5, k: int = None):
        """
        Search for questions with fuzzy match (levenstein-damerau distance) based on threshold, case-insensitive.

        - **question**: string to be searched within the questions.

        Returns a list of questions that match the search criteria if within the specified threshold.
        """
        conn = await connect()

        if k is None:
            k = self.k_fuzzy_match
        elif k == -1:
            k = 'NULL'

        # Fetch all rows from the database
        rows = await conn.fetch(f"""
            SELECT * 
            FROM data 
            WHERE language='{language}' AND levenshtein_less_equal(question, {question}, {threshold})
            ORDER BY levenshtein(question, '{question}')
            LIMIT {'NULL' if k==-1 else k}
        """)
        await conn.close()  # Close the database connection

        return rows

    async def get_semantic_similarity_match(self,
                                            question: str,
                                            language: str = '*',
                                            symbol: str = '<=>',
                                            k: int = None):
        """
        Search for questions with cosine (semantic) similarity using an embedding model, case-insensitive.

        - **question**: string to be searched within the questions.

        Returns a list of the k most similar questions based on cosine similarity.
        """
        conn = await connect()

        if k is None:
            k = self.k_semantic_match
        elif k == -1:
            k = 'NULL'

        # Make POST request to the /embed API endpoint to get the embedding
        question_embedding = get_embedding(question)[0]["embedding"]

        matches = await conn.fetch(f"""
            SELECT question, answer, url,  1 - (embedding {symbol} '{question_embedding}') AS cosine_similarity
            FROM faq_embeddings
            WHERE language='{language}'
            ORDER BY cosine_similarity desc
            LIMIT {k}
        """)

        await conn.close()  # Close the database connection

        # Convert the results to a list of dictionaries
        matches = [{"question": row[0],
                    "answer": row[1],
                    "url": row[2]} for row in matches]

        return matches

    async def get_semantic_similarity_match_l1(self, question: str, language: str = '*', k: int = None):
        return self.get_semantic_similarity_match(question, language, '<+>', k)

    async def get_semantic_similarity_match_l2(self, question: str, language: str = '*', k: int = None):
        return self.get_semantic_similarity_match(question, language, '<->', k)

    async def get_semantic_similarity_match_inner_product(self, question: str, language: str = '*', k: int = None):
        return self.get_semantic_similarity_match(question, language, '<#>', k)

    async def get_autocomplete(self, question: str, language: str = '*', k: int = -1):
        if k is None:
            k = self.k_autocomplete
        elif k == -1:
            k = 'NULL'

        match_results = await self.get_fuzzy_match(question, language)

        # If the combined results from exact match and fuzzy match are less than 5, get semantic similarity matches
        if len(match_results) < 5:

            semantic_similarity_match_results = await self.get_semantic_similarity_match(question, language)

            # Combine the results
            match_results += semantic_similarity_match_results

        # Remove duplicates
        unique_matches = []
        [unique_matches.append(i) for i in match_results if i not in unique_matches]

        if k != -1:
            unique_matches = unique_matches[:k]

        return unique_matches
