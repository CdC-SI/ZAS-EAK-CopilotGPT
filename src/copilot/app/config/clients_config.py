import os
from dotenv import load_dotenv

import openai
import cohere
import deepl

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from config.base_config import rag_config
from config.llm_config import (
    SUPPORTED_OPENAI_LLM_MODELS,
    SUPPORTED_AZUREOPENAI_LLM_MODELS,
    SUPPORTED_ANTHROPIC_LLM_MODELS,
    SUPPORTED_GROQ_LLM_MODELS,
    SUPPORTED_OPENAI_EMBEDDING_MODELS,
    SUPPORTED_AZUREOPENAI_EMBEDDING_MODELS,
    SUPPORTED_OLLAMA_LLM_MODELS,
)

load_dotenv()

# API keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
AZUREOPENAI_API_KEY = os.environ.get("AZUREOPENAI_API_KEY", None)
AZUREOPENAI_API_VERSION = os.environ.get("AZUREOPENAI_API_VERSION", None)
AZUREOPENAI_ENDPOINT = os.environ.get("AZUREOPENAI_ENDPOINT", None)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", None)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)
COHERE_API_KEY = os.environ.get("COHERE_API_KEY", None)
DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY", None)
LLM_GENERATION_ENDPOINT = os.environ.get("LLM_GENERATION_ENDPOINT", None)

# Load Proxy settings
HTTP_PROXY = os.environ.get("HTTP_PROXY", None)
REQUESTS_CA_BUNDLE = os.environ.get("REQUESTS_CA_BUNDLE", None)
logger.info(
    f"HTTP_PROXY: {HTTP_PROXY}, REQUESTS_CA_BUNDLE: {REQUESTS_CA_BUNDLE}"
)


def setup_httpx_client():
    """Initialize httpx client with proxy settings once at boot."""
    if HTTP_PROXY and REQUESTS_CA_BUNDLE:
        import httpx

        logger.info(f"Setting up HTTP_PROXY: {HTTP_PROXY}")
        logger.info(f"Setting up REQUESTS_CA_BUNDLE: {REQUESTS_CA_BUNDLE}")
        return httpx.AsyncClient(proxy=HTTP_PROXY, verify=REQUESTS_CA_BUNDLE)
    return None


# Initialize proxy client at boot time
httpx_client = setup_httpx_client()


def create_llm_client(llm_model: str):
    """Factory function to create LLM client instances."""
    if llm_model in SUPPORTED_OPENAI_LLM_MODELS and OPENAI_API_KEY:
        return openai.AsyncOpenAI(
            api_key=OPENAI_API_KEY, http_client=httpx_client
        )
    elif llm_model in SUPPORTED_AZUREOPENAI_LLM_MODELS and AZUREOPENAI_API_KEY:
        return openai.AsyncAzureOpenAI(
            api_key=AZUREOPENAI_API_KEY,
            api_version=AZUREOPENAI_API_VERSION,
            azure_endpoint=AZUREOPENAI_ENDPOINT,
            http_client=httpx_client,
        )
    elif llm_model in SUPPORTED_ANTHROPIC_LLM_MODELS and ANTHROPIC_API_KEY:
        from anthropic import AsyncAnthropic

        return AsyncAnthropic(
            api_key=ANTHROPIC_API_KEY, http_client=httpx_client
        )
    elif llm_model in SUPPORTED_GROQ_LLM_MODELS and GROQ_API_KEY:
        from groq import AsyncGroq

        return AsyncGroq(api_key=GROQ_API_KEY, http_client=httpx_client)
    elif llm_model in SUPPORTED_OLLAMA_LLM_MODELS:
        from ollama import AsyncClient

        return AsyncClient(
            host=LLM_GENERATION_ENDPOINT,
            proxy=HTTP_PROXY,
            verify=REQUESTS_CA_BUNDLE,
        )
    return None


# Initialize default client at boot time
default_llm_model = rag_config["llm"]["model"]
clientLLM = create_llm_client(default_llm_model)

clientEmbed = None
default_embedding_model = rag_config["embedding"]["model"]

# Initialize Embedding client
if (
    default_embedding_model in SUPPORTED_OPENAI_EMBEDDING_MODELS
    and OPENAI_API_KEY
):
    clientEmbed = openai.AsyncOpenAI(
        api_key=OPENAI_API_KEY, http_client=httpx_client
    )
elif (
    default_embedding_model in SUPPORTED_AZUREOPENAI_EMBEDDING_MODELS
    and AZUREOPENAI_API_KEY
):
    clientEmbed = openai.AsyncAzureOpenAI(
        api_key=AZUREOPENAI_API_KEY,
        api_version=AZUREOPENAI_API_VERSION,
        azure_endpoint=AZUREOPENAI_ENDPOINT,
        http_client=httpx_client,
    )

if COHERE_API_KEY:
    clientRerank = cohere.AsyncClient(
        api_key=COHERE_API_KEY, httpx_client=httpx_client
    )
else:
    clientRerank = None

if DEEPL_API_KEY:
    clientDeepl = deepl.DeepLClient(
        auth_key=DEEPL_API_KEY, proxy=HTTP_PROXY, verify_ssl=REQUESTS_CA_BUNDLE
    )
else:
    clientDeepl = None
