
import asyncpg
from config import DB_PARAMS


def connect() -> asyncpg.connection:
    """Establish a database connection."""
    conn = asyncpg.connect(**DB_PARAMS)

    return conn


async def fetch(query: str):
    conn = connect()
    try:
        # Fetch all rows from the database
        rows = await conn.fetch(query)
        await conn.close()  # Close the database connection

    except Exception as e:
        await conn.close()
        raise e


def exact_condition(question: str):
    search_query = f"%{question.lower()}%"
    return f"LOWER(question) LIKE {search_query}"