import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Database connection parameters
@dataclass
class DBConfiguration:
    enabled: bool
    user: str
    password: str
    database: str
    host: str
    port: int

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        self.enabled = os.getenv("ENABLED", "true").lower() in ('true', '1', 't')

        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.database = os.getenv("POSTGRES_DB", "postgres")
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", "5432"))


