import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load OpenAI API key
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Load PostgreSQL database credentials
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

# Database connection parameters
DB_PARAMS = {
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "database": POSTGRES_DB,
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT,
}

# Set OpenAI API key
import openai
openai.api_key = OPENAI_API_KEY