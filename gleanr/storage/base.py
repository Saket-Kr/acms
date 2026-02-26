"""Storage backend abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from gleanr.models import Episode, EpisodeStatus, Fact, Turn, VectorSearchResult


class StorageBackend(ABC):
    """Abstract base for all storage backends.

    Storage backends handle persistence of turns, episodes, facts,
    and embeddings. They provide both relational queries and
    vector similarity search.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize storage (create tables, indexes, etc.).

        Called once when the backend is first used.
        Should be idempotent.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources (close connections, flush buffers, etc.)."""
        ...

    # Turn operations

    @abstractmethod
    async def save_turn(self, turn: "Turn") -> None:
        """Save a turn to storage.

        Args:
            turn: Turn to save

        Raises:
            StorageError: If save fails
        """
        ...

    @abstractmethod
    async def get_turn(self, turn_id: str) -> "Turn | None":
        """Get a turn by ID.

        Args:
            turn_id: Turn identifier

        Returns:
            Turn if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_turns_by_episode(self, episode_id: str) -> list["Turn"]:
        """Get all turns for an episode, ordered by position.

        Args:
            episode_id: Episode identifier

        Returns:
            List of turns in chronological order
        """
        ...

    @abstractmethod
    async def get_turns_by_session(
        self,
        session_id: str,
        *,
        limit: int = 1000,
    ) -> list["Turn"]:
        """Get all turns for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of turns to return

        Returns:
            List of turns in chronological order
        """
        ...

    @abstractmethod
    async def get_marked_turns(
        self,
        session_id: str,
        *,
        exclude_episode_id: str | None = None,
    ) -> list["Turn"]:
        """Get all turns with markers (decision, constraint, failure, goal).

        Args:
            session_id: Session identifier
            exclude_episode_id: Episode to exclude (typically current episode)

        Returns:
            List of marked turns
        """
        ...

    # Episode operations

    @abstractmethod
    async def save_episode(self, episode: "Episode") -> None:
        """Save an episode to storage.

        Args:
            episode: Episode to save

        Raises:
            StorageError: If save fails
        """
        ...

    @abstractmethod
    async def get_episode(self, episode_id: str) -> "Episode | None":
        """Get an episode by ID.

        Args:
            episode_id: Episode identifier

        Returns:
            Episode if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_episodes(
        self,
        session_id: str,
        *,
        limit: int = 100,
        status: "EpisodeStatus | None" = None,
    ) -> list["Episode"]:
        """Get episodes for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of episodes
            status: Filter by status (None = all)

        Returns:
            List of episodes in chronological order
        """
        ...

    @abstractmethod
    async def update_episode(self, episode: "Episode") -> None:
        """Update an existing episode.

        Args:
            episode: Episode with updated fields

        Raises:
            StorageError: If update fails
        """
        ...

    # Vector operations

    @abstractmethod
    async def save_embedding(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Save an embedding vector.

        Args:
            id: Unique identifier for the embedding
            embedding: Vector values
            metadata: Associated metadata (session_id, type, etc.)

        Raises:
            StorageError: If save fails
        """
        ...

    @abstractmethod
    async def get_embedding(self, id: str) -> list[float] | None:
        """Get an embedding by ID.

        Args:
            id: Embedding identifier

        Returns:
            Embedding vector if found, None otherwise
        """
        ...

    @abstractmethod
    async def vector_search(
        self,
        embedding: list[float],
        *,
        k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list["VectorSearchResult"]:
        """Search for similar vectors.

        Args:
            embedding: Query vector
            k: Number of results to return
            filter: Optional metadata filter (e.g., {"session_id": "x"})

        Returns:
            List of search results ordered by similarity (highest first)
        """
        ...

    # Fact operations (L2)

    @abstractmethod
    async def save_fact(self, fact: "Fact") -> None:
        """Save a fact to storage.

        Args:
            fact: Fact to save

        Raises:
            StorageError: If save fails
        """
        ...

    @abstractmethod
    async def get_facts_by_session(self, session_id: str) -> list["Fact"]:
        """Get all facts for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of facts in chronological order
        """
        ...

    @abstractmethod
    async def get_facts_by_episode(self, episode_id: str) -> list["Fact"]:
        """Get facts derived from a specific episode.

        Args:
            episode_id: Episode identifier

        Returns:
            List of facts
        """
        ...

    @abstractmethod
    async def get_active_facts_by_session(self, session_id: str) -> list["Fact"]:
        """Get non-superseded facts for a session.

        Returns only facts where superseded_by is None, i.e. facts that
        have not been replaced or removed by a later consolidation.

        Args:
            session_id: Session identifier

        Returns:
            List of active facts in chronological order
        """
        ...

    @abstractmethod
    async def update_fact(self, fact: "Fact") -> None:
        """Update an existing fact in storage.

        Used during consolidation to set superseded_by on old facts.

        Args:
            fact: Fact with updated fields

        Raises:
            StorageError: If update fails
        """
        ...

    # Statistics

    @abstractmethod
    async def get_session_stats(
        self,
        session_id: str,
    ) -> dict[str, Any]:
        """Get statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with counts and metadata
        """
        ...
