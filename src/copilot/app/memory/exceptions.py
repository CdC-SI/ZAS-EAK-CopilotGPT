class MemoryErrorBase(Exception):
    """Base exception class for memory-related errors."""

    pass


class StorageError(MemoryErrorBase):
    """Raised when there's an error with Redis or Postgres storage operations."""

    pass


class RedisStorageError(StorageError):
    """Raised when there's an error with Redis operations."""

    pass


class PostgresStorageError(StorageError):
    """Raised when there's an error with Postgres operations."""

    pass


class MemoryStrategyError(MemoryErrorBase):
    """Raised when there's an error with memory strategy initialization or usage."""

    pass


class InvalidMemoryTypeError(MemoryStrategyError):
    """Raised when an invalid memory type is provided."""

    pass
