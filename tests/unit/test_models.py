"""Unit tests for ACMS models."""

from datetime import datetime

import pytest

from acms.models import (
    ContextItem,
    Episode,
    EpisodeStatus,
    Fact,
    MarkerType,
    Role,
    SessionStats,
    Turn,
    VectorSearchResult,
)


class TestRole:
    """Tests for Role enum."""

    def test_role_values(self) -> None:
        """Test role enum values."""
        assert Role.USER.value == "user"
        assert Role.ASSISTANT.value == "assistant"
        assert Role.TOOL.value == "tool"

    def test_role_from_string(self) -> None:
        """Test creating role from string."""
        assert Role("user") == Role.USER
        assert Role("assistant") == Role.ASSISTANT
        assert Role("tool") == Role.TOOL


class TestEpisodeStatus:
    """Tests for EpisodeStatus enum."""

    def test_status_values(self) -> None:
        """Test episode status values."""
        assert EpisodeStatus.OPEN.value == "open"
        assert EpisodeStatus.CLOSED.value == "closed"


class TestMarkerType:
    """Tests for MarkerType enum."""

    def test_marker_values(self) -> None:
        """Test marker type values."""
        assert MarkerType.DECISION.value == "decision"
        assert MarkerType.CONSTRAINT.value == "constraint"
        assert MarkerType.FAILURE.value == "failure"
        assert MarkerType.GOAL.value == "goal"


class TestTurn:
    """Tests for Turn dataclass."""

    def test_turn_creation(self) -> None:
        """Test creating a turn."""
        turn = Turn(
            id="turn_123",
            session_id="session_1",
            episode_id="ep_1",
            role=Role.USER,
            content="Hello",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )

        assert turn.id == "turn_123"
        assert turn.session_id == "session_1"
        assert turn.role == Role.USER
        assert turn.content == "Hello"
        assert turn.markers == []
        assert turn.metadata == {}

    def test_turn_to_dict(self) -> None:
        """Test turn serialization."""
        turn = Turn(
            id="turn_123",
            session_id="session_1",
            episode_id="ep_1",
            role=Role.USER,
            content="Hello",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            markers=["decision"],
            token_count=5,
        )

        data = turn.to_dict()
        assert data["id"] == "turn_123"
        assert data["role"] == "user"
        assert data["markers"] == ["decision"]
        assert data["token_count"] == 5

    def test_turn_from_dict(self) -> None:
        """Test turn deserialization."""
        data = {
            "id": "turn_123",
            "session_id": "session_1",
            "episode_id": "ep_1",
            "role": "assistant",
            "content": "Hi there!",
            "created_at": "2024-01-01T12:00:00",
            "markers": ["goal"],
            "token_count": 3,
        }

        turn = Turn.from_dict(data)
        assert turn.id == "turn_123"
        assert turn.role == Role.ASSISTANT
        assert turn.markers == ["goal"]


class TestEpisode:
    """Tests for Episode dataclass."""

    def test_episode_creation(self) -> None:
        """Test creating an episode."""
        episode = Episode(
            id="ep_123",
            session_id="session_1",
            status=EpisodeStatus.OPEN,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )

        assert episode.id == "ep_123"
        assert episode.status == EpisodeStatus.OPEN
        assert episode.closed_at is None
        assert episode.turn_count == 0

    def test_episode_to_dict(self) -> None:
        """Test episode serialization."""
        episode = Episode(
            id="ep_123",
            session_id="session_1",
            status=EpisodeStatus.CLOSED,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            closed_at=datetime(2024, 1, 1, 13, 0, 0),
            close_reason="manual",
            turn_count=5,
        )

        data = episode.to_dict()
        assert data["id"] == "ep_123"
        assert data["status"] == "closed"
        assert data["closed_at"] is not None
        assert data["turn_count"] == 5

    def test_episode_from_dict(self) -> None:
        """Test episode deserialization."""
        data = {
            "id": "ep_123",
            "session_id": "session_1",
            "status": "open",
            "created_at": "2024-01-01T12:00:00",
            "turn_count": 3,
        }

        episode = Episode.from_dict(data)
        assert episode.id == "ep_123"
        assert episode.status == EpisodeStatus.OPEN
        assert episode.turn_count == 3


class TestFact:
    """Tests for Fact dataclass."""

    def test_fact_creation(self) -> None:
        """Test creating a fact."""
        fact = Fact(
            id="fact_123",
            session_id="session_1",
            episode_id="ep_1",
            content="User prefers Python",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )

        assert fact.id == "fact_123"
        assert fact.content == "User prefers Python"
        assert fact.fact_type == MarkerType.DECISION.value
        assert fact.confidence == 1.0

    def test_fact_to_dict(self) -> None:
        """Test fact serialization."""
        fact = Fact(
            id="fact_123",
            session_id="session_1",
            episode_id="ep_1",
            content="User prefers Python",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            fact_type="constraint",
            confidence=0.9,
        )

        data = fact.to_dict()
        assert data["id"] == "fact_123"
        assert data["fact_type"] == "constraint"
        assert data["confidence"] == 0.9

    def test_fact_from_dict(self) -> None:
        """Test fact deserialization."""
        data = {
            "id": "fact_123",
            "session_id": "session_1",
            "episode_id": "ep_1",
            "content": "User prefers Python",
            "created_at": "2024-01-01T12:00:00",
            "fact_type": "goal",
            "confidence": 0.85,
        }

        fact = Fact.from_dict(data)
        assert fact.id == "fact_123"
        assert fact.fact_type == "goal"
        assert fact.confidence == 0.85


class TestVectorSearchResult:
    """Tests for VectorSearchResult dataclass."""

    def test_search_result_creation(self) -> None:
        """Test creating a search result."""
        result = VectorSearchResult(
            id="emb_123",
            score=0.95,
            metadata={"turn_id": "turn_1"},
        )

        assert result.id == "emb_123"
        assert result.score == 0.95
        assert result.metadata["turn_id"] == "turn_1"


class TestContextItem:
    """Tests for ContextItem dataclass."""

    def test_context_item_creation(self) -> None:
        """Test creating a context item."""
        item = ContextItem(
            id="turn_123",
            content="Hello",
            role=Role.USER,
            source="turn",
            score=0.9,
            token_count=5,
            markers=("decision",),
        )

        assert item.id == "turn_123"
        assert item.role == Role.USER
        assert item.source == "turn"
        assert "decision" in item.markers


class TestSessionStats:
    """Tests for SessionStats dataclass."""

    def test_session_stats_creation(self) -> None:
        """Test creating session stats."""
        now = datetime.utcnow()
        stats = SessionStats(
            session_id="session_1",
            total_turns=10,
            total_episodes=2,
            total_facts=3,
            open_episode_id="ep_2",
            open_episode_turn_count=4,
            total_tokens_ingested=500,
            created_at=now,
            last_activity_at=now,
        )

        assert stats.session_id == "session_1"
        assert stats.total_turns == 10
        assert stats.total_facts == 3
