import asyncpg

# Import env vars
from config.db_config import DB_PARAMS

# Function to create a db connection
async def get_db_connection():
    """Establish a database connection."""
    conn = await asyncpg.connect(**DB_PARAMS)
    return conn