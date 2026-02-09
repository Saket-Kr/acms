"""Reflection runner for L2 fact extraction."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from acms.errors import ReflectionError
from acms.utils import generate_embedding_id

if TYPE_CHECKING:
    from acms.core.config import ACMSConfig
    from acms.models import Episode, Fact, Turn
    from acms.providers import Embedder, Reflector
    from acms.storage import StorageBackend
    from acms.utils import TokenCounter

logger = logging.getLogger(__name__)


class ReflectionRunner:
    """Runs reflection on closed episodes to extract L2 facts.

    Reflection is:
    - Asynchronous (can run in background)
    - Optional (system works without it)
    - LLM-assisted (uses a Reflector provider)

    The runner:
    1. Takes a closed episode and its turns
    2. Calls the reflector to extract facts
    3. Generates embeddings for facts
    4. Saves facts to storage
    """

    def __init__(
        self,
        session_id: str,
        storage: "StorageBackend",
        reflector: "Reflector",
        embedder: "Embedder",
        token_counter: "TokenCounter",
        config: "ACMSConfig",
    ) -> None:
        self._session_id = session_id
        self._storage = storage
        self._reflector = reflector
        self._embedder = embedder
        self._token_counter = token_counter
        self._config = config
        self._pending_tasks: list[asyncio.Task[list["Fact"]]] = []

    async def reflect_episode(
        self,
        episode: "Episode",
        turns: list["Turn"],
        *,
        background: bool = False,
    ) -> list["Fact"]:
        """Run reflection on an episode.

        Args:
            episode: The closed episode
            turns: Turns in the episode
            background: If True, run in background and return immediately

        Returns:
            List of extracted facts (empty if background=True)

        Raises:
            ReflectionError: If reflection fails (only if background=False)
        """
        if not self._config.reflection.enabled:
            return []

        if len(turns) < self._config.reflection.min_episode_turns:
            logger.debug(
                f"Skipping reflection for episode {episode.id}: "
                f"only {len(turns)} turns (min: {self._config.reflection.min_episode_turns})"
            )
            return []

        if background:
            task = asyncio.create_task(
                self._reflect_and_save(episode, turns)
            )
            self._pending_tasks.append(task)
            # Clean up completed tasks
            self._pending_tasks = [t for t in self._pending_tasks if not t.done()]
            return []

        return await self._reflect_and_save(episode, turns)

    async def _reflect_and_save(
        self,
        episode: "Episode",
        turns: list["Turn"],
    ) -> list["Fact"]:
        """Reflect on episode and save facts."""
        try:
            # Call reflector
            facts = await self._reflector.reflect(episode, turns)

            # Process and save facts
            saved_facts: list["Fact"] = []
            for fact in facts[: self._config.reflection.max_facts_per_episode]:
                # Check confidence threshold
                if fact.confidence < self._config.reflection.min_confidence:
                    continue

                # Count tokens
                fact.token_count = self._token_counter.count(fact.content)

                # Generate embedding
                try:
                    embeddings = await self._embedder.embed([fact.content])
                    if embeddings:
                        emb_id = generate_embedding_id()
                        await self._storage.save_embedding(
                            id=emb_id,
                            embedding=embeddings[0],
                            metadata={
                                "session_id": self._session_id,
                                "episode_id": episode.id,
                                "fact_id": fact.id,
                                "type": "fact",
                                "fact_type": fact.fact_type,
                            },
                        )
                        fact.embedding_id = emb_id
                except Exception as e:
                    logger.warning(f"Failed to embed fact {fact.id}: {e}")

                # Save fact
                await self._storage.save_fact(fact)
                saved_facts.append(fact)

            logger.info(
                f"Reflection extracted {len(saved_facts)} facts "
                f"from episode {episode.id}"
            )
            return saved_facts

        except Exception as e:
            logger.error(f"Reflection failed for episode {episode.id}: {e}")
            raise ReflectionError(
                f"Reflection failed: {e}",
                episode_id=episode.id,
                cause=e,
            ) from e

    async def wait_pending(self) -> None:
        """Wait for all pending background reflection tasks."""
        if self._pending_tasks:
            await asyncio.gather(*self._pending_tasks, return_exceptions=True)
            self._pending_tasks = []

    def cancel_pending(self) -> None:
        """Cancel all pending background reflection tasks."""
        for task in self._pending_tasks:
            if not task.done():
                task.cancel()
        self._pending_tasks = []
