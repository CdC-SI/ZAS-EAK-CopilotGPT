from typing import Union
import asyncpg
from config.db_config import DB_PARAMS

from utils.embedding import get_embedding


class FAQDatabase:

    def connect(self) -> asyncpg.connection:
        """Establish a database connection."""
        conn = asyncpg.connect(**DB_PARAMS)

        return conn

    async def fetch(self, db_name: str, select: [str] = None, where: [str] = None, language: str = '*', order: str = 'question', k: int = -1):
        conn = await self.connect()

        selection = ', '.join(['question', 'answer', 'url']+select)
        conditions = ' AND '.join([f"language='{language}'"]+where)
        k = 'NULL' if k == -1 else k

        try:
            rows = await conn.fetch(f"""
                SELECT {selection}
                FROM {db_name}
                WHERE {conditions}
                ORDER BY {order}
                LIMIT {k}
            """)

        finally:
            await conn.close()

        return rows

    async def exact_match(self, question: str, language: str = '*', k: int = -1):
        return await self.fetch('data',
                                where=[f"LOWER(question) LIKE '{question}'"],
                                language=language,
                                k=k)

    async def fuzzy_match(self, question: str, language: str = '*', threshold: int = 5, k: int = -1):
        return await self.fetch('data',
                                where=[f"levenshtein_less_equal(question, '{question}', {threshold}"],
                                language=language,
                                order=f"levenshtein(question, '{question}') desc",
                                k=k)

    async def semantic_similarity_match(self,
                                        question: str,
                                        language: str = '*',
                                        symbol: str = '<=>',
                                        k: int = -1):
        # Make POST request to the /embed API endpoint to get the embedding
        question_embedding = get_embedding(question)[0]["embedding"]

        return await self.fetch('faq_embeddings',
                                select=[f"1 - (embedding {symbol} '{question_embedding}') AS cosine_similarity"],
                                language=language,
                                order="cosine_similarity desc",
                                k=k)

    async def semantic_similarity_match_l1(self, question: str, language: str = '*', k: int = -1):
        return self.semantic_similarity_match(question, language, '<+>', k)

    async def semantic_similarity_match_l2(self, question: str, language: str = '*', k: int = -1):
        return self.semantic_similarity_match(question, language, '<->', k)

    async def semantic_similarity_match_inner_prod(self, question: str, language: str = '*', k: int = -1):
        return self.semantic_similarity_match(question, language, '<#>', k)
