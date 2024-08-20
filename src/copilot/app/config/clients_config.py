import os
from dotenv import load_dotenv

import openai
import cohere

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from config.base_config import rag_config
from config.llm_config import SUPPORTED_GROQ_LLM_MODELS

load_dotenv()

# API keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)
COHERE_API_KEY = os.environ.get("COHERE_API_KEY", None)

# Load Proxy settings
HTTP_PROXY = os.environ.get("HTTP_PROXY", None)
REQUESTS_CA_BUNDLE = os.environ.get("REQUESTS_CA_BUNDLE", None)
logger.info(f"HTTP_PROXY: {HTTP_PROXY}, REQUESTS_CA_BUNDLE: {REQUESTS_CA_BUNDLE}")

# if HTTP_PROXY then set the proxy in openai client
httpx_client = None
if HTTP_PROXY and REQUESTS_CA_BUNDLE:
    logger.info(f"Setting up HTTP_PROXY: {HTTP_PROXY}")
    logger.info(f"Setting up REQUESTS_CA_BUNDLE: {REQUESTS_CA_BUNDLE}")

    import httpx
    httpx_client = httpx.Client(proxy=HTTP_PROXY, verify=REQUESTS_CA_BUNDLE)

# Create API clients
clientEmbed = openai.OpenAI(api_key=OPENAI_API_KEY, http_client=httpx_client)
clientLLM = clientEmbed  # default LLM client
clientRerank = cohere.Client(api_key=COHERE_API_KEY, httpx_client=httpx_client)

if rag_config["llm"]["model"] in SUPPORTED_GROQ_LLM_MODELS:
    from groq import Groq
    clientLLM = Groq(api_key=GROQ_API_KEY, http_client=httpx_client)
