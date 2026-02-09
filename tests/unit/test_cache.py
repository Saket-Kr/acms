"""Unit tests for LRU cache."""

import time

import pytest

from acms.cache import CacheConfig, LRUCache


class TestLRUCache:
    """Tests for LRUCache."""

    def test_put_and_get(self) -> None:
        """Test basic put and get operations."""
        cache: LRUCache[str, int] = LRUCache(max_size=10)

        cache.put("a", 1)
        cache.put("b", 2)

        assert cache.get("a") == 1
        assert cache.get("b") == 2

    def test_get_nonexistent(self) -> None:
        """Test getting a non-existent key."""
        cache: LRUCache[str, int] = LRUCache(max_size=10)

        assert cache.get("nonexistent") is None

    def test_eviction(self) -> None:
        """Test LRU eviction when cache is full."""
        cache: LRUCache[str, int] = LRUCache(max_size=3)

        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.put("d", 4)  # Should evict "a"

        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_lru_order_on_get(self) -> None:
        """Test that get updates LRU order."""
        cache: LRUCache[str, int] = LRUCache(max_size=3)

        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)

        # Access "a" to make it most recently used
        _ = cache.get("a")

        # Add "d" - should evict "b" (least recently used)
        cache.put("d", 4)

        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_update_existing_key(self) -> None:
        """Test updating an existing key."""
        cache: LRUCache[str, int] = LRUCache(max_size=10)

        cache.put("a", 1)
        cache.put("a", 2)

        assert cache.get("a") == 2
        assert cache.size == 1

    def test_delete(self) -> None:
        """Test deleting a key."""
        cache: LRUCache[str, int] = LRUCache(max_size=10)

        cache.put("a", 1)
        assert cache.delete("a") is True
        assert cache.get("a") is None
        assert cache.delete("a") is False

    def test_contains(self) -> None:
        """Test checking if key exists."""
        cache: LRUCache[str, int] = LRUCache(max_size=10)

        cache.put("a", 1)
        assert cache.contains("a") is True
        assert cache.contains("b") is False

    def test_clear(self) -> None:
        """Test clearing the cache."""
        cache: LRUCache[str, int] = LRUCache(max_size=10)

        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()

        assert cache.size == 0
        assert cache.get("a") is None

    def test_stats(self) -> None:
        """Test cache statistics."""
        cache: LRUCache[str, int] = LRUCache(max_size=10)

        cache.put("a", 1)
        cache.get("a")  # Hit
        cache.get("a")  # Hit
        cache.get("b")  # Miss

        assert cache.hits == 2
        assert cache.misses == 1
        assert cache.hit_rate == 2 / 3

    def test_reset_stats(self) -> None:
        """Test resetting statistics."""
        cache: LRUCache[str, int] = LRUCache(max_size=10)

        cache.put("a", 1)
        cache.get("a")
        cache.reset_stats()

        assert cache.hits == 0
        assert cache.misses == 0

    def test_get_stats(self) -> None:
        """Test getting statistics as dict."""
        cache: LRUCache[str, int] = LRUCache(max_size=10)

        cache.put("a", 1)
        stats = cache.get_stats()

        assert "size" in stats
        assert "max_size" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats

    def test_ttl_expiry(self) -> None:
        """Test TTL-based expiry."""
        cache: LRUCache[str, int] = LRUCache(max_size=10, ttl_seconds=1)

        cache.put("a", 1)
        assert cache.get("a") == 1

        # Wait for TTL to expire
        time.sleep(1.1)

        assert cache.get("a") is None

    def test_evict_expired(self) -> None:
        """Test explicit eviction of expired entries."""
        cache: LRUCache[str, int] = LRUCache(max_size=10, ttl_seconds=1)

        cache.put("a", 1)
        cache.put("b", 2)

        time.sleep(1.1)

        evicted = cache.evict_expired()
        assert evicted == 2
        assert cache.size == 0


class TestCacheConfig:
    """Tests for CacheConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = CacheConfig()

        assert config.enabled is True
        assert config.max_turns == 1000
        assert config.max_episodes == 100
        assert config.max_embeddings == 1000
        assert config.ttl_seconds is None

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = CacheConfig(
            enabled=False,
            max_turns=500,
            ttl_seconds=300,
        )

        assert config.enabled is False
        assert config.max_turns == 500
        assert config.ttl_seconds == 300
