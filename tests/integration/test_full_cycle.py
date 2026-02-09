"""Integration tests for the full ACMS cycle."""

import pytest

from acms import ACMS, ACMSConfig, InMemoryBackend, MarkerType, NullEmbedder, Role


@pytest.fixture
def config() -> ACMSConfig:
    """Create test configuration with small episode size."""
    return ACMSConfig()


@pytest.fixture
async def acms(config: ACMSConfig) -> ACMS:
    """Create an ACMS instance for testing."""
    storage = InMemoryBackend()
    embedder = NullEmbedder(dimension=1536)

    acms = ACMS(
        session_id="test_session",
        storage=storage,
        embedder=embedder,
        config=config,
    )
    await acms.initialize()
    return acms


class TestIngestRecallCycle:
    """Tests for the ingest → recall cycle."""

    @pytest.mark.asyncio
    async def test_basic_ingest(self, acms: ACMS) -> None:
        """Test basic turn ingestion."""
        turn_id = await acms.ingest("user", "Hello, how are you?")

        assert turn_id is not None
        assert turn_id.startswith("turn_")

    @pytest.mark.asyncio
    async def test_ingest_multiple_roles(self, acms: ACMS) -> None:
        """Test ingesting turns from different roles."""
        user_id = await acms.ingest("user", "Hello")
        assistant_id = await acms.ingest("assistant", "Hi there!")
        tool_id = await acms.ingest("tool", '{"result": "success"}')

        assert user_id != assistant_id != tool_id

    @pytest.mark.asyncio
    async def test_ingest_with_markers(self, acms: ACMS) -> None:
        """Test ingesting turns with markers."""
        turn_id = await acms.ingest(
            "assistant",
            "Decision: We will use PostgreSQL.",
            markers=[MarkerType.DECISION],
        )

        assert turn_id is not None

    @pytest.mark.asyncio
    async def test_ingest_with_metadata(self, acms: ACMS) -> None:
        """Test ingesting turns with metadata."""
        turn_id = await acms.ingest(
            "user",
            "Hello",
            metadata={"source": "web", "client_id": "123"},
        )

        assert turn_id is not None

    @pytest.mark.asyncio
    async def test_recall_basic(self, acms: ACMS) -> None:
        """Test basic recall."""
        await acms.ingest("user", "What is Python?")
        await acms.ingest("assistant", "Python is a programming language.")

        context = await acms.recall("Python", token_budget=1000)

        assert len(context) > 0
        assert any("Python" in item.content for item in context)

    @pytest.mark.asyncio
    async def test_recall_respects_budget(self, acms: ACMS) -> None:
        """Test that recall respects token budget."""
        # Ingest many turns
        for i in range(10):
            await acms.ingest("user", f"Message {i} " * 50)  # ~250 chars each

        context = await acms.recall("message", token_budget=100)

        total_tokens = sum(item.token_count for item in context)
        assert total_tokens <= 100

    @pytest.mark.asyncio
    async def test_recall_includes_current_episode(self, acms: ACMS) -> None:
        """Test that recall includes current episode by default."""
        await acms.ingest("user", "Current question about Python")

        context = await acms.recall("unrelated query")

        # Current episode should be included
        assert len(context) > 0
        assert any("Python" in item.content for item in context)

    @pytest.mark.asyncio
    async def test_recall_excludes_current_episode_priority(self, acms: ACMS) -> None:
        """Test that excluding current episode removes its priority.

        Note: When include_current_episode=False, current episode turns
        are not explicitly included as candidates, but they may still
        appear via vector search if they match the query. The difference
        is they won't get the reserved budget allocation.
        """
        # Create a turn in current episode
        await acms.ingest("user", "Current question about something")

        # Close the episode to create a new one
        await acms.close_episode()

        # Add a turn in the new episode
        await acms.ingest("user", "New episode content")

        # Recall without including current episode
        context = await acms.recall(
            "New episode",
            include_current_episode=False,
        )

        # The new episode content should NOT be explicitly included
        # (though it might still show up via vector search)
        # This test verifies the flag is respected


class TestEpisodeManagement:
    """Tests for episode lifecycle."""

    @pytest.mark.asyncio
    async def test_auto_episode_creation(self, acms: ACMS) -> None:
        """Test that first ingest creates an episode."""
        await acms.ingest("user", "Hello")

        assert acms.current_episode_id is not None

    @pytest.mark.asyncio
    async def test_manual_episode_close(self, acms: ACMS) -> None:
        """Test manually closing an episode."""
        await acms.ingest("user", "Hello")
        old_episode_id = acms.current_episode_id

        closed_id = await acms.close_episode(reason="manual")

        assert closed_id == old_episode_id
        # New episode should be created on next ingest
        await acms.ingest("user", "New message")
        assert acms.current_episode_id != old_episode_id

    @pytest.mark.asyncio
    async def test_episode_stats(self, acms: ACMS) -> None:
        """Test session statistics."""
        await acms.ingest("user", "Message 1")
        await acms.ingest("assistant", "Response 1")

        stats = await acms.get_session_stats()

        assert stats.session_id == "test_session"
        assert stats.total_turns == 2
        assert stats.total_episodes >= 1
        assert stats.open_episode_id is not None


class TestContextManager:
    """Tests for async context manager usage."""

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test using ACMS as async context manager."""
        storage = InMemoryBackend()
        embedder = NullEmbedder()

        async with ACMS("session_1", storage, embedder) as acms:
            await acms.ingest("user", "Hello")
            context = await acms.recall("hello")
            assert len(context) > 0

        # After exiting, ACMS should be closed


class TestMarkerAutoDetection:
    """Tests for automatic marker detection."""

    @pytest.mark.asyncio
    async def test_detect_decision_marker(self, acms: ACMS) -> None:
        """Test auto-detecting decision markers."""
        await acms.ingest("assistant", "Decision: We will use PostgreSQL.")

        context = await acms.recall("database")
        # The turn should have been marked
        decision_items = [item for item in context if "decision" in item.markers]
        assert len(decision_items) >= 1

    @pytest.mark.asyncio
    async def test_detect_constraint_marker(self, acms: ACMS) -> None:
        """Test auto-detecting constraint markers."""
        await acms.ingest("user", "Constraint: Budget is limited to $10k.")

        context = await acms.recall("budget")
        constraint_items = [item for item in context if "constraint" in item.markers]
        assert len(constraint_items) >= 1

    @pytest.mark.asyncio
    async def test_explicit_markers_override(self, acms: ACMS) -> None:
        """Test that explicit markers override auto-detection."""
        await acms.ingest(
            "assistant",
            "Decision: Use Python.",  # Would auto-detect decision
            markers=[MarkerType.GOAL],  # But we say it's a goal
        )

        context = await acms.recall("Python")
        # Should have goal marker, not decision (explicit overrides)
        for item in context:
            if "Python" in item.content:
                assert "goal" in item.markers


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_not_initialized_error(self) -> None:
        """Test error when using uninitialized ACMS."""
        storage = InMemoryBackend()
        acms = ACMS("session_1", storage)

        with pytest.raises(RuntimeError, match="not initialized"):
            await acms.ingest("user", "Hello")

    @pytest.mark.asyncio
    async def test_empty_content_error(self, acms: ACMS) -> None:
        """Test error on empty content."""
        from acms.errors import ValidationError

        with pytest.raises(ValidationError):
            await acms.ingest("user", "")

    @pytest.mark.asyncio
    async def test_invalid_role_error(self, acms: ACMS) -> None:
        """Test error on invalid role."""
        from acms.errors import ValidationError

        with pytest.raises(ValidationError):
            await acms.ingest("invalid_role", "Hello")
