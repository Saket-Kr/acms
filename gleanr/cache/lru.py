"""LRU cache implementation."""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class CacheEntry(Generic[V]):
    """A single cache entry with optional TTL tracking."""

    value: V
    created_at: float = field(default_factory=time.time)

    def is_expired(self, ttl_seconds: int | None) -> bool:
        """Check if this entry has expired."""
        if ttl_seconds is None:
            return False
        return (time.time() - self.created_at) > ttl_seconds


class LRUCache(Generic[K, V]):
    """Thread-safe LRU cache with optional TTL.

    Uses OrderedDict for O(1) operations.
    Move-to-end on access, pop from beginning on eviction.
    """

    def __init__(
        self,
        max_size: int,
        ttl_seconds: int | None = None,
    ) -> None:
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._cache: OrderedDict[K, CacheEntry[V]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    @property
    def max_size(self) -> int:
        """Maximum cache size."""
        return self._max_size

    @property
    def size(self) -> int:
        """Current number of entries."""
        return len(self._cache)

    @property
    def hits(self) -> int:
        """Number of cache hits."""
        return self._hits

    @property
    def misses(self) -> int:
        """Number of cache misses."""
        return self._misses

    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0-1)."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    def get(self, key: K) -> V | None:
        """Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            return None

        # Check TTL
        if entry.is_expired(self._ttl_seconds):
            del self._cache[key]
            self._misses += 1
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        self._hits += 1
        return entry.value

    def put(self, key: K, value: V) -> None:
        """Put a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Update existing entry
        if key in self._cache:
            self._cache[key] = CacheEntry(value)
            self._cache.move_to_end(key)
            return

        # Evict if at capacity
        while len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)

        # Add new entry
        self._cache[key] = CacheEntry(value)

    def delete(self, key: K) -> bool:
        """Delete a key from the cache.

        Args:
            key: Cache key

        Returns:
            True if key was present and deleted
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def contains(self, key: K) -> bool:
        """Check if key is in cache (doesn't update LRU order).

        Args:
            key: Cache key

        Returns:
            True if key is present and not expired
        """
        entry = self._cache.get(key)
        if entry is None:
            return False
        if entry.is_expired(self._ttl_seconds):
            del self._cache[key]
            return False
        return True

    def clear(self) -> None:
        """Clear all entries from the cache."""
        self._cache.clear()

    def reset_stats(self) -> None:
        """Reset hit/miss statistics."""
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict[str, int | float]:
        """Get cache statistics."""
        return {
            "size": self.size,
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
        }

    def evict_expired(self) -> int:
        """Evict all expired entries.

        Returns:
            Number of entries evicted
        """
        if self._ttl_seconds is None:
            return 0

        expired_keys = [
            key
            for key, entry in self._cache.items()
            if entry.is_expired(self._ttl_seconds)
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)
