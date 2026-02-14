"""Unit tests for storage backends."""

from datetime import datetime

import pytest

from acms.models import Episode, EpisodeStatus, Fact, MarkerType, Role, Turn
from acms.storage import InMemoryBackend
from acms.utils import generate_episode_id, generate_fact_id, generate_turn_id


@pytest.fixture
async def backend() -> InMemoryBackend:
    """Create and initialize an in-memory backend."""
    backend = InMemoryBackend()
    await backend.initialize()
    return backend


class TestInMemoryBackendTurns:
    """Tests for turn operations."""

    @pytest.mark.asyncio
    async def test_save_and_get_turn(self, backend: InMemoryBackend) -> None:
        """Test saving and retrieving a turn."""
        turn = Turn(
            id=generate_turn_id(),
            session_id="session_1",
            episode_id="ep_1",
            role=Role.USER,
            content="Hello",
            created_at=datetime.utcnow(),
            token_count=5,
        )

        await backend.save_turn(turn)
        retrieved = await backend.get_turn(turn.id)

        assert retrieved is not None
        assert retrieved.id == turn.id
        assert retrieved.content == "Hello"

    @pytest.mark.asyncio
    async def test_get_nonexistent_turn(self, backend: InMemoryBackend) -> None:
        """Test getting a non-existent turn."""
        retrieved = await backend.get_turn("nonexistent")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_turns_by_episode(self, backend: InMemoryBackend) -> None:
        """Test getting turns by episode."""
        episode_id = "ep_1"
        for i in range(3):
            turn = Turn(
                id=generate_turn_id(),
                session_id="session_1",
                episode_id=episode_id,
                role=Role.USER if i % 2 == 0 else Role.ASSISTANT,
                content=f"Message {i}",
                created_at=datetime.utcnow(),
                position=i,
            )
            await backend.save_turn(turn)

        turns = await backend.get_turns_by_episode(episode_id)
        assert len(turns) == 3
        # Check ordered by position
        for i, turn in enumerate(turns):
            assert turn.position == i

    @pytest.mark.asyncio
    async def test_get_marked_turns(self, backend: InMemoryBackend) -> None:
        """Test getting turns with markers."""
        session_id = "session_1"

        # Unmarked turn
        await backend.save_turn(
            Turn(
                id=generate_turn_id(),
                session_id=session_id,
                episode_id="ep_1",
                role=Role.USER,
                content="Hello",
                created_at=datetime.utcnow(),
            )
        )

        # Marked turn
        await backend.save_turn(
            Turn(
                id=generate_turn_id(),
                session_id=session_id,
                episode_id="ep_1",
                role=Role.ASSISTANT,
                content="Decision made",
                created_at=datetime.utcnow(),
                markers=["decision"],
            )
        )

        marked = await backend.get_marked_turns(session_id)
        assert len(marked) == 1
        assert "decision" in marked[0].markers

    @pytest.mark.asyncio
    async def test_get_marked_turns_exclude_episode(
        self, backend: InMemoryBackend
    ) -> None:
        """Test excluding an episode from marked turns."""
        session_id = "session_1"

        # Marked turn in ep_1
        await backend.save_turn(
            Turn(
                id=generate_turn_id(),
                session_id=session_id,
                episode_id="ep_1",
                role=Role.ASSISTANT,
                content="Decision 1",
                created_at=datetime.utcnow(),
                markers=["decision"],
            )
        )

        # Marked turn in ep_2
        await backend.save_turn(
            Turn(
                id=generate_turn_id(),
                session_id=session_id,
                episode_id="ep_2",
                role=Role.ASSISTANT,
                content="Decision 2",
                created_at=datetime.utcnow(),
                markers=["decision"],
            )
        )

        marked = await backend.get_marked_turns(session_id, exclude_episode_id="ep_1")
        assert len(marked) == 1
        assert marked[0].episode_id == "ep_2"


class TestInMemoryBackendEpisodes:
    """Tests for episode operations."""

    @pytest.mark.asyncio
    async def test_save_and_get_episode(self, backend: InMemoryBackend) -> None:
        """Test saving and retrieving an episode."""
        episode = Episode(
            id=generate_episode_id(),
            session_id="session_1",
            status=EpisodeStatus.OPEN,
            created_at=datetime.utcnow(),
        )

        await backend.save_episode(episode)
        retrieved = await backend.get_episode(episode.id)

        assert retrieved is not None
        assert retrieved.id == episode.id
        assert retrieved.status == EpisodeStatus.OPEN

    @pytest.mark.asyncio
    async def test_get_episodes_by_status(self, backend: InMemoryBackend) -> None:
        """Test filtering episodes by status."""
        session_id = "session_1"

        # Open episode
        await backend.save_episode(
            Episode(
                id=generate_episode_id(),
                session_id=session_id,
                status=EpisodeStatus.OPEN,
                created_at=datetime.utcnow(),
            )
        )

        # Closed episode
        await backend.save_episode(
            Episode(
                id=generate_episode_id(),
                session_id=session_id,
                status=EpisodeStatus.CLOSED,
                created_at=datetime.utcnow(),
            )
        )

        open_episodes = await backend.get_episodes(
            session_id, status=EpisodeStatus.OPEN
        )
        assert len(open_episodes) == 1
        assert open_episodes[0].status == EpisodeStatus.OPEN

    @pytest.mark.asyncio
    async def test_update_episode(self, backend: InMemoryBackend) -> None:
        """Test updating an episode."""
        episode = Episode(
            id=generate_episode_id(),
            session_id="session_1",
            status=EpisodeStatus.OPEN,
            created_at=datetime.utcnow(),
        )

        await backend.save_episode(episode)

        # Update status
        episode.status = EpisodeStatus.CLOSED
        episode.closed_at = datetime.utcnow()
        await backend.update_episode(episode)

        retrieved = await backend.get_episode(episode.id)
        assert retrieved is not None
        assert retrieved.status == EpisodeStatus.CLOSED


class TestInMemoryBackendVectors:
    """Tests for vector operations."""

    @pytest.mark.asyncio
    async def test_save_and_get_embedding(self, backend: InMemoryBackend) -> None:
        """Test saving and retrieving an embedding."""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        metadata = {"turn_id": "turn_1"}

        await backend.save_embedding("emb_1", embedding, metadata)
        retrieved = await backend.get_embedding("emb_1")

        assert retrieved is not None
        assert retrieved == embedding

    @pytest.mark.asyncio
    async def test_vector_search(self, backend: InMemoryBackend) -> None:
        """Test vector similarity search."""
        # Save some embeddings
        await backend.save_embedding(
            "emb_1", [1.0, 0.0, 0.0], {"session_id": "s1"}
        )
        await backend.save_embedding(
            "emb_2", [0.9, 0.1, 0.0], {"session_id": "s1"}
        )
        await backend.save_embedding(
            "emb_3", [0.0, 1.0, 0.0], {"session_id": "s1"}
        )

        # Search with query similar to emb_1
        results = await backend.vector_search([1.0, 0.0, 0.0], k=2)

        assert len(results) == 2
        assert results[0].id == "emb_1"  # Most similar
        assert results[0].score > 0.9

    @pytest.mark.asyncio
    async def test_vector_search_with_filter(self, backend: InMemoryBackend) -> None:
        """Test vector search with metadata filter."""
        await backend.save_embedding(
            "emb_1", [1.0, 0.0, 0.0], {"session_id": "s1"}
        )
        await backend.save_embedding(
            "emb_2", [1.0, 0.0, 0.0], {"session_id": "s2"}
        )

        results = await backend.vector_search(
            [1.0, 0.0, 0.0],
            filter={"session_id": "s1"},
        )

        assert len(results) == 1
        assert results[0].id == "emb_1"


class TestInMemoryBackendFacts:
    """Tests for fact operations."""

    @pytest.mark.asyncio
    async def test_save_and_get_facts(self, backend: InMemoryBackend) -> None:
        """Test saving and retrieving facts."""
        fact = Fact(
            id=generate_fact_id(),
            session_id="session_1",
            episode_id="ep_1",
            content="User prefers Python",
            created_at=datetime.utcnow(),
            fact_type=MarkerType.DECISION.value,
        )

        await backend.save_fact(fact)
        facts = await backend.get_facts_by_session("session_1")

        assert len(facts) == 1
        assert facts[0].content == "User prefers Python"

    @pytest.mark.asyncio
    async def test_get_facts_by_episode(self, backend: InMemoryBackend) -> None:
        """Test getting facts by episode."""
        # Fact in ep_1
        await backend.save_fact(
            Fact(
                id=generate_fact_id(),
                session_id="session_1",
                episode_id="ep_1",
                content="Fact 1",
                created_at=datetime.utcnow(),
            )
        )

        # Fact in ep_2
        await backend.save_fact(
            Fact(
                id=generate_fact_id(),
                session_id="session_1",
                episode_id="ep_2",
                content="Fact 2",
                created_at=datetime.utcnow(),
            )
        )

        facts = await backend.get_facts_by_episode("ep_1")
        assert len(facts) == 1
        assert facts[0].content == "Fact 1"


    @pytest.mark.asyncio
    async def test_get_active_facts_excludes_superseded(
        self, backend: InMemoryBackend
    ) -> None:
        """Test that get_active_facts_by_session excludes superseded facts."""
        session_id = "session_1"

        # Active fact
        active_fact = Fact(
            id="fact_active",
            session_id=session_id,
            episode_id="ep_1",
            content="Active fact",
            created_at=datetime.utcnow(),
        )
        await backend.save_fact(active_fact)

        # Superseded fact
        superseded_fact = Fact(
            id="fact_old",
            session_id=session_id,
            episode_id="ep_1",
            content="Old fact",
            created_at=datetime.utcnow(),
            superseded_by="fact_active",
        )
        await backend.save_fact(superseded_fact)

        active_facts = await backend.get_active_facts_by_session(session_id)
        assert len(active_facts) == 1
        assert active_facts[0].id == "fact_active"

    @pytest.mark.asyncio
    async def test_get_all_facts_includes_superseded(
        self, backend: InMemoryBackend
    ) -> None:
        """Test that get_facts_by_session still returns all facts."""
        session_id = "session_1"

        await backend.save_fact(
            Fact(
                id="fact_1",
                session_id=session_id,
                episode_id="ep_1",
                content="Fact 1",
                created_at=datetime.utcnow(),
            )
        )
        await backend.save_fact(
            Fact(
                id="fact_2",
                session_id=session_id,
                episode_id="ep_1",
                content="Fact 2",
                created_at=datetime.utcnow(),
                superseded_by="fact_1",
            )
        )

        all_facts = await backend.get_facts_by_session(session_id)
        assert len(all_facts) == 2

    @pytest.mark.asyncio
    async def test_update_fact(self, backend: InMemoryBackend) -> None:
        """Test updating a fact (e.g., setting superseded_by)."""
        session_id = "session_1"

        fact = Fact(
            id="fact_1",
            session_id=session_id,
            episode_id="ep_1",
            content="Original fact",
            created_at=datetime.utcnow(),
        )
        await backend.save_fact(fact)

        # Update to mark as superseded
        from dataclasses import replace

        updated = replace(fact, superseded_by="fact_2")
        await backend.update_fact(updated)

        # Verify the update persisted
        active = await backend.get_active_facts_by_session(session_id)
        assert len(active) == 0

        all_facts = await backend.get_facts_by_session(session_id)
        assert len(all_facts) == 1
        assert all_facts[0].superseded_by == "fact_2"


class TestInMemoryBackendStats:
    """Tests for session statistics."""

    @pytest.mark.asyncio
    async def test_get_session_stats(self, backend: InMemoryBackend) -> None:
        """Test getting session statistics."""
        session_id = "session_1"

        # Add an episode
        await backend.save_episode(
            Episode(
                id="ep_1",
                session_id=session_id,
                status=EpisodeStatus.OPEN,
                created_at=datetime.utcnow(),
            )
        )

        # Add turns
        await backend.save_turn(
            Turn(
                id="turn_1",
                session_id=session_id,
                episode_id="ep_1",
                role=Role.USER,
                content="Hello",
                created_at=datetime.utcnow(),
                token_count=5,
            )
        )

        # Add a fact
        await backend.save_fact(
            Fact(
                id="fact_1",
                session_id=session_id,
                episode_id="ep_1",
                content="User said hello",
                created_at=datetime.utcnow(),
            )
        )

        stats = await backend.get_session_stats(session_id)

        assert stats["session_id"] == session_id
        assert stats["total_turns"] == 1
        assert stats["total_episodes"] == 1
        assert stats["total_facts"] == 1
        assert stats["open_episode_id"] == "ep_1"
        assert stats["total_tokens_ingested"] == 5
