from utils.embedding import get_embedding
from utils.db import get_db_connection


async def fetch(db_name: str, select: [str] = None, where: [str] = None, language: str = '*', order: str = 'question',
                k: int = -1):
    conn = await get_db_connection()

    selection = ', '.join(['question', 'answer', 'url'] + select)
    conditions = ' AND '.join([f"language='{language}'"] + where)
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


def exact_match(question: str, language: str = '*', k: int = -1):
    return fetch('data',
                 where=[f"LOWER(question) LIKE '{question}'"],
                 language=language,
                 k=k)


def fuzzy_match(question: str, language: str = '*', threshold: int = 5, k: int = -1):
    return fetch('data',
                 where=[f"levenshtein_less_equal(question, '{question}', {threshold}"],
                 language=language,
                 order=f"levenshtein(question, '{question}') desc",
                 k=k)


def semantic_similarity_match(question: str,
                                    db_name: str = 'faq_embeddings',
                                    language: str = '*',
                                    symbol: str = '<=>',
                                    k: int = -1):
    # Make POST request to the /embed API endpoint to get the embedding
    question_embedding = get_embedding(question)[0]["embedding"]

    return fetch(db_name,
                 select=[f"1 - (embedding {symbol} '{question_embedding}') AS cosine_similarity"],
                 language=language,
                 order="cosine_similarity desc",
                 k=k)


def semantic_similarity_match_l1(question: str, language: str = '*', k: int = -1):
    return semantic_similarity_match(question, language, symbol='<+>', k=k)


def semantic_similarity_match_l2(question: str, language: str = '*', k: int = -1):
    return semantic_similarity_match(question, language, symbol='<->', k=k)


def semantic_similarity_match_inner_prod(question: str, language: str = '*', k: int = -1):
    return semantic_similarity_match(question, language, symbol='<#>', k=k)
