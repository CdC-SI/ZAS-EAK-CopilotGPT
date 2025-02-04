from typing import Dict, Optional, Any

# from functools import lru_cache
import asyncio

from config.llm_config_manager import llm_config_manager
from config.model_provider_registry import model_provider_registry
from clients.factories import client_factory_registry
from config.clients_config import ProxyConfig
from utils.logging import get_logger

logger = get_logger(__name__)


class ClientManager:
    """Manages creation and lifecycle of LLM clients"""

    def __init__(
        self,
        config_manager=llm_config_manager,
        provider_registry=model_provider_registry,
        factory_registry=client_factory_registry,
        proxy_config=ProxyConfig(),
    ):
        self.config_manager = config_manager
        self.provider_registry = provider_registry
        self.factory_registry = factory_registry
        self.proxy_config = proxy_config
        self._client_cache = {}
        self._lock = asyncio.Lock()

    async def _get_cached_client(self, cache_key: str):
        """Get client from cache if available"""
        async with self._lock:
            return self._client_cache.get(cache_key)

    async def _cache_client(self, cache_key: str, client: Any):
        """Cache client for reuse"""
        async with self._lock:
            self._client_cache[cache_key] = client

    def _generate_cache_key(self, model: str, config: Dict[str, Any]) -> str:
        """Generate cache key from model and config"""
        # Create deterministic string from config
        config_str = str(sorted(config.items()))
        return f"{model}:{hash(config_str)}"

    async def _cleanup_client(self, client: Any):
        """Cleanup resources for a client"""
        try:
            if hasattr(client, "aclose"):
                await client.aclose()
            elif hasattr(client, "close"):
                await asyncio.to_thread(client.close)
        except Exception as e:
            logger.warning(f"Error during client cleanup: {e}")

    async def get_llm_client(
        self,
        model: str,
        runtime_overrides: Optional[Dict[str, Any]] = None,
        force_new: bool = False,
    ) -> Any:
        """
        Get an LLM client for the specified model.

        Parameters
        ----------
        model : str
            Model identifier
        runtime_overrides : Optional[Dict[str, Any]]
            Runtime configuration overrides
        force_new : bool
            Force creation of new client instead of using cache

        Returns
        -------
        Any
            Configured LLM client

        Raises
        ------
        ValueError
            If configuration is invalid or provider not supported
        RuntimeError
            If client creation fails
        """
        try:
            # Get merged configuration
            config = self.config_manager.get_merged_config(
                model, runtime_overrides
            )

            # Get cache key and check cache unless force_new
            cache_key = self._generate_cache_key(model, config)
            if not force_new:
                cached_client = await self._get_cached_client(cache_key)
                if cached_client:
                    logger.debug(f"Using cached client for {model}")
                    return cached_client

            # Get provider and factory
            provider = self.provider_registry.get_provider(model)
            factory = self.factory_registry.get_factory(provider)

            # Create new client
            logger.info(f"Creating new client for {model} ({provider})")
            client = factory.create_client(config)

            # Cache client if not force_new
            if not force_new:
                await self._cache_client(cache_key, client)

            return client

        except ValueError as e:
            logger.error(f"Invalid configuration for {model}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating client for {model}: {e}")
            raise RuntimeError(f"Failed to create client: {str(e)}")

    async def cleanup(self):
        """Cleanup all cached clients"""
        async with self._lock:
            for client in self._client_cache.values():
                await self._cleanup_client(client)
            self._client_cache.clear()

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        await self.cleanup()


# Create singleton instance
client_manager = ClientManager()
