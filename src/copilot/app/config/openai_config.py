import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Load OpenAI API key
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY
