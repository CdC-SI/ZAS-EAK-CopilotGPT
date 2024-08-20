import os
from dotenv import load_dotenv
import openai
from groq import Groq
import logging
from config.base_config import rag_config
from config.llm_config import SUPPORTED_OPENAI_LLM_MODELS, SUPPORTED_GROQ_LLM_MODELS

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)

# Load Proxy
HTTP_PROXY = os.environ.get("HTTP_PROXY", None)
REQUESTS_CA_BUNDLE = os.environ.get("REQUESTS_CA_BUNDLE", None)

# Set API key
if rag_config["llm"]["model"] in SUPPORTED_OPENAI_LLM_MODELS:
    clientAI = openai.OpenAI(
        api_key=OPENAI_API_KEY,
    )
    EmbeddingClientAI = openai.OpenAI(
        api_key=OPENAI_API_KEY,
    )
elif rag_config["llm"]["model"] in SUPPORTED_GROQ_LLM_MODELS:
    clientAI = Groq(
        api_key=GROQ_API_KEY,
    )
    EmbeddingClientAI = openai.OpenAI(
        api_key=OPENAI_API_KEY,
    )

# if HTTP_PROXY then set the proxy in openai client
if HTTP_PROXY and REQUESTS_CA_BUNDLE:
    logger = logging.getLogger(__name__)
    logger.info(f"Setting up HTTP_PROXY: {HTTP_PROXY}")
    logger.info(f"Setting up REQUESTS_CA_BUNDLE: {REQUESTS_CA_BUNDLE}")

    import httpx
    clientAI.http_client = httpx.Client(proxy=HTTP_PROXY, verify=REQUESTS_CA_BUNDLE)

    EmbeddingClientAI.http_client = httpx.Client(proxy=HTTP_PROXY, verify=REQUESTS_CA_BUNDLE)
