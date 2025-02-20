import os
from dataclasses import dataclass
from typing import Optional
import httpx
from dotenv import load_dotenv

import openai
import cohere
import deepl

from utils.logging import get_logger

logger = get_logger(__name__)

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


@dataclass
class EnvironmentConfig:
    """
    Configuration class for storing API keys and endpoints.

    Parameters
    ----------
    openai_api_key : str, optional
        API key for OpenAI services
    azure_openai_api_key : str, optional
        API key for Azure OpenAI services
    azure_openai_api_version : str, optional
        API version for Azure OpenAI
    azure_openai_endpoint : str, optional
        Endpoint URL for Azure OpenAI
    anthropic_api_key : str, optional
        API key for Anthropic services
    groq_api_key : str, optional
        API key for Groq services
    cohere_api_key : str, optional
        API key for Cohere services
    deepl_api_key : str, optional
        API key for DeepL translation services
    llm_generation_endpoint : str, optional
        Endpoint for local LLM generation
    """

    openai_api_key: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_api_version: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    deepl_api_key: Optional[str] = None
    llm_generation_endpoint: Optional[str] = None


class ProxyConfig:
    """
    Configuration class for HTTP proxy settings.
    """

    def __init__(self):
        self.http_proxy = os.environ.get("HTTP_PROXY")
        self.ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE")

    def setup_httpx_client(self) -> Optional[httpx.AsyncClient]:
        """
        Set up an httpx client with proxy configuration.

        Returns
        -------
        httpx.AsyncClient or None
            Configured httpx client if proxy settings exist, None otherwise
        """
        if self.http_proxy and self.ca_bundle:
            return httpx.AsyncClient(
                proxy=self.http_proxy, verify=self.ca_bundle
            )
        return None


class ClientFactory:
    """
    Factory class for creating various API clients.

    Parameters
    ----------
    env_config : EnvironmentConfig
        Environment configuration containing API keys
    proxy_config : ProxyConfig
        Proxy configuration for HTTP requests
    """

    def __init__(
        self, env_config: EnvironmentConfig, proxy_config: ProxyConfig
    ):
        self.env_config = env_config
        self.proxy_config = proxy_config
        self.httpx_client = proxy_config.setup_httpx_client()

    def create_llm_client(self, model: str):
        """
        Create a language model client based on the model type.

        Parameters
        ----------
        model : str
            Name of the LLM model to use

        Returns
        -------
        object or None
            Appropriate client instance for the specified model
        """
        if (
            model in SUPPORTED_OPENAI_LLM_MODELS
            and self.env_config.openai_api_key
        ):
            return openai.AsyncOpenAI(
                api_key=self.env_config.openai_api_key,
                http_client=self.httpx_client,
            )
        elif (
            model in SUPPORTED_AZUREOPENAI_LLM_MODELS
            and self.env_config.azure_openai_api_key
        ):
            return openai.AsyncAzureOpenAI(
                api_key=self.env_config.azure_openai_api_key,
                api_version=self.env_config.azure_openai_api_version,
                azure_endpoint=self.env_config.azure_openai_endpoint,
                http_client=self.httpx_client,
            )
        elif (
            model in SUPPORTED_ANTHROPIC_LLM_MODELS
            and self.env_config.anthropic_api_key
        ):
            from anthropic import AsyncAnthropic

            return AsyncAnthropic(
                api_key=self.env_config.anthropic_api_key,
                http_client=self.httpx_client,
            )
        elif (
            model in SUPPORTED_GROQ_LLM_MODELS and self.env_config.groq_api_key
        ):
            from groq import AsyncGroq

            return AsyncGroq(
                api_key=self.env_config.groq_api_key,
                http_client=self.httpx_client,
            )
        elif model in SUPPORTED_OLLAMA_LLM_MODELS:
            from ollama import AsyncClient

            return AsyncClient(
                host=self.env_config.llm_generation_endpoint,
                proxy=self.proxy_config.http_proxy,
                verify=self.proxy_config.ca_bundle,
            )
        return None

    def create_embedding_client(self, model: str):
        """
        Create an embedding model client.

        Parameters
        ----------
        model : str
            Name of the embedding model to use

        Returns
        -------
        object or None
            OpenAI or Azure OpenAI client for embeddings
        """
        if (
            model in SUPPORTED_OPENAI_EMBEDDING_MODELS
            and self.env_config.openai_api_key
        ):
            return openai.AsyncOpenAI(
                api_key=self.env_config.openai_api_key,
                http_client=self.httpx_client,
            )
        elif (
            model in SUPPORTED_AZUREOPENAI_EMBEDDING_MODELS
            and self.env_config.azure_openai_api_key
        ):
            return openai.AsyncAzureOpenAI(
                api_key=self.env_config.azure_openai_api_key,
                api_version=self.env_config.azure_openai_api_version,
                azure_endpoint=self.env_config.azure_openai_endpoint,
                http_client=self.httpx_client,
            )
        return None

    def create_rerank_client(self):
        """
        Create a client for reranking operations.

        Returns
        -------
        cohere.AsyncClient or None
            Cohere client if API key exists, None otherwise
        """
        if self.env_config.cohere_api_key:
            return cohere.AsyncClient(
                api_key=self.env_config.cohere_api_key,
                httpx_client=self.httpx_client,
            )
        return None

    def create_translation_client(self):
        """
        Create a translation client.

        Returns
        -------
        deepl.DeepLClient or None
            DeepL client if API key exists, None otherwise
        """
        if self.env_config.deepl_api_key:
            return deepl.DeepLClient(
                auth_key=self.env_config.deepl_api_key,
                proxy=self.proxy_config.http_proxy,
                verify_ssl=self.proxy_config.ca_bundle,
            )
        return None


class ClientConfig:
    """
    Main configuration class for initializing all API clients.
    """

    def __init__(self):
        load_dotenv()
        self.env_config = EnvironmentConfig(
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            azure_openai_api_key=os.environ.get("AZUREOPENAI_API_KEY"),
            azure_openai_api_version=os.environ.get("AZUREOPENAI_API_VERSION"),
            azure_openai_endpoint=os.environ.get("AZUREOPENAI_ENDPOINT"),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
            groq_api_key=os.environ.get("GROQ_API_KEY"),
            cohere_api_key=os.environ.get("COHERE_API_KEY"),
            deepl_api_key=os.environ.get("DEEPL_API_KEY"),
            llm_generation_endpoint=os.environ.get(
                "LOCAL_LLM_GENERATION_ENDPOINT"
            ),
        )
        self.proxy_config = ProxyConfig()
        self.factory = ClientFactory(self.env_config, self.proxy_config)

        # Initialize clients
        self.client_llm = self.factory.create_llm_client(
            rag_config["llm"]["model"]
        )
        self.client_embed = self.factory.create_embedding_client(
            rag_config["embedding"]["model"]
        )
        self.client_rerank = self.factory.create_rerank_client()
        self.client_deepl = self.factory.create_translation_client()


# Initialize the configuration
config = ClientConfig()

# Export client instances for backward compatibility
clientLLM = config.client_llm
clientEmbed = config.client_embed
clientRerank = config.client_rerank
clientDeepl = config.client_deepl
