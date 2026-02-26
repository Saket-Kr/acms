"""Shared test fixtures for Gleanr."""

from __future__ import annotations

from datetime import datetime
from typing import Any, AsyncGenerator

import pytest

from gleanr import Gleanr, GleanrConfig, InMemoryBackend, NullEmbedder
from gleanr.models import Episode, EpisodeStatus, Fact, MarkerType, Role, Turn
from gleanr.utils import (
    HeuristicTokenCounter,
    generate_episode_id,
    generate_fact_id,
    generate_turn_id,
)


@pytest.fixture
def token_counter() -> HeuristicTokenCounter:
    """Create a heuristic token counter."""
    return HeuristicTokenCounter()


@pytest.fixture
def null_embedder() -> NullEmbedder:
    """Create a null embedder for testing."""
    return NullEmbedder(dimension=1536)


@pytest.fixture
def storage() -> InMemoryBackend:
    """Create an in-memory storage backend."""
    return InMemoryBackend()


@pytest.fixture
def config() -> GleanrConfig:
    """Create default Gleanr configuration."""
    return GleanrConfig()


@pytest.fixture
async def initialized_storage(storage: InMemoryBackend) -> AsyncGenerator[InMemoryBackend, None]:
    """Create and initialize an in-memory storage backend."""
    await storage.initialize()
    yield storage
    await storage.close()


@pytest.fixture
async def gleanr_instance(
    storage: InMemoryBackend,
    null_embedder: NullEmbedder,
    config: GleanrConfig,
) -> AsyncGenerator[Gleanr, None]:
    """Create an initialized Gleanr instance for testing."""
    gleanr = Gleanr(
        session_id="test_session",
        storage=storage,
        embedder=null_embedder,
        config=config,
    )
    await gleanr.initialize()
    yield gleanr
    await gleanr.close()


@pytest.fixture
def sample_turn() -> Turn:
    """Create a sample turn for testing."""
    return Turn(
        id=generate_turn_id(),
        session_id="test_session",
        episode_id="ep_123",
        role=Role.USER,
        content="Hello, how are you?",
        created_at=datetime.utcnow(),
        markers=[],
        metadata={},
        token_count=5,
        position=0,
    )


@pytest.fixture
def sample_episode() -> Episode:
    """Create a sample episode for testing."""
    return Episode(
        id=generate_episode_id(),
        session_id="test_session",
        status=EpisodeStatus.OPEN,
        created_at=datetime.utcnow(),
        turn_count=0,
        total_tokens=0,
        markers=[],
        metadata={},
    )


@pytest.fixture
def sample_fact() -> Fact:
    """Create a sample fact for testing."""
    return Fact(
        id=generate_fact_id(),
        session_id="test_session",
        episode_id="ep_123",
        content="User prefers Python over JavaScript",
        created_at=datetime.utcnow(),
        fact_type=MarkerType.DECISION.value,
        confidence=0.9,
        token_count=7,
        metadata={},
    )


@pytest.fixture
def marked_turn() -> Turn:
    """Create a turn with markers for testing."""
    return Turn(
        id=generate_turn_id(),
        session_id="test_session",
        episode_id="ep_123",
        role=Role.ASSISTANT,
        content="Decision: We will use PostgreSQL for the database.",
        created_at=datetime.utcnow(),
        markers=[MarkerType.DECISION.value],
        metadata={},
        token_count=10,
        position=1,
    )
