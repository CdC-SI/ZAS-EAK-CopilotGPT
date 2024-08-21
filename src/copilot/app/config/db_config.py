import os
from dotenv import load_dotenv
from dataclasses import dataclass


import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection parameters
@dataclass
class DBConfiguration:
    without_db: bool
    echo: bool
    
    user: str
    password: str
    database: str
    host: str
    port: int

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        self.without_db = os.getenv("RUN_WITHOUT_DB", "false").lower() in ('true', '1', 't')
        self.echo = os.getenv("DEBUG_SQL", "true").lower() in ('true', '1', 't')

        self.user = os.getenv("POSTGRES_USER", "postgres")
        self.password = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.database = os.getenv("POSTGRES_DB", "postgres")
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", "5432"))


