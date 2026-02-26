"""Episode lifecycle management."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Awaitable, Callable

from gleanr.models import Episode, EpisodeStatus, Role, Turn
from gleanr.utils import generate_episode_id

if TYPE_CHECKING:
    from gleanr.core.config import GleanrConfig
    from gleanr.storage import StorageBackend

# Type alias for episode close callback
OnEpisodeClosedCallback = Callable[[str], Awaitable[None]]


class EpisodeManager:
    """Manages episode lifecycle and boundary detection.

    Handles:
    - Creating new episodes
    - Detecting episode boundaries
    - Closing episodes
    """

    def __init__(
        self,
        session_id: str,
        storage: "StorageBackend",
        config: "GleanrConfig",
    ) -> None:
        self._session_id = session_id
        self._storage = storage
        self._config = config
        self._current_episode: Episode | None = None
        self._last_turn_time: datetime | None = None
        self._on_episode_closed: OnEpisodeClosedCallback | None = None

    def set_on_episode_closed(self, callback: OnEpisodeClosedCallback | None) -> None:
        """Set callback to be invoked when any episode closes.

        The callback receives the closed episode ID and is called for both
        manual closes and automatic closes (boundary rules).

        Args:
            callback: Async function that takes episode_id as argument
        """
        self._on_episode_closed = callback

    @property
    def current_episode(self) -> Episode | None:
        """Get the current open episode."""
        return self._current_episode

    @property
    def current_episode_id(self) -> str | None:
        """Get the current episode ID."""
        return self._current_episode.id if self._current_episode else None

    async def initialize(self) -> None:
        """Initialize by loading or creating current episode."""
        # Check for existing open episode
        episodes = await self._storage.get_episodes(
            self._session_id,
            status=EpisodeStatus.OPEN,
            limit=1,
        )

        if episodes:
            self._current_episode = episodes[0]
            # Load last turn time
            turns = await self._storage.get_turns_by_episode(self._current_episode.id)
            if turns:
                self._last_turn_time = turns[-1].created_at
        else:
            # Create first episode
            await self._create_new_episode()

    async def _create_new_episode(self) -> Episode:
        """Create a new episode."""
        episode = Episode(
            id=generate_episode_id(),
            session_id=self._session_id,
            status=EpisodeStatus.OPEN,
            created_at=datetime.utcnow(),
        )
        await self._storage.save_episode(episode)
        self._current_episode = episode
        return episode

    async def should_close_episode(self, turn: Turn) -> bool:
        """Check if episode should be closed based on boundary rules.

        Args:
            turn: The turn being ingested

        Returns:
            True if episode should be closed before this turn
        """
        if self._current_episode is None:
            return False

        boundary_config = self._config.episode_boundary

        # Rule 1: Max turns reached
        if self._current_episode.turn_count >= boundary_config.max_turns:
            return True

        # Rule 2: Time gap exceeded
        if self._last_turn_time:
            gap = turn.created_at - self._last_turn_time
            max_gap = timedelta(seconds=boundary_config.max_time_gap_seconds)
            if gap > max_gap:
                return True

        # Rule 3: Tool result (complete a unit of work)
        if boundary_config.close_on_tool_result and turn.role == Role.TOOL:
            return True

        # Rule 4: Content patterns
        if boundary_config.should_close_on_content(turn.content):
            return True

        return False

    async def assign_episode(self, turn: Turn) -> str:
        """Assign a turn to an episode.

        Creates new episode if needed based on boundary rules.

        Args:
            turn: Turn to assign

        Returns:
            Episode ID the turn was assigned to
        """
        # Check if we need to close current episode
        if await self.should_close_episode(turn):
            await self.close_current_episode(reason="boundary_rule")

        # Ensure we have an open episode
        if self._current_episode is None:
            await self._create_new_episode()

        assert self._current_episode is not None

        # Update episode stats
        self._current_episode.turn_count += 1
        self._current_episode.total_tokens += turn.token_count

        # Aggregate markers
        for marker in turn.markers:
            if marker not in self._current_episode.markers:
                self._current_episode.markers.append(marker)

        await self._storage.update_episode(self._current_episode)
        self._last_turn_time = turn.created_at

        return self._current_episode.id

    async def close_current_episode(
        self,
        reason: str = "manual",
    ) -> str | None:
        """Close the current episode.

        Invokes the on_episode_closed callback if set.

        Args:
            reason: Reason for closing

        Returns:
            Closed episode ID, or None if no open episode
        """
        if self._current_episode is None:
            return None

        episode_id = self._current_episode.id

        self._current_episode.status = EpisodeStatus.CLOSED
        self._current_episode.closed_at = datetime.utcnow()
        self._current_episode.close_reason = reason

        await self._storage.update_episode(self._current_episode)
        self._current_episode = None
        self._last_turn_time = None

        # Invoke callback for reflection or other processing
        if self._on_episode_closed is not None:
            await self._on_episode_closed(episode_id)

        return episode_id

    async def get_current_episode_turns(self) -> list[Turn]:
        """Get all turns in the current episode.

        Returns:
            List of turns in chronological order
        """
        if self._current_episode is None:
            return []

        return await self._storage.get_turns_by_episode(self._current_episode.id)
