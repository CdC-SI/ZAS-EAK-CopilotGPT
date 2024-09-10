import os

import httpx
from dotenv import load_dotenv
from enum import Enum

from config.config import RAGConfig, IndexingConfig
from utils.enum import Client

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_required_clients() -> dict:
    """
    Get the required API clients based on the enabled services in the configuration.

    Returns
    -------
    dict
        A dictionary of the required clients for the enabled services
    """
    required_clients = {'Embedding': IndexingConfig.Embedding.value.api}
    if RAGConfig.auto_init:
        required_clients.update({'LLM': RAGConfig.LLM.model.value.api})
        if RAGConfig.Retrieval.Reranking.auto_init:
            required_clients.update({'Reranking': RAGConfig.Retrieval.Reranking.model.value.api})
    return required_clients


def get_httpx_client() -> httpx.Client:
    """
    Get the HTTPX client with proxy settings if specified in the environment variables.

    Returns
    -------
    httpx.Client
        A HTTPX client with proxy settings if specified in the environment variables.
    """
    load_dotenv()

    # Load Proxy settings
    http_proxy = os.environ.get("HTTP_PROXY", None)
    requests_ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE", None)
    logger.info(f"HTTP_PROXY: {http_proxy}, REQUESTS_CA_BUNDLE: {requests_ca_bundle}")

    # If HTTP_PROXY is specified, create a httpx client with proxy settings
    httpx_client = None
    if http_proxy and requests_ca_bundle:
        logger.info(f"Setting up HTTP_PROXY: {http_proxy}")
        logger.info(f"Setting up REQUESTS_CA_BUNDLE: {requests_ca_bundle}")

        from httpx import Client as HTTPXClient
        httpx_client = HTTPXClient(proxy=http_proxy, verify=requests_ca_bundle)

    return httpx_client


def create_api_clients() -> dict:
    """
    Create the required API clients based on the enabled services in the configuration.

    Returns
    -------
    dict
        A dictionary of the required API clients for the enabled services.
    """
    instanced_clients = {}
    required_clients = get_required_clients()

    if required_clients:
        httpx_client = get_httpx_client()  # Handle proxy settings

        # Create required API clients
        for client in Client:
            if client in required_clients.values():
                api_key = os.environ.get(f"{client.name}_API_KEY")  # Get API key from environment variables

                match client:
                    case Client.OPENAI:
                        from openai import OpenAI
                        client_val = OpenAI(api_key=api_key, http_client=httpx_client)
                    case Client.COHERE:
                        from cohere import Client as Cohere
                        client_val = Cohere(api_key=api_key, httpx_client=httpx_client)
                    case _:
                        client_val = None

                instanced_clients.update({client.name: client_val})

    # Assign clients to variables
    service_clients = {}
    for model, client in required_clients.items():
        service_clients.update({model: instanced_clients.get(client.name)})

    return service_clients


CLIENTS = create_api_clients()
"""
A dictionary of the required API clients for the enabled services."""


class Clients(Enum):
    EMBEDDING = CLIENTS.get('Embedding')
    LLM = CLIENTS.get('LLM')
    RERANKING = CLIENTS.get('Reranking')
