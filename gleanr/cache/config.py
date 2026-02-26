"""Cache configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CacheConfig:
    """Configuration for the in-memory LRU cache.

    The cache sits between Gleanr and the storage backend,
    providing fast access to hot data.
    """

    enabled: bool = True
    """Whether caching is enabled."""

    max_turns: int = 1000
    """Maximum number of turns to cache."""

    max_episodes: int = 100
    """Maximum number of episodes to cache."""

    max_embeddings: int = 1000
    """Maximum number of embeddings to cache."""

    max_facts: int = 500
    """Maximum number of facts to cache."""

    ttl_seconds: int | None = None
    """Optional TTL for cache entries. None = no expiry."""
