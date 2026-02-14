"""OpenAI SDK-based providers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from acms.errors import ProviderError
from acms.models import Fact
from acms.models.consolidation import ConsolidationAction
from acms.providers.parsing import (
    CONSOLIDATION_PROMPT,
    REFLECTION_PROMPT,
    format_prior_facts,
    format_turns,
    parse_consolidation_actions,
    parse_reflection_facts,
)

if TYPE_CHECKING:
    from openai import AsyncOpenAI

    from acms.models import Episode, Turn

# Model dimensions for common OpenAI embedding models
MODEL_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


class OpenAIEmbedder:
    """Embedder using OpenAI Python SDK.

    Uses the user-provided AsyncOpenAI client, allowing full
    configuration control (API key, base URL, organization, etc.).
    """

    def __init__(
        self,
        client: "AsyncOpenAI",
        model: str = "text-embedding-3-small",
        *,
        dimension: int | None = None,
    ) -> None:
        """Initialize OpenAI embedder.

        Args:
            client: Configured AsyncOpenAI client
            model: Embedding model name
            dimension: Override dimension (auto-detected if None)
        """
        self._client = client
        self._model = model
        self._dimension = dimension or MODEL_DIMENSIONS.get(model, 1536)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            ProviderError: If embedding fails
        """
        if not texts:
            return []

        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=texts,
            )

            embeddings = [item.embedding for item in response.data]

            if len(embeddings) != len(texts):
                raise ProviderError(
                    f"Expected {len(texts)} embeddings, got {len(embeddings)}",
                    provider="OpenAIEmbedder",
                    retryable=False,
                )

            return embeddings

        except Exception as e:
            if "ProviderError" in type(e).__name__:
                raise
            raise ProviderError(
                f"OpenAI embedding failed: {e}",
                provider="OpenAIEmbedder",
                retryable=True,
                cause=e,
            ) from e

    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return self._dimension


class OpenAIReflector:
    """Reflector using OpenAI Python SDK for fact extraction.

    Uses the chat completions API with structured output
    to extract semantic facts from episodes.
    """

    def __init__(
        self,
        client: "AsyncOpenAI",
        model: str = "gpt-4o-mini",
        *,
        max_facts: int = 5,
    ) -> None:
        """Initialize OpenAI reflector.

        Args:
            client: Configured AsyncOpenAI client
            model: Chat model name
            max_facts: Maximum facts to extract per episode
        """
        self._client = client
        self._model = model
        self._max_facts = max_facts

    async def reflect(self, episode: "Episode", turns: list["Turn"]) -> list[Fact]:
        """Extract semantic facts from an episode.

        Args:
            episode: The episode to reflect on
            turns: Turns belonging to the episode

        Returns:
            List of extracted facts

        Raises:
            ProviderError: If reflection fails
        """
        if not turns:
            return []

        try:
            # Format turns for the prompt
            turns_text = "\n".join(
                f"[{t.role.value}]: {t.content}" for t in turns
            )

            prompt = REFLECTION_PROMPT.format(
                turns=turns_text,
                max_facts=self._max_facts,
            )

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            return self._parse_facts(content, episode)

        except Exception as e:
            if "ProviderError" in type(e).__name__:
                raise
            raise ProviderError(
                f"OpenAI reflection failed: {e}",
                provider="OpenAIReflector",
                retryable=True,
                cause=e,
            ) from e

    def _parse_facts(self, content: str, episode: "Episode") -> list[Fact]:
        """Parse facts from LLM response."""
        return parse_reflection_facts(content, episode)

    async def reflect_with_consolidation(
        self,
        episode: "Episode",
        turns: list["Turn"],
        prior_facts: list[Fact],
    ) -> list[ConsolidationAction]:
        """Consolidate prior facts with new episode content."""
        if not turns:
            return []

        try:
            prompt = CONSOLIDATION_PROMPT.format(
                prior_facts=format_prior_facts(prior_facts),
                turns=format_turns(turns),
            )

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            return parse_consolidation_actions(content)

        except Exception as e:
            if "ProviderError" in type(e).__name__:
                raise
            raise ProviderError(
                f"OpenAI consolidation failed: {e}",
                provider="OpenAIReflector",
                retryable=True,
                cause=e,
            ) from e
