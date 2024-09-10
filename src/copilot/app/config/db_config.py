import os
from dotenv import load_dotenv
from dataclasses import dataclass


# Database connection parameters
@dataclass
class DBConfiguration:
    """
    Dataclass for database connection parameters.
    """
    enabled: bool
    echo: bool

    user: str
    password: str
    database: str
    host: str
    port: int

    url: str

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        self.enabled = os.getenv("DB_ENABLED", "true").lower() in ('true', '1', 't')
        self.echo = os.getenv("DEBUG_SQL", "true").lower() in ('true', '1', 't')

        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.database = os.getenv("POSTGRES_DB", "postgres")
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", "5432"))

        self.url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


DBCONFIG = DBConfiguration()
"""
Database connection parameters."""
