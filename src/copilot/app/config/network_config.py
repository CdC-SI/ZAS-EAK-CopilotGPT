import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load CORS config
CORS_ALLOWED_ORIGINS = os.environ["CORS_ALLOWED_ORIGINS"]

REQUESTS_CA_BUNDLE = os.environ.get("REQUESTS_CA_BUNDLE", None)
if REQUESTS_CA_BUNDLE:
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Setting up CA_BUNDLE: {REQUESTS_CA_BUNDLE}")

