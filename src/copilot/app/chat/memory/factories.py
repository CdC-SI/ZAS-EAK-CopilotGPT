from typing import Type, Optional

from .enums import MemoryType
from .storage.redis_handler import RedisMemoryHandler
from .storage.postgres_handler import PostgresMemoryHandler
from .strategies.base import BaseMemoryStrategy
from .strategies.buffer import ConversationalMemoryBuffer
from .strategies.summary import ConversationalMemorySummary
from .strategies.buffer_summary import ConversationalMemoryBufferSummary
from .interfaces.storage import BaseStorage, DatabaseStorage
from .exceptions import InvalidMemoryTypeError, MemoryStrategyError
from .config import StorageConfig


class MemoryStrategyFactory:
    """Factory for creating memory strategy instances."""

    _strategies = {
        MemoryType.BUFFER: ConversationalMemoryBuffer,
        MemoryType.SUMMARY: ConversationalMemorySummary,
        MemoryType.BUFFER_SUMMARY: ConversationalMemoryBufferSummary,
    }

    @classmethod
    def get_strategy_class(
        cls, memory_type: MemoryType
    ) -> Type[BaseMemoryStrategy]:
        """Get the strategy class for the given memory type."""
        strategy_class = cls._strategies.get(memory_type)
        if not strategy_class:
            raise InvalidMemoryTypeError(f"Invalid memory type: {memory_type}")
        return strategy_class

    @classmethod
    def create_storage_handlers(
        cls, config: Optional[StorageConfig] = None, k_memory: int = 1
    ) -> tuple[BaseStorage, DatabaseStorage]:
        """Create storage handler instances with configuration."""
        config = config or StorageConfig()
        cache_storage = RedisMemoryHandler(
            k_memory=k_memory, config=config.redis
        )
        db_storage = PostgresMemoryHandler()
        return cache_storage, db_storage

    @classmethod
    def create_strategy(
        cls,
        memory_type: MemoryType,
        k_memory: int,
        cache_storage: Optional[BaseStorage] = None,
        db_storage: Optional[DatabaseStorage] = None,
        config: Optional[StorageConfig] = None,
    ) -> BaseMemoryStrategy:
        """Create a strategy instance with the given configuration."""
        try:
            if cache_storage is None or db_storage is None:
                cache_storage, db_storage = cls.create_storage_handlers(
                    config, k_memory
                )

            strategy_class = cls.get_strategy_class(memory_type)
            return strategy_class(
                cache_storage=cache_storage,
                db_storage=db_storage,
                k_memory=k_memory,
            )
        except InvalidMemoryTypeError:
            raise
        except Exception as e:
            raise MemoryStrategyError(f"Failed to create memory strategy: {e}")
