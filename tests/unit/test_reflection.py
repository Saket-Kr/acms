"""Unit tests for ReflectionRunner including consolidation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from gleanr.core.config import GleanrConfig, ReflectionConfig
from gleanr.memory.reflection import ReflectionRunner
from gleanr.models import Episode, EpisodeStatus, Fact, MarkerType, Role, Turn
from gleanr.models.consolidation import ConsolidationAction, ConsolidationActionType
from gleanr.providers.base import NullEmbedder
from gleanr.storage.memory import InMemoryBackend
from gleanr.utils import HeuristicTokenCounter, generate_episode_id, generate_fact_id


# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------


class FakeReflector:
    """Legacy reflector — only implements Reflector protocol."""

    def __init__(self, facts_to_return: list[Fact] | None = None) -> None:
        self._facts = facts_to_return or []
        self.reflect_calls: list[tuple[Episode, list[Turn]]] = []

    async def reflect(self, episode: Episode, turns: list[Turn]) -> list[Fact]:
        self.reflect_calls.append((episode, turns))
        return list(self._facts)


class FakeConsolidatingReflector:
    """Reflector that implements both Reflector and ConsolidatingReflector."""

    def __init__(
        self,
        facts_to_return: list[Fact] | None = None,
        actions_to_return: list[ConsolidationAction] | None = None,
    ) -> None:
        self._facts = facts_to_return or []
        self._actions = actions_to_return or []
        self.reflect_calls: list[tuple[Episode, list[Turn]]] = []
        self.consolidation_calls: list[tuple[Episode, list[Turn], list[Fact]]] = []

    async def reflect(self, episode: Episode, turns: list[Turn]) -> list[Fact]:
        self.reflect_calls.append((episode, turns))
        return list(self._facts)

    async def reflect_with_consolidation(
        self,
        episode: Episode,
        turns: list[Turn],
        prior_facts: list[Fact],
    ) -> list[ConsolidationAction]:
        self.consolidation_calls.append((episode, turns, prior_facts))
        return list(self._actions)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_episode(
    episode_id: str = "ep_1",
    session_id: str = "test_session",
) -> Episode:
    return Episode(
        id=episode_id,
        session_id=session_id,
        status=EpisodeStatus.CLOSED,
        created_at=datetime.utcnow(),
        turn_count=3,
        total_tokens=100,
    )


def _make_turns(
    episode_id: str = "ep_1",
    session_id: str = "test_session",
    count: int = 3,
) -> list[Turn]:
    turns = []
    for i in range(count):
        turns.append(
            Turn(
                id=f"turn_{episode_id}_{i}",
                session_id=session_id,
                episode_id=episode_id,
                role=Role.USER if i % 2 == 0 else Role.ASSISTANT,
                content=f"Message {i} for {episode_id}",
                created_at=datetime.utcnow(),
                position=i,
            )
        )
    return turns


def _make_fact(
    fact_id: str | None = None,
    session_id: str = "test_session",
    episode_id: str = "ep_1",
    content: str = "Test fact",
    confidence: float = 0.9,
    fact_type: str = MarkerType.DECISION.value,
) -> Fact:
    return Fact(
        id=fact_id or generate_fact_id(),
        session_id=session_id,
        episode_id=episode_id,
        content=content,
        created_at=datetime.utcnow(),
        fact_type=fact_type,
        confidence=confidence,
    )


async def _build_runner(
    reflector: Any,
    storage: InMemoryBackend | None = None,
    config: GleanrConfig | None = None,
    session_id: str = "test_session",
) -> tuple[ReflectionRunner, InMemoryBackend]:
    storage = storage or InMemoryBackend()
    await storage.initialize()
    config = config or GleanrConfig()
    runner = ReflectionRunner(
        session_id=session_id,
        storage=storage,
        reflector=reflector,
        embedder=NullEmbedder(dimension=4),
        token_counter=HeuristicTokenCounter(),
        config=config,
    )
    return runner, storage


# ---------------------------------------------------------------------------
# Tests: _supports_consolidation detection
# ---------------------------------------------------------------------------


class TestSupportsConsolidation:
    """Tests for reflector capability detection."""

    @pytest.mark.asyncio
    async def test_legacy_reflector_not_detected(self) -> None:
        runner, _ = await _build_runner(FakeReflector())
        assert runner._supports_consolidation() is False

    @pytest.mark.asyncio
    async def test_consolidating_reflector_detected(self) -> None:
        runner, _ = await _build_runner(FakeConsolidatingReflector())
        assert runner._supports_consolidation() is True


# ---------------------------------------------------------------------------
# Tests: Legacy path
# ---------------------------------------------------------------------------


class TestLegacyReflection:
    """Tests for the legacy reflection path."""

    @pytest.mark.asyncio
    async def test_basic_reflection(self) -> None:
        fact = _make_fact(content="Extracted fact")
        reflector = FakeReflector(facts_to_return=[fact])
        runner, storage = await _build_runner(reflector)

        episode = _make_episode()
        turns = _make_turns()
        result = await runner.reflect_episode(episode, turns)

        assert len(result) == 1
        assert result[0].content == "Extracted fact"
        assert len(reflector.reflect_calls) == 1

        # Verify fact was persisted
        stored = await storage.get_facts_by_session("test_session")
        assert len(stored) == 1

    @pytest.mark.asyncio
    async def test_confidence_filtering(self) -> None:
        low_conf = _make_fact(content="Low confidence", confidence=0.3)
        high_conf = _make_fact(content="High confidence", confidence=0.9)
        reflector = FakeReflector(facts_to_return=[low_conf, high_conf])
        runner, storage = await _build_runner(reflector)

        episode = _make_episode()
        turns = _make_turns()
        result = await runner.reflect_episode(episode, turns)

        assert len(result) == 1
        assert result[0].content == "High confidence"

    @pytest.mark.asyncio
    async def test_max_facts_cap(self) -> None:
        facts = [_make_fact(content=f"Fact {i}") for i in range(10)]
        reflector = FakeReflector(facts_to_return=facts)
        config = GleanrConfig(
            reflection=ReflectionConfig(max_facts_per_episode=3)
        )
        runner, _ = await _build_runner(reflector, config=config)

        episode = _make_episode()
        turns = _make_turns()
        result = await runner.reflect_episode(episode, turns)

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_disabled_reflection(self) -> None:
        reflector = FakeReflector(facts_to_return=[_make_fact()])
        config = GleanrConfig(reflection=ReflectionConfig(enabled=False))
        runner, _ = await _build_runner(reflector, config=config)

        result = await runner.reflect_episode(_make_episode(), _make_turns())
        assert result == []
        assert len(reflector.reflect_calls) == 0

    @pytest.mark.asyncio
    async def test_min_turns_carries_forward(self) -> None:
        """Turns below min_episode_turns are carried forward, not discarded."""
        reflector = FakeReflector(facts_to_return=[_make_fact()])
        config = GleanrConfig(reflection=ReflectionConfig(min_episode_turns=5))
        runner, _ = await _build_runner(reflector, config=config)

        # Only 3 turns, below min — carried forward, not reflected
        result = await runner.reflect_episode(_make_episode(), _make_turns(count=3))
        assert result == []
        assert len(reflector.reflect_calls) == 0
        assert len(runner._carried_turns) == 3


# ---------------------------------------------------------------------------
# Tests: Consolidation path
# ---------------------------------------------------------------------------


class TestConsolidation:
    """Tests for the consolidation reflection path."""

    @pytest.mark.asyncio
    async def test_first_episode_uses_legacy(self) -> None:
        """First episode has no prior facts, should use legacy path."""
        fact = _make_fact(content="First episode fact")
        reflector = FakeConsolidatingReflector(facts_to_return=[fact])
        runner, _ = await _build_runner(reflector)

        result = await runner.reflect_episode(_make_episode(), _make_turns())

        # Legacy path used (no consolidation calls)
        assert len(reflector.reflect_calls) == 1
        assert len(reflector.consolidation_calls) == 0
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_consolidation_with_prior_facts(self) -> None:
        """Second episode with prior facts triggers consolidation."""
        storage = InMemoryBackend()
        await storage.initialize()

        # Pre-populate prior fact
        prior = _make_fact(fact_id="fact_prior", content="Prior fact")
        await storage.save_fact(prior)

        actions = [
            ConsolidationAction(
                action=ConsolidationActionType.KEEP,
                content="Prior fact",
                source_fact_id="fact_prior",
            ),
            ConsolidationAction(
                action=ConsolidationActionType.ADD,
                content="New fact from consolidation",
                confidence=0.9,
            ),
        ]
        reflector = FakeConsolidatingReflector(actions_to_return=actions)
        runner, storage = await _build_runner(reflector, storage=storage)

        episode = _make_episode(episode_id="ep_2")
        turns = _make_turns(episode_id="ep_2")
        result = await runner.reflect_episode(episode, turns)

        # Consolidation path used
        assert len(reflector.consolidation_calls) == 1
        assert len(reflector.reflect_calls) == 0

        # ADD produces one new fact
        assert len(result) == 1
        assert result[0].content == "New fact from consolidation"

    @pytest.mark.asyncio
    async def test_update_action_supersedes(self) -> None:
        """UPDATE action creates new fact and marks old as superseded."""
        storage = InMemoryBackend()
        await storage.initialize()

        prior = _make_fact(fact_id="fact_old", content="Old content")
        await storage.save_fact(prior)

        actions = [
            ConsolidationAction(
                action=ConsolidationActionType.UPDATE,
                content="Updated content",
                source_fact_id="fact_old",
                confidence=0.95,
                reason="content changed",
            ),
        ]
        reflector = FakeConsolidatingReflector(actions_to_return=actions)
        runner, storage = await _build_runner(reflector, storage=storage)

        result = await runner.reflect_episode(
            _make_episode(episode_id="ep_2"),
            _make_turns(episode_id="ep_2"),
        )

        assert len(result) == 1
        assert result[0].content == "Updated content"
        assert result[0].supersedes == ["fact_old"]

        # Old fact should be superseded
        all_facts = await storage.get_facts_by_session("test_session")
        old = next(f for f in all_facts if f.id == "fact_old")
        assert old.superseded_by == result[0].id

        # Only new fact should be active
        active = await storage.get_active_facts_by_session("test_session")
        assert len(active) == 1
        assert active[0].content == "Updated content"

    @pytest.mark.asyncio
    async def test_remove_action_supersedes(self) -> None:
        """REMOVE action marks old fact as superseded with sentinel."""
        storage = InMemoryBackend()
        await storage.initialize()

        prior = _make_fact(fact_id="fact_gone", content="Contradicted fact")
        await storage.save_fact(prior)

        actions = [
            ConsolidationAction(
                action=ConsolidationActionType.REMOVE,
                content="Contradicted fact",
                source_fact_id="fact_gone",
                reason="user changed mind",
            ),
        ]
        reflector = FakeConsolidatingReflector(actions_to_return=actions)
        runner, storage = await _build_runner(reflector, storage=storage)

        result = await runner.reflect_episode(
            _make_episode(episode_id="ep_2"),
            _make_turns(episode_id="ep_2"),
        )

        # REMOVE produces no new facts
        assert len(result) == 0

        # Old fact superseded with sentinel
        all_facts = await storage.get_facts_by_session("test_session")
        assert all_facts[0].superseded_by == "removed_by_ep_2"

        active = await storage.get_active_facts_by_session("test_session")
        assert len(active) == 0

    @pytest.mark.asyncio
    async def test_unknown_fact_id_skipped(self) -> None:
        """UPDATE/REMOVE with unknown source_fact_id is logged and skipped."""
        storage = InMemoryBackend()
        await storage.initialize()

        prior = _make_fact(fact_id="fact_real", content="Real fact")
        await storage.save_fact(prior)

        actions = [
            ConsolidationAction(
                action=ConsolidationActionType.KEEP,
                content="Real fact",
                source_fact_id="fact_real",
            ),
            ConsolidationAction(
                action=ConsolidationActionType.UPDATE,
                content="Update to unknown",
                source_fact_id="fact_nonexistent",
                confidence=0.9,
            ),
        ]
        reflector = FakeConsolidatingReflector(actions_to_return=actions)
        runner, storage = await _build_runner(reflector, storage=storage)

        result = await runner.reflect_episode(
            _make_episode(episode_id="ep_2"),
            _make_turns(episode_id="ep_2"),
        )

        # Unknown ID skipped, no error
        assert len(result) == 0

        # Real fact still active
        active = await storage.get_active_facts_by_session("test_session")
        assert len(active) == 1
        assert active[0].id == "fact_real"

    @pytest.mark.asyncio
    async def test_empty_actions_falls_back_to_legacy(self) -> None:
        """If consolidation returns empty actions, fall back to legacy."""
        storage = InMemoryBackend()
        await storage.initialize()

        prior = _make_fact(fact_id="fact_p", content="Prior")
        await storage.save_fact(prior)

        legacy_fact = _make_fact(content="Legacy extracted")
        reflector = FakeConsolidatingReflector(
            facts_to_return=[legacy_fact],
            actions_to_return=[],
        )
        runner, storage = await _build_runner(reflector, storage=storage)

        result = await runner.reflect_episode(
            _make_episode(episode_id="ep_2"),
            _make_turns(episode_id="ep_2"),
        )

        # Fallback to legacy
        assert len(reflector.consolidation_calls) == 1
        assert len(reflector.reflect_calls) == 1
        assert len(result) == 1
        assert result[0].content == "Legacy extracted"

    @pytest.mark.asyncio
    async def test_add_below_min_confidence_filtered(self) -> None:
        """ADD actions below min_confidence are filtered out."""
        storage = InMemoryBackend()
        await storage.initialize()

        prior = _make_fact(fact_id="fact_p", content="Prior")
        await storage.save_fact(prior)

        actions = [
            ConsolidationAction(
                action=ConsolidationActionType.KEEP,
                content="Prior",
                source_fact_id="fact_p",
            ),
            ConsolidationAction(
                action=ConsolidationActionType.ADD,
                content="Low confidence new fact",
                confidence=0.3,
            ),
        ]
        reflector = FakeConsolidatingReflector(actions_to_return=actions)
        runner, storage = await _build_runner(reflector, storage=storage)

        result = await runner.reflect_episode(
            _make_episode(episode_id="ep_2"),
            _make_turns(episode_id="ep_2"),
        )

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_legacy_reflector_always_uses_legacy_path(self) -> None:
        """A legacy reflector never triggers consolidation, even with prior facts."""
        storage = InMemoryBackend()
        await storage.initialize()

        prior = _make_fact(fact_id="fact_p", content="Prior")
        await storage.save_fact(prior)

        legacy_fact = _make_fact(content="Legacy fact")
        reflector = FakeReflector(facts_to_return=[legacy_fact])
        runner, _ = await _build_runner(reflector, storage=storage)

        result = await runner.reflect_episode(
            _make_episode(episode_id="ep_2"),
            _make_turns(episode_id="ep_2"),
        )

        assert len(result) == 1
        assert result[0].content == "Legacy fact"
        assert len(reflector.reflect_calls) == 1


# ---------------------------------------------------------------------------
# Tests: Scoping
# ---------------------------------------------------------------------------


class TestFactScoping:
    """Tests for _scope_relevant_facts."""

    @pytest.mark.asyncio
    async def test_null_embedder_includes_all_facts(self) -> None:
        """NullEmbedder (zero vectors) should include all prior facts."""
        storage = InMemoryBackend()
        await storage.initialize()

        facts = [_make_fact(fact_id=f"f{i}", content=f"Fact {i}") for i in range(5)]
        for f in facts:
            await storage.save_fact(f)

        runner, _ = await _build_runner(
            FakeConsolidatingReflector(), storage=storage
        )

        episode = _make_episode(episode_id="ep_2")
        turns = _make_turns(episode_id="ep_2")

        result = await runner._scope_relevant_facts(episode, turns, facts)
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_facts_without_embeddings_always_included(self) -> None:
        """Facts without embedding_id are always included in scope."""
        storage = InMemoryBackend()
        await storage.initialize()

        fact_no_emb = _make_fact(fact_id="f1", content="No embedding")
        # fact_no_emb.embedding_id is None by default
        assert fact_no_emb.embedding_id is None

        runner, _ = await _build_runner(
            FakeConsolidatingReflector(), storage=storage
        )

        episode = _make_episode()
        turns = _make_turns()

        # With NullEmbedder this will include all anyway, but the code
        # path for facts without embeddings is tested
        result = await runner._scope_relevant_facts(episode, turns, [fact_no_emb])
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_empty_prior_facts_returns_empty(self) -> None:
        runner, _ = await _build_runner(FakeConsolidatingReflector())
        result = await runner._scope_relevant_facts(
            _make_episode(), _make_turns(), []
        )
        assert result == []


# ---------------------------------------------------------------------------
# Tests: Carry-forward for short episodes
# ---------------------------------------------------------------------------


class TestCarryForward:
    """Tests for buffering turns from episodes that are too short."""

    @pytest.mark.asyncio
    async def test_short_episode_carries_forward(self) -> None:
        """Turns from a 1-turn episode are carried into the next reflection."""
        fact = _make_fact(content="Combined fact")
        reflector = FakeReflector(facts_to_return=[fact])
        config = GleanrConfig(reflection=ReflectionConfig(min_episode_turns=3))
        runner, storage = await _build_runner(reflector, config=config)

        # Episode 1: only 1 turn — too short, gets carried
        ep1 = _make_episode(episode_id="ep_1")
        turns1 = _make_turns(episode_id="ep_1", count=1)
        result1 = await runner.reflect_episode(ep1, turns1)
        assert result1 == []
        assert len(reflector.reflect_calls) == 0

        # Episode 2: 3 turns — combined with carried = 4, meets threshold
        ep2 = _make_episode(episode_id="ep_2")
        turns2 = _make_turns(episode_id="ep_2", count=3)
        result2 = await runner.reflect_episode(ep2, turns2)

        assert len(result2) == 1
        assert len(reflector.reflect_calls) == 1

        # Reflector received all 4 turns (1 carried + 3 new)
        _, reflected_turns = reflector.reflect_calls[0]
        assert len(reflected_turns) == 4

    @pytest.mark.asyncio
    async def test_multiple_short_episodes_accumulate(self) -> None:
        """Multiple short episodes accumulate until threshold is met."""
        fact = _make_fact(content="Accumulated fact")
        reflector = FakeReflector(facts_to_return=[fact])
        config = GleanrConfig(reflection=ReflectionConfig(min_episode_turns=4))
        runner, _ = await _build_runner(reflector, config=config)

        # Three 1-turn episodes: carried = 3, still below 4
        for i in range(3):
            ep = _make_episode(episode_id=f"ep_{i}")
            turns = _make_turns(episode_id=f"ep_{i}", count=1)
            result = await runner.reflect_episode(ep, turns)
            assert result == []

        assert len(reflector.reflect_calls) == 0

        # Episode 4: 1 turn — combined = 4, meets threshold
        ep4 = _make_episode(episode_id="ep_3")
        turns4 = _make_turns(episode_id="ep_3", count=1)
        result = await runner.reflect_episode(ep4, turns4)

        assert len(result) == 1
        _, reflected_turns = reflector.reflect_calls[0]
        assert len(reflected_turns) == 4

    @pytest.mark.asyncio
    async def test_flush_carried_turns(self) -> None:
        """flush_carried_turns forces reflection on buffered turns."""
        fact = _make_fact(content="Flushed fact")
        reflector = FakeReflector(facts_to_return=[fact])
        config = GleanrConfig(reflection=ReflectionConfig(min_episode_turns=5))
        runner, storage = await _build_runner(reflector, config=config)

        # Episode with 2 turns — below threshold, gets carried
        ep = _make_episode(episode_id="ep_1")
        turns = _make_turns(episode_id="ep_1", count=2)
        result = await runner.reflect_episode(ep, turns)
        assert result == []
        assert len(reflector.reflect_calls) == 0

        # Flush forces reflection regardless of count
        flushed = await runner.flush_carried_turns(ep)
        assert len(flushed) == 1
        assert flushed[0].content == "Flushed fact"
        assert len(reflector.reflect_calls) == 1

        # Buffer is now empty
        assert runner._carried_turns == []

    @pytest.mark.asyncio
    async def test_flush_empty_buffer_returns_empty(self) -> None:
        """flush_carried_turns with no buffered turns returns empty."""
        runner, _ = await _build_runner(FakeReflector())
        result = await runner.flush_carried_turns(_make_episode())
        assert result == []

    @pytest.mark.asyncio
    async def test_carried_turns_cleared_after_reflection(self) -> None:
        """After successful reflection, carried turns are cleared."""
        fact = _make_fact(content="Test")
        reflector = FakeReflector(facts_to_return=[fact])
        config = GleanrConfig(reflection=ReflectionConfig(min_episode_turns=2))
        runner, _ = await _build_runner(reflector, config=config)

        # 1 turn → carried
        ep1 = _make_episode(episode_id="ep_1")
        await runner.reflect_episode(ep1, _make_turns(episode_id="ep_1", count=1))
        assert len(runner._carried_turns) == 1

        # 2 turns → combined = 3, reflection runs, buffer cleared
        ep2 = _make_episode(episode_id="ep_2")
        await runner.reflect_episode(ep2, _make_turns(episode_id="ep_2", count=2))
        assert runner._carried_turns == []


# ---------------------------------------------------------------------------
# Reflection Tracing Tests
# ---------------------------------------------------------------------------


class TestReflectionTracing:
    """Tests for the reflection tracing / observability feature."""

    @pytest.mark.asyncio
    async def test_legacy_trace_emitted(self) -> None:
        """Trace is emitted for legacy reflection with correct fields."""
        from gleanr.memory.reflection import ReflectionTrace

        fact = _make_fact(content="Database is PostgreSQL")
        reflector = FakeReflector(facts_to_return=[fact])
        runner, _ = await _build_runner(reflector)

        traces: list[ReflectionTrace] = []
        runner.set_trace_callback(traces.append)

        episode = _make_episode()
        turns = _make_turns(count=3)
        await runner.reflect_episode(episode, turns)

        assert len(traces) == 1
        trace = traces[0]
        assert trace.episode_id == episode.id
        assert trace.mode == "legacy"
        assert trace.input_turn_count == 3
        assert len(trace.input_turns) == 3
        assert trace.raw_facts is not None
        assert len(trace.raw_facts) == 1
        assert trace.raw_facts[0]["content"] == "Database is PostgreSQL"
        assert len(trace.saved_facts) == 1
        assert trace.elapsed_ms >= 0
        # Consolidation fields should be None for legacy
        assert trace.prior_facts is None
        assert trace.raw_actions is None

    @pytest.mark.asyncio
    async def test_consolidation_trace_emitted(self) -> None:
        """Trace is emitted for consolidation with prior facts and actions."""
        from gleanr.memory.reflection import ReflectionTrace

        prior_fact = _make_fact(
            fact_id="fact_prior",
            content="Database is PostgreSQL",
        )
        actions = [
            ConsolidationAction(
                action=ConsolidationActionType.UPDATE,
                content="Database is MySQL (changed from PostgreSQL)",
                fact_type=MarkerType.DECISION.value,
                confidence=0.9,
                source_fact_id="fact_prior",
                reason="user switched to MySQL",
            ),
        ]
        reflector = FakeConsolidatingReflector(actions_to_return=actions)
        runner, storage = await _build_runner(reflector)

        # Save prior fact so consolidation path is triggered
        await storage.save_fact(prior_fact)

        traces: list[ReflectionTrace] = []
        runner.set_trace_callback(traces.append)

        episode = _make_episode(episode_id="ep_2")
        turns = _make_turns(episode_id="ep_2", count=3)
        await runner.reflect_episode(episode, turns)

        assert len(traces) == 1
        trace = traces[0]
        assert trace.mode == "consolidation"
        assert trace.prior_facts is not None
        assert len(trace.prior_facts) == 1
        assert trace.prior_facts[0]["content"] == "Database is PostgreSQL"
        assert trace.scoped_fact_count is not None
        assert trace.raw_actions is not None
        assert len(trace.raw_actions) == 1
        assert trace.raw_actions[0]["action"] == "update"
        assert len(trace.saved_facts) == 1
        assert len(trace.superseded_facts) == 1
        assert trace.superseded_facts[0]["id"] == "fact_prior"

    @pytest.mark.asyncio
    async def test_no_trace_when_callback_not_set(self) -> None:
        """No trace emitted when callback is None."""
        fact = _make_fact(content="Test")
        reflector = FakeReflector(facts_to_return=[fact])
        runner, _ = await _build_runner(reflector)

        # No callback set — should not raise
        episode = _make_episode()
        turns = _make_turns(count=3)
        result = await runner.reflect_episode(episode, turns)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_trace_callback_exception_does_not_crash(self) -> None:
        """If trace callback raises, reflection still succeeds."""
        fact = _make_fact(content="Test")
        reflector = FakeReflector(facts_to_return=[fact])
        runner, _ = await _build_runner(reflector)

        def bad_callback(trace: Any) -> None:
            raise RuntimeError("callback exploded")

        runner.set_trace_callback(bad_callback)

        episode = _make_episode()
        turns = _make_turns(count=3)
        result = await runner.reflect_episode(episode, turns)
        # Should still succeed despite callback error
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_trace_to_dict(self) -> None:
        """ReflectionTrace.to_dict() produces a serializable dict."""
        from gleanr.memory.reflection import ReflectionTrace

        fact = _make_fact(content="Test fact")
        reflector = FakeReflector(facts_to_return=[fact])
        runner, _ = await _build_runner(reflector)

        traces: list[ReflectionTrace] = []
        runner.set_trace_callback(traces.append)

        await runner.reflect_episode(_make_episode(), _make_turns(count=3))

        d = traces[0].to_dict()
        assert isinstance(d, dict)
        assert d["mode"] == "legacy"
        assert d["input_turn_count"] == 3
        assert isinstance(d["saved_facts"], list)

    @pytest.mark.asyncio
    async def test_disable_trace_callback(self) -> None:
        """Setting callback to None disables tracing."""
        from gleanr.memory.reflection import ReflectionTrace

        fact = _make_fact(content="Test")
        reflector = FakeReflector(facts_to_return=[fact])
        runner, _ = await _build_runner(reflector)

        traces: list[ReflectionTrace] = []
        runner.set_trace_callback(traces.append)
        runner.set_trace_callback(None)

        await runner.reflect_episode(_make_episode(), _make_turns(count=3))
        assert len(traces) == 0


# ---------------------------------------------------------------------------
# Deduplication Tests
# ---------------------------------------------------------------------------


class DeterministicEmbedder:
    """Embedder that returns deterministic embeddings based on content hash.

    Identical content produces identical embeddings. Different content
    produces different embeddings. This allows testing dedup logic.
    """

    def __init__(self, dimension: int = 4) -> None:
        self._dimension = dimension

    async def embed(self, texts: list[str]) -> list[list[float]]:
        import hashlib

        results = []
        for text in texts:
            h = hashlib.sha256(text.encode()).digest()
            vec = [b / 255.0 for b in h[: self._dimension]]
            results.append(vec)
        return results


class TestDeduplication:
    """Tests for post-consolidation duplicate detection."""

    @pytest.mark.asyncio
    async def test_duplicate_add_is_skipped(self) -> None:
        """ADD that duplicates an existing fact is skipped."""
        # Create a prior fact with known content
        prior_fact = _make_fact(fact_id="fact_existing", content="Database is PostgreSQL")

        # Consolidation tries to ADD the exact same content
        actions = [
            ConsolidationAction(
                action=ConsolidationActionType.KEEP,
                content="Database is PostgreSQL",
                fact_type=MarkerType.DECISION.value,
                confidence=0.9,
                source_fact_id="fact_existing",
            ),
            ConsolidationAction(
                action=ConsolidationActionType.ADD,
                content="Database is PostgreSQL",  # Exact duplicate
                fact_type=MarkerType.DECISION.value,
                confidence=0.9,
            ),
        ]
        reflector = FakeConsolidatingReflector(actions_to_return=actions)

        storage = InMemoryBackend()
        await storage.initialize()

        embedder = DeterministicEmbedder(dimension=4)
        config = GleanrConfig(reflection=ReflectionConfig(dedup_similarity_threshold=0.95))

        runner = ReflectionRunner(
            session_id="test_session",
            storage=storage,
            reflector=reflector,
            embedder=embedder,
            token_counter=HeuristicTokenCounter(),
            config=config,
        )

        # Save prior fact WITH embedding so dedup can compare
        emb = (await embedder.embed([prior_fact.content]))[0]
        await storage.save_embedding(id="emb_existing", embedding=emb, metadata={})
        prior_fact.embedding_id = "emb_existing"
        await storage.save_fact(prior_fact)

        episode = _make_episode(episode_id="ep_2")
        turns = _make_turns(episode_id="ep_2", count=3)
        result = await runner.reflect_episode(episode, turns)

        # Duplicate ADD should be skipped
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_non_duplicate_add_is_saved(self) -> None:
        """ADD with genuinely new content is saved."""
        prior_fact = _make_fact(fact_id="fact_existing", content="Database is PostgreSQL")

        actions = [
            ConsolidationAction(
                action=ConsolidationActionType.KEEP,
                content="Database is PostgreSQL",
                fact_type=MarkerType.DECISION.value,
                confidence=0.9,
                source_fact_id="fact_existing",
            ),
            ConsolidationAction(
                action=ConsolidationActionType.ADD,
                content="Frontend uses React with TypeScript",
                fact_type=MarkerType.DECISION.value,
                confidence=0.9,
            ),
        ]
        reflector = FakeConsolidatingReflector(actions_to_return=actions)

        storage = InMemoryBackend()
        await storage.initialize()

        embedder = DeterministicEmbedder(dimension=4)
        config = GleanrConfig(reflection=ReflectionConfig(dedup_similarity_threshold=0.95))

        runner = ReflectionRunner(
            session_id="test_session",
            storage=storage,
            reflector=reflector,
            embedder=embedder,
            token_counter=HeuristicTokenCounter(),
            config=config,
        )

        emb = (await embedder.embed([prior_fact.content]))[0]
        await storage.save_embedding(id="emb_existing", embedding=emb, metadata={})
        prior_fact.embedding_id = "emb_existing"
        await storage.save_fact(prior_fact)

        episode = _make_episode(episode_id="ep_2")
        turns = _make_turns(episode_id="ep_2", count=3)
        result = await runner.reflect_episode(episode, turns)

        # Non-duplicate ADD should be saved
        assert len(result) == 1
        assert result[0].content == "Frontend uses React with TypeScript"

    @pytest.mark.asyncio
    async def test_dedup_disabled_when_threshold_is_one(self) -> None:
        """Dedup is disabled when threshold is 1.0."""
        prior_fact = _make_fact(fact_id="fact_existing", content="Database is PostgreSQL")

        actions = [
            ConsolidationAction(
                action=ConsolidationActionType.KEEP,
                content="Database is PostgreSQL",
                fact_type=MarkerType.DECISION.value,
                confidence=0.9,
                source_fact_id="fact_existing",
            ),
            ConsolidationAction(
                action=ConsolidationActionType.ADD,
                content="Database is PostgreSQL",  # Exact duplicate
                fact_type=MarkerType.DECISION.value,
                confidence=0.9,
            ),
        ]
        reflector = FakeConsolidatingReflector(actions_to_return=actions)

        storage = InMemoryBackend()
        await storage.initialize()

        embedder = DeterministicEmbedder(dimension=4)
        # Threshold of 1.0 disables dedup
        config = GleanrConfig(reflection=ReflectionConfig(dedup_similarity_threshold=1.0))

        runner = ReflectionRunner(
            session_id="test_session",
            storage=storage,
            reflector=reflector,
            embedder=embedder,
            token_counter=HeuristicTokenCounter(),
            config=config,
        )

        emb = (await embedder.embed([prior_fact.content]))[0]
        await storage.save_embedding(id="emb_existing", embedding=emb, metadata={})
        prior_fact.embedding_id = "emb_existing"
        await storage.save_fact(prior_fact)

        episode = _make_episode(episode_id="ep_2")
        turns = _make_turns(episode_id="ep_2", count=3)
        result = await runner.reflect_episode(episode, turns)

        # Even exact duplicate should be saved when dedup is disabled
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_dedup_with_null_embedder_does_not_block(self) -> None:
        """Dedup gracefully handles NullEmbedder (zero vectors)."""
        prior_fact = _make_fact(fact_id="fact_existing", content="Database is PostgreSQL")

        actions = [
            ConsolidationAction(
                action=ConsolidationActionType.KEEP,
                content="Database is PostgreSQL",
                fact_type=MarkerType.DECISION.value,
                confidence=0.9,
                source_fact_id="fact_existing",
            ),
            ConsolidationAction(
                action=ConsolidationActionType.ADD,
                content="Database is PostgreSQL",
                fact_type=MarkerType.DECISION.value,
                confidence=0.9,
            ),
        ]
        reflector = FakeConsolidatingReflector(actions_to_return=actions)
        config = GleanrConfig(reflection=ReflectionConfig(dedup_similarity_threshold=0.95))
        runner, storage = await _build_runner(reflector, config=config)

        # NullEmbedder produces zero vectors — dedup should not block
        await storage.save_fact(prior_fact)

        episode = _make_episode(episode_id="ep_2")
        turns = _make_turns(episode_id="ep_2", count=3)
        result = await runner.reflect_episode(episode, turns)

        # Should still save even though content is identical (zero vectors = no dedup)
        assert len(result) == 1
