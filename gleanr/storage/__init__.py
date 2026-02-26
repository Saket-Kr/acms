"""Gleanr storage backends."""

from gleanr.storage.base import StorageBackend
from gleanr.storage.memory import InMemoryBackend

__all__ = [
    "StorageBackend",
    "InMemoryBackend",
]


def get_sqlite_backend() -> type:
    """Get SQLiteBackend class (lazy import to avoid requiring aiosqlite)."""
    from gleanr.storage.sqlite import SQLiteBackend

    return SQLiteBackend
