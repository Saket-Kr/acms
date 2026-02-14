"""In-memory storage backend for testing and development."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from acms.models import Episode, EpisodeStatus, Fact, Turn, VectorSearchResult
from acms.storage.base import StorageBackend


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(a) != len(b):
        raise ValueError(f"Vector dimensions must match: {len(a)} != {len(b)}")

    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class InMemoryBackend(StorageBackend):
    """In-memory storage backend.

    Stores all data in dictionaries. Useful for testing and development.
    Data is lost when the process exits.
    """

    def __init__(self) -> None:
        self._turns: dict[str, Turn] = {}
        self._episodes: dict[str, Episode] = {}
        self._facts: dict[str, Fact] = {}
        self._embeddings: dict[str, tuple[list[float], dict[str, Any]]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the backend (no-op for in-memory)."""
        self._initialized = True

    async def close(self) -> None:
        """Close the backend (no-op for in-memory)."""
        pass

    # Turn operations

    async def save_turn(self, turn: Turn) -> None:
        """Save a turn to memory."""
        self._turns[turn.id] = turn

    async def get_turn(self, turn_id: str) -> Turn | None:
        """Get a turn by ID."""
        return self._turns.get(turn_id)

    async def get_turns_by_episode(self, episode_id: str) -> list[Turn]:
        """Get all turns for an episode, ordered by position."""
        turns = [t for t in self._turns.values() if t.episode_id == episode_id]
        return sorted(turns, key=lambda t: t.position)

    async def get_turns_by_session(
        self,
        session_id: str,
        *,
        limit: int = 1000,
    ) -> list[Turn]:
        """Get all turns for a session."""
        turns = [t for t in self._turns.values() if t.session_id == session_id]
        turns.sort(key=lambda t: t.created_at)
        return turns[:limit]

    async def get_marked_turns(
        self,
        session_id: str,
        *,
        exclude_episode_id: str | None = None,
    ) -> list[Turn]:
        """Get all turns with markers."""
        turns = [
            t
            for t in self._turns.values()
            if t.session_id == session_id
            and t.markers
            and (exclude_episode_id is None or t.episode_id != exclude_episode_id)
        ]
        return sorted(turns, key=lambda t: t.created_at)

    # Episode operations

    async def save_episode(self, episode: Episode) -> None:
        """Save an episode to memory."""
        self._episodes[episode.id] = episode

    async def get_episode(self, episode_id: str) -> Episode | None:
        """Get an episode by ID."""
        return self._episodes.get(episode_id)

    async def get_episodes(
        self,
        session_id: str,
        *,
        limit: int = 100,
        status: EpisodeStatus | None = None,
    ) -> list[Episode]:
        """Get episodes for a session."""
        episodes = [e for e in self._episodes.values() if e.session_id == session_id]

        if status is not None:
            episodes = [e for e in episodes if e.status == status]

        episodes.sort(key=lambda e: e.created_at)
        return episodes[:limit]

    async def update_episode(self, episode: Episode) -> None:
        """Update an existing episode."""
        self._episodes[episode.id] = episode

    # Vector operations

    async def save_embedding(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Save an embedding vector."""
        self._embeddings[id] = (embedding, metadata)

    async def get_embedding(self, id: str) -> list[float] | None:
        """Get an embedding by ID."""
        result = self._embeddings.get(id)
        return result[0] if result else None

    async def vector_search(
        self,
        embedding: list[float],
        *,
        k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search for similar vectors using cosine similarity."""
        results: list[tuple[str, float, dict[str, Any]]] = []

        for emb_id, (emb_vector, metadata) in self._embeddings.items():
            # Apply filter
            if filter:
                match = all(metadata.get(key) == value for key, value in filter.items())
                if not match:
                    continue

            # Calculate similarity
            similarity = cosine_similarity(embedding, emb_vector)
            results.append((emb_id, similarity, metadata))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        # Return top k
        return [
            VectorSearchResult(id=r[0], score=r[1], metadata=r[2])
            for r in results[:k]
        ]

    # Fact operations

    async def save_fact(self, fact: Fact) -> None:
        """Save a fact to memory."""
        self._facts[fact.id] = fact

    async def get_facts_by_session(self, session_id: str) -> list[Fact]:
        """Get all facts for a session."""
        facts = [f for f in self._facts.values() if f.session_id == session_id]
        return sorted(facts, key=lambda f: f.created_at)

    async def get_facts_by_episode(self, episode_id: str) -> list[Fact]:
        """Get facts derived from a specific episode."""
        facts = [f for f in self._facts.values() if f.episode_id == episode_id]
        return sorted(facts, key=lambda f: f.created_at)

    async def get_active_facts_by_session(self, session_id: str) -> list[Fact]:
        """Get non-superseded facts for a session."""
        facts = [
            f
            for f in self._facts.values()
            if f.session_id == session_id and f.superseded_by is None
        ]
        return sorted(facts, key=lambda f: f.created_at)

    async def update_fact(self, fact: Fact) -> None:
        """Update an existing fact in storage."""
        self._facts[fact.id] = fact

    # Statistics

    async def get_session_stats(
        self,
        session_id: str,
    ) -> dict[str, Any]:
        """Get statistics for a session."""
        turns = [t for t in self._turns.values() if t.session_id == session_id]
        episodes = [e for e in self._episodes.values() if e.session_id == session_id]
        facts = [f for f in self._facts.values() if f.session_id == session_id]

        open_episodes = [e for e in episodes if e.status == EpisodeStatus.OPEN]
        open_episode = open_episodes[0] if open_episodes else None

        total_tokens = sum(t.token_count for t in turns)

        created_at = min((t.created_at for t in turns), default=datetime.utcnow())
        last_activity = max((t.created_at for t in turns), default=created_at)

        return {
            "session_id": session_id,
            "total_turns": len(turns),
            "total_episodes": len(episodes),
            "total_facts": len(facts),
            "open_episode_id": open_episode.id if open_episode else None,
            "open_episode_turn_count": (
                len([t for t in turns if t.episode_id == open_episode.id])
                if open_episode
                else 0
            ),
            "total_tokens_ingested": total_tokens,
            "created_at": created_at,
            "last_activity_at": last_activity,
        }

    # Additional utility methods

    def clear(self) -> None:
        """Clear all stored data (for testing)."""
        self._turns.clear()
        self._episodes.clear()
        self._facts.clear()
        self._embeddings.clear()
