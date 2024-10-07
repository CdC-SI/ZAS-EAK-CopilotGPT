import os
from dotenv import load_dotenv

import openai
from openai import AzureOpenAI
import cohere

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from config.base_config import rag_config
from config.llm_config import SUPPORTED_OPENAI_LLM_MODELS, SUPPORTED_AZUREOPENAI_LLM_MODELS, SUPPORTED_ANTHROPIC_LLM_MODELS, SUPPORTED_GROQ_LLM_MODELS, SUPPORTED_OPENAI_EMBEDDING_MODELS, SUPPORTED_AZUREOPENAI_EMBEDDING_MODELS

load_dotenv()

# API keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
AZUREOPENAI_API_KEY = os.environ.get("AZUREOPENAI_API_KEY", None)
AZUREOPENAI_API_VERSION = os.environ.get("AZUREOPENAI_API_VERSION", None)
AZUREOPENAI_ENDPOINT = os.environ.get("AZUREOPENAI_ENDPOINT", None)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", None)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)
COHERE_API_KEY = os.environ.get("COHERE_API_KEY", None)

# LLM model
llm_model = rag_config["llm"]["model"]
embedding_model = rag_config["embedding"]["model"]

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

clientLLM = None
clientEmbed = None

# Initialize Embedding client
if embedding_model in SUPPORTED_OPENAI_EMBEDDING_MODELS and OPENAI_API_KEY:
    clientEmbed = openai.OpenAI(api_key=OPENAI_API_KEY, http_client=httpx_client)
elif embedding_model in SUPPORTED_AZUREOPENAI_EMBEDDING_MODELS and AZUREOPENAI_API_KEY:
    clientEmbed = AzureOpenAI(
        api_key=AZUREOPENAI_API_KEY,
        api_version=AZUREOPENAI_API_VERSION,
        azure_endpoint=AZUREOPENAI_ENDPOINT,
        http_client=httpx_client
    )

# Initialize LLM client based on OpenAI, AzureOpenAI or Groq model
if llm_model in SUPPORTED_OPENAI_LLM_MODELS and OPENAI_API_KEY:
    clientLLM = openai.OpenAI(api_key=OPENAI_API_KEY, http_client=httpx_client)
elif llm_model in SUPPORTED_AZUREOPENAI_LLM_MODELS and AZUREOPENAI_API_KEY:
    clientLLM = AzureOpenAI(
        api_key=AZUREOPENAI_API_KEY,
        api_version=AZUREOPENAI_API_VERSION,
        azure_endpoint=AZUREOPENAI_ENDPOINT,
        http_client=httpx_client
    )
elif llm_model in SUPPORTED_ANTHROPIC_LLM_MODELS and ANTHROPIC_API_KEY:
    from anthropic import Anthropic
    clientLLM = Anthropic(api_key=ANTHROPIC_API_KEY, http_client=httpx_client)
elif llm_model in SUPPORTED_GROQ_LLM_MODELS and GROQ_API_KEY:
    from groq import Groq
    clientLLM = Groq(api_key=GROQ_API_KEY, http_client=httpx_client)

clientRerank = cohere.Client(api_key=COHERE_API_KEY, httpx_client=httpx_client)

logger.info(f"---------LLMMODEL: {llm_model}---------")
logger.info(f"---------CLIENTLLM: {clientLLM}, CLIENTEMBED: {clientEmbed}, CLIENTRERANK: {clientRerank}---------")
