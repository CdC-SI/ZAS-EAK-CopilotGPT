

from typing import List, Union
from database import connect

import asyncpg
import httpx


class Autocompleter:

    def __init__(self, rag_addr: str = "http://rag:8010/rag"):
        self.rag_addr = rag_addr

    @staticmethod
    async def get_exact_match(self, question: str, language: str = '*'):
        """
        Search for questions that contain the exact specified string, case-insensitive.

        - **question**: string to be searched within the questions.

        Returns a list of questions that exactly match the search criteria.
        """
        conn = await connect()

        # Convert both the 'question' column and the search string to lowercase to perform a case-insensitive search
        search_query = f"%{question.lower()}%"
        rows = await conn.fetch(f"SELECT * FROM data WHERE language={language} AND LOWER(question) LIKE {search_query}")
        await conn.close()

        # Convert the results to a list of dictionaries
        matches = [dict(row) for row in rows]
        return matches

    @staticmethod
    async def get_fuzzy_match(self, question: str, language: str = '*', threshold: int = 5):
        """
        Search for questions with fuzzy match (levenstein-damerau distance) based on threshold, case-insensitive.

        - **question**: string to be searched within the questions.

        Returns a list of questions that match the search criteria if within the specified threshold.
        """
        conn = await connect()

        # Fetch all rows from the database
        rows = await conn.fetch(f"SELECT * FROM data WHERE language={language} AND levenshtein_less_equal(question, {question}, {threshold})")
        await conn.close()  # Close the database connection

        return rows


    async def get_semantic_similarity_match(self, question: str, language: str = '*', k: int = 5):
        """
        Search for questions with cosine (semantic) similarity using an embedding model, case-insensitive.

        - **question**: string to be searched within the questions.

        Returns a list of the k most similar questions based on cosine similarity.
        """
        conn = await connect()

        # Make POST request to the /embed API endpoint to get the embedding
        async with httpx.AsyncClient() as client:
            response = await client.post(self.rag_addr + "/embed", json={"text": question})

        # Ensure the request was successful
        response.raise_for_status()

        # Get the resulting embedding vector from the response
        question_embedding = response.json()["data"][0]["embedding"]

        matches = await conn.fetch(f"""
            SELECT question, answer, url,  1 - (embedding <=> '{question_embedding}') AS cosine_similarity
            FROM faq_embeddings
            WHERE language={language}
            ORDER BY cosine_similarity desc
            LIMIT {k}
        """)

        await conn.close()  # Close the database connection

        # Convert the results to a list of dictionaries
        matches = [{"question": row[0],
                    "answer": row[1],
                    "url": row[2]} for row in matches]

        return matches

    async def get_autocomplete(self, question: str, language: str = '*'):

        match_results = await self.get_fuzzy_match(question, language)

        # If the combined results from exact match and fuzzy match are less than 5, get semantic similarity matches
        if len(match_results) < 5:

            semantic_similarity_match_results = await self.get_semantic_similarity_match(question, language)

            # Combine the results
            match_results += semantic_similarity_match_results

        # Remove duplicates
        unique_matches = []
        [unique_matches.append(i) for i in match_results if i not in unique_matches]

        return unique_matches
