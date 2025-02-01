import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

from utils.logging import get_logger

logger = get_logger(__name__)

from .enums import MemoryType
from .exceptions import InvalidMemoryTypeError


@dataclass
class RedisConfig:
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    password: Optional[str] = os.getenv("REDIS_PASSWORD")
    db: int = 0
    decode_responses: bool = True
    cache_ttl_hours: int = int(os.getenv("REDIS_CACHE_TTL_HOURS", "72"))

    @property
    def cache_ttl_seconds(self) -> int:
        return self.cache_ttl_hours * 60 * 60

    def __post_init__(self):
        masked_config = self.__dict__.copy()
        if self.password:
            masked_config["password"] = "****"
        logger.info(f"Initialized RedisConfig: {masked_config}")


@dataclass
class StorageConfig:
    redis: RedisConfig = RedisConfig()


@dataclass
class MemoryConfig:
    memory_type: MemoryType
    k_memory: int
    storage: Optional[StorageConfig] = None

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "MemoryConfig":
        """
        Create MemoryConfig from dictionary with validation.

        Args:
            config: Dictionary containing memory configuration

        Returns:
            MemoryConfig: Validated memory configuration

        Raises:
            InvalidMemoryTypeError: If memory_type is invalid
            ValueError: If k_memory is invalid
        """
        try:
            memory_type = MemoryType(config.get("memory_type", "buffer"))
        except ValueError:
            raise InvalidMemoryTypeError(
                f"Invalid memory type: {config.get('memory_type')}. "
                f"Valid types are: {[t.value for t in MemoryType]}"
            )

        k_memory = int(config.get("k_memory", 5))
        if k_memory < 1:
            raise ValueError("k_memory must be greater than 0")

        return cls(
            memory_type=memory_type, k_memory=k_memory, storage=StorageConfig()
        )
