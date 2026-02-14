"""Unit tests for consolidation action models."""

from __future__ import annotations

import pytest

from acms.models.consolidation import ConsolidationAction, ConsolidationActionType


class TestConsolidationActionType:
    """Tests for ConsolidationActionType enum."""

    def test_enum_values(self) -> None:
        assert ConsolidationActionType.KEEP.value == "keep"
        assert ConsolidationActionType.UPDATE.value == "update"
        assert ConsolidationActionType.ADD.value == "add"
        assert ConsolidationActionType.REMOVE.value == "remove"

    def test_from_string(self) -> None:
        assert ConsolidationActionType("keep") == ConsolidationActionType.KEEP
        assert ConsolidationActionType("update") == ConsolidationActionType.UPDATE
        assert ConsolidationActionType("add") == ConsolidationActionType.ADD
        assert ConsolidationActionType("remove") == ConsolidationActionType.REMOVE

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            ConsolidationActionType("invalid")

    def test_is_string_subclass(self) -> None:
        """ConsolidationActionType is a str enum for JSON compatibility."""
        assert isinstance(ConsolidationActionType.KEEP, str)


class TestConsolidationAction:
    """Tests for ConsolidationAction dataclass."""

    def test_creation_defaults(self) -> None:
        action = ConsolidationAction(
            action=ConsolidationActionType.ADD,
            content="New fact content",
        )
        assert action.action == ConsolidationActionType.ADD
        assert action.content == "New fact content"
        assert action.fact_type == "decision"
        assert action.confidence == 0.9
        assert action.source_fact_id is None
        assert action.reason == ""

    def test_creation_with_all_fields(self) -> None:
        action = ConsolidationAction(
            action=ConsolidationActionType.UPDATE,
            content="Updated fact",
            fact_type="constraint",
            confidence=0.95,
            source_fact_id="fact_abc123",
            reason="database changed",
        )
        assert action.fact_type == "constraint"
        assert action.confidence == 0.95
        assert action.source_fact_id == "fact_abc123"
        assert action.reason == "database changed"

    def test_frozen_immutability(self) -> None:
        action = ConsolidationAction(
            action=ConsolidationActionType.KEEP,
            content="unchanged",
        )
        with pytest.raises(AttributeError):
            action.content = "changed"  # type: ignore[misc]

    def test_keep_action(self) -> None:
        action = ConsolidationAction(
            action=ConsolidationActionType.KEEP,
            content="fact stays the same",
            source_fact_id="fact_123",
        )
        assert action.action == ConsolidationActionType.KEEP
        assert action.source_fact_id == "fact_123"

    def test_remove_action_with_reason(self) -> None:
        action = ConsolidationAction(
            action=ConsolidationActionType.REMOVE,
            content="contradicted fact",
            source_fact_id="fact_456",
            reason="user changed their mind",
        )
        assert action.action == ConsolidationActionType.REMOVE
        assert action.reason == "user changed their mind"
