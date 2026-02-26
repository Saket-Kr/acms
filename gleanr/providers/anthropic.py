"""Anthropic SDK-based providers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gleanr.errors import ProviderError
from gleanr.models import Fact
from gleanr.models.consolidation import ConsolidationAction
from gleanr.providers.parsing import (
    CONSOLIDATION_PROMPT,
    REFLECTION_PROMPT,
    format_prior_facts,
    format_turns,
    parse_consolidation_actions,
    parse_reflection_facts,
)

if TYPE_CHECKING:
    from anthropic import AsyncAnthropic

    from gleanr.models import Episode, Turn


class AnthropicReflector:
    """Reflector using Anthropic Python SDK for fact extraction.

    Uses Claude to extract semantic facts from episodes.
    """

    def __init__(
        self,
        client: "AsyncAnthropic",
        model: str = "claude-3-haiku-20240307",
        *,
        max_facts: int = 5,
        max_tokens: int = 1024,
    ) -> None:
        """Initialize Anthropic reflector.

        Args:
            client: Configured AsyncAnthropic client
            model: Claude model name
            max_facts: Maximum facts to extract per episode
            max_tokens: Maximum tokens in response
        """
        self._client = client
        self._model = model
        self._max_facts = max_facts
        self._max_tokens = max_tokens

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

            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text from response
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            return self._parse_facts(content, episode)

        except Exception as e:
            if "ProviderError" in type(e).__name__:
                raise
            raise ProviderError(
                f"Anthropic reflection failed: {e}",
                provider="AnthropicReflector",
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

            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            return parse_consolidation_actions(content)

        except Exception as e:
            if "ProviderError" in type(e).__name__:
                raise
            raise ProviderError(
                f"Anthropic consolidation failed: {e}",
                provider="AnthropicReflector",
                retryable=True,
                cause=e,
            ) from e

        return facts
