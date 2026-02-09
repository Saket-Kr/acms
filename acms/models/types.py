"""Core type definitions for ACMS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Role(str, Enum):
    """Who produced a turn."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class EpisodeStatus(str, Enum):
    """Lifecycle status of an episode."""

    OPEN = "open"
    CLOSED = "closed"


class MarkerType(str, Enum):
    """Built-in marker types with semantic meaning.

    Markers provide lightweight importance signals for recall scoring.
    """

    DECISION = "decision"  # Choices made - maintain consistency
    CONSTRAINT = "constraint"  # Limitations/requirements - always relevant
    FAILURE = "failure"  # What didn't work - prevent repeated attempts
    GOAL = "goal"  # Task objectives - anchor for relevance


# Default boost weights for markers in scoring
DEFAULT_MARKER_WEIGHTS: dict[str, float] = {
    MarkerType.CONSTRAINT.value: 0.4,  # Constraints are critical
    MarkerType.DECISION.value: 0.3,  # Decisions drive consistency
    MarkerType.GOAL.value: 0.3,  # Goals anchor relevance
    MarkerType.FAILURE.value: 0.2,  # Failures prevent waste
}

# Default boost for custom markers (custom:*)
DEFAULT_CUSTOM_MARKER_WEIGHT: float = 0.2


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    """Result from a vector similarity search."""

    id: str
    score: float  # Cosine similarity score (0-1)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ContextItem:
    """A single item returned by recall.

    Represents a piece of context that can be included in the agent's prompt.
    """

    id: str
    content: str
    role: Role
    source: str  # "turn", "episode", "fact"
    score: float  # Final score after all adjustments
    token_count: int
    metadata: dict[str, Any] = field(default_factory=dict)
    markers: tuple[str, ...] = field(default_factory=tuple)
    timestamp: datetime | None = None


@dataclass(frozen=True, slots=True)
class SessionStats:
    """Statistics about a session."""

    session_id: str
    total_turns: int
    total_episodes: int
    total_facts: int
    open_episode_id: str | None
    open_episode_turn_count: int
    total_tokens_ingested: int
    created_at: datetime
    last_activity_at: datetime


@dataclass(frozen=True, slots=True)
class ScoredCandidate:
    """Internal type for recall scoring pipeline."""

    id: str
    content: str
    role: Role
    source: str
    relevance_score: float  # Raw cosine similarity
    marker_boost: float  # Boost from markers
    final_score: float  # relevance + marker_boost
    token_count: int
    metadata: dict[str, Any] = field(default_factory=dict)
    markers: tuple[str, ...] = field(default_factory=tuple)
    timestamp: datetime | None = None
    episode_id: str | None = None
