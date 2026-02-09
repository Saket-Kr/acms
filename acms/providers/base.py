"""Provider protocols for ACMS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from acms.models import Episode, Fact, Turn


@runtime_checkable
class Embedder(Protocol):
    """Protocol for embedding providers.

    Embedders convert text into dense vector representations
    for semantic similarity search.
    """

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (one per input text)

        Raises:
            ProviderError: If embedding fails
        """
        ...

    @property
    def dimension(self) -> int:
        """Embedding dimension (e.g., 1536 for text-embedding-3-small)."""
        ...


@runtime_checkable
class Reflector(Protocol):
    """Protocol for reflection providers (LLM-assisted fact extraction).

    Reflectors analyze episodes to extract semantic facts
    for L2 memory.
    """

    async def reflect(self, episode: "Episode", turns: list["Turn"]) -> list["Fact"]:
        """Extract semantic facts from an episode.

        Args:
            episode: The episode to reflect on
            turns: Turns belonging to the episode

        Returns:
            List of extracted facts

        Raises:
            ProviderError: If reflection fails
        """
        ...


@runtime_checkable
class TokenCounter(Protocol):
    """Protocol for token counting.

    TokenCounters estimate the number of tokens in text
    for budget management.
    """

    def count(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens in

        Returns:
            Estimated token count
        """
        ...


class NullEmbedder:
    """No-op embedder for testing without real embeddings.

    Returns zero vectors of configurable dimension.
    """

    def __init__(self, dimension: int = 1536) -> None:
        self._dimension = dimension

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return zero vectors for all texts."""
        return [[0.0] * self._dimension for _ in texts]

    @property
    def dimension(self) -> int:
        return self._dimension


class NullReflector:
    """No-op reflector that returns no facts.

    Use when reflection is disabled.
    """

    async def reflect(self, episode: "Episode", turns: list["Turn"]) -> list["Fact"]:
        """Return empty list (no reflection)."""
        return []
