import os
from dotenv import load_dotenv
import openai

import logging

# Load environment variables from .env file
load_dotenv()

# Load OpenAI API key
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
HTTP_PROXY = os.environ.get("HTTP_PROXY", "noproxy")

# if HTTP_PROXY not noproxy then set the proxy in openai client
if HTTP_PROXY != "noproxy":
    logger = logging.getLogger(__name__)
    logger.info(f"Setting up HTTP_PROXY: {HTTP_PROXY}")

# Load OpenAI API key
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY
