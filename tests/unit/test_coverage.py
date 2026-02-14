"""Unit tests for coverage validation module."""

from __future__ import annotations

from datetime import datetime

from acms.memory.coverage import extract_keywords, validate_coverage
from acms.models import Fact, MarkerType
from acms.models.consolidation import ConsolidationAction, ConsolidationActionType


def _make_fact(
    fact_id: str = "fact_1",
    content: str = "User prefers Python for backend development",
) -> Fact:
    return Fact(
        id=fact_id,
        session_id="s1",
        episode_id="ep_1",
        content=content,
        created_at=datetime.utcnow(),
        fact_type=MarkerType.DECISION.value,
        confidence=0.9,
    )


def _make_action(
    action: ConsolidationActionType = ConsolidationActionType.KEEP,
    content: str = "",
    source_fact_id: str | None = None,
) -> ConsolidationAction:
    return ConsolidationAction(
        action=action,
        content=content,
        source_fact_id=source_fact_id,
    )


class TestExtractKeywords:
    """Tests for extract_keywords."""

    def test_basic_extraction(self) -> None:
        keywords = extract_keywords("User prefers Python for backend")
        assert "python" in keywords
        assert "prefers" in keywords
        assert "backend" in keywords

    def test_stop_words_excluded(self) -> None:
        keywords = extract_keywords("the user and their preferences")
        assert "the" not in keywords
        assert "and" not in keywords
        assert "their" not in keywords

    def test_short_words_excluded(self) -> None:
        keywords = extract_keywords("I am OK")
        # "am" and "OK" are < 3 chars
        assert "am" not in keywords

    def test_empty_input(self) -> None:
        keywords = extract_keywords("")
        assert keywords == set()

    def test_punctuation_stripped(self) -> None:
        keywords = extract_keywords("Python, JavaScript, and TypeScript.")
        assert "python" in keywords
        assert "javascript" in keywords
        assert "typescript" in keywords

    def test_case_insensitive(self) -> None:
        keywords = extract_keywords("PostgreSQL MySQL")
        assert "postgresql" in keywords
        assert "mysql" in keywords


class TestValidateCoverage:
    """Tests for validate_coverage."""

    def test_all_facts_referenced_by_id(self) -> None:
        facts = [_make_fact("fact_1"), _make_fact("fact_2", "Another fact")]
        actions = [
            _make_action(ConsolidationActionType.KEEP, source_fact_id="fact_1"),
            _make_action(ConsolidationActionType.UPDATE, content="updated", source_fact_id="fact_2"),
        ]
        warnings = validate_coverage(facts, actions)
        assert warnings == []

    def test_keyword_overlap_covers_fact(self) -> None:
        facts = [_make_fact("fact_1", "User prefers Python for backend development")]
        actions = [
            # No source_fact_id, but keywords overlap
            _make_action(
                ConsolidationActionType.ADD,
                content="User prefers Python for backend projects",
            ),
        ]
        warnings = validate_coverage(facts, actions)
        assert warnings == []

    def test_uncovered_fact_generates_warning(self) -> None:
        facts = [_make_fact("fact_1", "User prefers Python for backend development")]
        actions = [
            _make_action(
                ConsolidationActionType.ADD,
                content="Database uses MongoDB",
            ),
        ]
        warnings = validate_coverage(facts, actions)
        assert len(warnings) == 1
        assert "fact_1" in warnings[0]

    def test_empty_prior_facts(self) -> None:
        actions = [_make_action(ConsolidationActionType.ADD, content="new fact")]
        warnings = validate_coverage([], actions)
        assert warnings == []

    def test_empty_actions_warns_for_all_facts(self) -> None:
        facts = [
            _make_fact("fact_1", "User prefers Python for backend development"),
            _make_fact("fact_2", "Database uses PostgreSQL for persistence"),
        ]
        warnings = validate_coverage(facts, [])
        assert len(warnings) == 2

    def test_partial_id_coverage(self) -> None:
        facts = [
            _make_fact("fact_1", "First fact content"),
            _make_fact("fact_2", "Second totally different fact content"),
        ]
        actions = [
            _make_action(ConsolidationActionType.KEEP, source_fact_id="fact_1"),
            # fact_2 not referenced and keywords don't match
            _make_action(ConsolidationActionType.ADD, content="unrelated new stuff"),
        ]
        warnings = validate_coverage(facts, actions)
        assert len(warnings) == 1
        assert "fact_2" in warnings[0]
