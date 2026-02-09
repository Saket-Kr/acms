"""Anthropic SDK-based providers."""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING

from acms.errors import ProviderError
from acms.models import Fact, MarkerType
from acms.utils import generate_fact_id

if TYPE_CHECKING:
    from anthropic import AsyncAnthropic

    from acms.models import Episode, Turn


class AnthropicReflector:
    """Reflector using Anthropic Python SDK for fact extraction.

    Uses Claude to extract semantic facts from episodes.
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

Respond ONLY with valid JSON in this exact format, no other text:
{{"facts": [
  {{"content": "...", "type": "decision", "confidence": 0.9}},
  ...
]}}"""

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

            prompt = self.REFLECTION_PROMPT.format(
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
        # Try to extract JSON from the response
        # Claude might include extra text before/after JSON
        try:
            # Find JSON in response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
                facts_data = data.get("facts", [])
            else:
                return []
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
