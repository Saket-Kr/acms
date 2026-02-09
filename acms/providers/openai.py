"""OpenAI SDK-based providers."""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any

from acms.errors import ProviderError
from acms.models import Fact, MarkerType
from acms.utils import generate_fact_id

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

    REFLECTION_PROMPT = """Analyze this conversation episode and extract key facts.

Focus on:
- DECISIONS: Choices made (what was decided and why)
- CONSTRAINTS: Limitations discovered (what cannot/should not be done)
- FAILURES: What didn't work (to avoid repeating)
- GOALS: Objectives established (what the user wants to achieve)

Episode turns:
{turns}

Extract up to {max_facts} facts. For each fact:
1. State it concisely (one sentence)
2. Classify its type (decision/constraint/failure/goal)
3. Rate your confidence (0-1)

Respond in JSON format:
{{"facts": [
  {{"content": "...", "type": "decision|constraint|failure|goal", "confidence": 0.9}},
  ...
]}}"""

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

            prompt = self.REFLECTION_PROMPT.format(
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
        try:
            data = json.loads(content)
            facts_data = data.get("facts", [])
        except json.JSONDecodeError:
            return []

        facts = []
        for item in facts_data:
            fact_type = item.get("type", "decision")
            # Normalize fact type to MarkerType values
            if fact_type not in [m.value for m in MarkerType]:
                fact_type = MarkerType.DECISION.value

            facts.append(
                Fact(
                    id=generate_fact_id(),
                    session_id=episode.session_id,
                    episode_id=episode.id,
                    content=item.get("content", ""),
                    created_at=datetime.utcnow(),
                    fact_type=fact_type,
                    confidence=float(item.get("confidence", 0.8)),
                )
            )

        return facts
