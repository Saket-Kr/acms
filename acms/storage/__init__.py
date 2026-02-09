"""ACMS storage backends."""

from acms.storage.base import StorageBackend
from acms.storage.memory import InMemoryBackend

__all__ = [
    "StorageBackend",
    "InMemoryBackend",
]


def get_sqlite_backend() -> type:
    """Get SQLiteBackend class (lazy import to avoid requiring aiosqlite)."""
    from acms.storage.sqlite import SQLiteBackend

    return SQLiteBackend
