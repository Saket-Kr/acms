"""Unit tests for shared parsing utilities."""

from __future__ import annotations

from datetime import datetime

from acms.models import Episode, EpisodeStatus, Fact, Role, Turn
from acms.models.consolidation import ConsolidationActionType
from acms.providers.parsing import (
    format_prior_facts,
    format_turns,
    parse_consolidation_actions,
    parse_reflection_facts,
)
from acms.utils import generate_episode_id


def _make_episode() -> Episode:
    return Episode(
        id=generate_episode_id(),
        session_id="s1",
        status=EpisodeStatus.CLOSED,
        created_at=datetime.utcnow(),
    )


class TestParseReflectionFacts:
    """Tests for parse_reflection_facts."""

    def test_valid_json(self) -> None:
        content = '{"facts": [{"content": "User likes Python", "type": "decision", "confidence": 0.9}]}'
        facts = parse_reflection_facts(content, _make_episode())
        assert len(facts) == 1
        assert facts[0].content == "User likes Python"
        assert facts[0].fact_type == "decision"
        assert facts[0].confidence == 0.9

    def test_multiple_facts(self) -> None:
        content = '{"facts": [{"content": "Fact 1"}, {"content": "Fact 2"}]}'
        facts = parse_reflection_facts(content, _make_episode())
        assert len(facts) == 2

    def test_invalid_json_returns_empty(self) -> None:
        facts = parse_reflection_facts("not json at all", _make_episode())
        assert facts == []

    def test_json_with_extra_text(self) -> None:
        content = 'Here are the facts:\n{"facts": [{"content": "Fact 1"}]}\nDone.'
        facts = parse_reflection_facts(content, _make_episode())
        assert len(facts) == 1

    def test_empty_facts_array(self) -> None:
        facts = parse_reflection_facts('{"facts": []}', _make_episode())
        assert facts == []

    def test_unknown_fact_type_normalized(self) -> None:
        content = '{"facts": [{"content": "test", "type": "unknown_type"}]}'
        facts = parse_reflection_facts(content, _make_episode())
        assert facts[0].fact_type == "decision"

    def test_missing_confidence_defaults(self) -> None:
        content = '{"facts": [{"content": "test"}]}'
        facts = parse_reflection_facts(content, _make_episode())
        assert facts[0].confidence == 0.8


class TestParseConsolidationActions:
    """Tests for parse_consolidation_actions."""

    def test_valid_actions(self) -> None:
        content = '{"actions": [{"action": "keep", "content": "fact", "source_fact_id": "f1"}]}'
        actions = parse_consolidation_actions(content)
        assert len(actions) == 1
        assert actions[0].action == ConsolidationActionType.KEEP
        assert actions[0].source_fact_id == "f1"

    def test_all_action_types(self) -> None:
        content = '{"actions": [{"action": "keep", "content": "a"}, {"action": "update", "content": "b", "source_fact_id": "f1", "reason": "changed"}, {"action": "add", "content": "c"}, {"action": "remove", "content": "d", "source_fact_id": "f2", "reason": "gone"}]}'
        actions = parse_consolidation_actions(content)
        assert len(actions) == 4
        types = [a.action for a in actions]
        assert ConsolidationActionType.KEEP in types
        assert ConsolidationActionType.UPDATE in types
        assert ConsolidationActionType.ADD in types
        assert ConsolidationActionType.REMOVE in types

    def test_invalid_json_returns_empty(self) -> None:
        actions = parse_consolidation_actions("garbage")
        assert actions == []

    def test_unknown_action_type_skipped(self) -> None:
        content = '{"actions": [{"action": "unknown", "content": "test"}, {"action": "keep", "content": "valid"}]}'
        actions = parse_consolidation_actions(content)
        assert len(actions) == 1
        assert actions[0].action == ConsolidationActionType.KEEP

    def test_empty_actions(self) -> None:
        actions = parse_consolidation_actions('{"actions": []}')
        assert actions == []

    def test_json_wrapped_in_markdown(self) -> None:
        content = '```json\n{"actions": [{"action": "add", "content": "new"}]}\n```'
        # The extract_json should find the { } even in markdown
        actions = parse_consolidation_actions(content)
        assert len(actions) == 1


class TestFormatPriorFacts:
    """Tests for format_prior_facts."""

    def test_formats_facts(self) -> None:
        facts = [
            Fact(
                id="fact_1",
                session_id="s1",
                episode_id="ep_1",
                content="User prefers Python",
                created_at=datetime.utcnow(),
                fact_type="decision",
            ),
        ]
        result = format_prior_facts(facts)
        assert "fact_1" in result
        assert "decision" in result
        assert "User prefers Python" in result

    def test_empty_facts(self) -> None:
        assert format_prior_facts([]) == ""


class TestFormatTurns:
    """Tests for format_turns."""

    def test_formats_turns(self) -> None:
        turns = [
            Turn(
                id="t1",
                session_id="s1",
                episode_id="ep_1",
                role=Role.USER,
                content="Hello",
                created_at=datetime.utcnow(),
            ),
            Turn(
                id="t2",
                session_id="s1",
                episode_id="ep_1",
                role=Role.ASSISTANT,
                content="Hi there",
                created_at=datetime.utcnow(),
            ),
        ]
        result = format_turns(turns)
        assert "[user]: Hello" in result
        assert "[assistant]: Hi there" in result
