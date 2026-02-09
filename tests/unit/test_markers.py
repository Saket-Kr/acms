"""Unit tests for marker detection and scoring."""

import pytest

from acms.models import MarkerType
from acms.utils import (
    calculate_marker_boost,
    detect_markers,
    get_marker_type,
    is_custom_marker,
    merge_markers,
)


class TestDetectMarkers:
    """Tests for detect_markers."""

    def test_detect_decision(self) -> None:
        """Test detecting decision markers."""
        content = "Decision: We will use PostgreSQL for the database."
        markers = detect_markers(content)
        assert MarkerType.DECISION.value in markers

    def test_detect_constraint(self) -> None:
        """Test detecting constraint markers."""
        content = "Constraint: The budget is $10,000."
        markers = detect_markers(content)
        assert MarkerType.CONSTRAINT.value in markers

    def test_detect_failure(self) -> None:
        """Test detecting failure markers."""
        content = "Failed: The API call returned an error."
        markers = detect_markers(content)
        assert MarkerType.FAILURE.value in markers

    def test_detect_goal(self) -> None:
        """Test detecting goal markers."""
        content = "Goal: Build a user authentication system."
        markers = detect_markers(content)
        assert MarkerType.GOAL.value in markers

    def test_case_insensitive(self) -> None:
        """Test case-insensitive detection."""
        content = "DECISION: Use Python."
        markers = detect_markers(content)
        assert MarkerType.DECISION.value in markers

    def test_no_markers(self) -> None:
        """Test content without markers."""
        content = "Hello, how can I help you today?"
        markers = detect_markers(content)
        assert markers == []

    def test_multiple_markers(self) -> None:
        """Test detecting multiple markers."""
        content = """Decision: Use Python.
        Goal: Build an API."""
        markers = detect_markers(content)
        assert MarkerType.DECISION.value in markers
        assert MarkerType.GOAL.value in markers


class TestMergeMarkers:
    """Tests for merge_markers."""

    def test_explicit_only(self) -> None:
        """Test with only explicit markers."""
        markers = merge_markers(["decision", "goal"], [])
        assert markers == ["decision", "goal"]

    def test_detected_only(self) -> None:
        """Test with only detected markers."""
        markers = merge_markers(None, ["decision", "goal"])
        assert markers == ["decision", "goal"]

    def test_explicit_overrides(self) -> None:
        """Test that explicit markers override detected."""
        markers = merge_markers(["constraint"], ["decision", "goal"])
        # Only explicit should be used
        assert markers == ["constraint"]

    def test_empty_both(self) -> None:
        """Test with both empty."""
        markers = merge_markers(None, [])
        assert markers == []

    def test_deduplication(self) -> None:
        """Test that duplicates are removed."""
        markers = merge_markers(["decision", "decision", "goal"], [])
        assert markers == ["decision", "goal"]


class TestCalculateMarkerBoost:
    """Tests for calculate_marker_boost."""

    def test_no_markers(self) -> None:
        """Test with no markers."""
        boost = calculate_marker_boost([])
        assert boost == 0.0

    def test_single_marker(self) -> None:
        """Test with single marker."""
        boost = calculate_marker_boost(["decision"])
        assert boost == 0.3  # Default weight for decision

    def test_constraint_highest(self) -> None:
        """Test that constraint has highest weight."""
        constraint_boost = calculate_marker_boost(["constraint"])
        decision_boost = calculate_marker_boost(["decision"])
        assert constraint_boost > decision_boost

    def test_multiple_markers(self) -> None:
        """Test with multiple markers."""
        boost = calculate_marker_boost(["decision", "constraint"])
        assert boost == 0.3 + 0.4  # decision + constraint

    def test_custom_marker(self) -> None:
        """Test with custom marker."""
        boost = calculate_marker_boost(["custom:important"])
        assert boost == 0.2  # Default custom weight

    def test_custom_weights(self) -> None:
        """Test with custom weights."""
        weights = {"decision": 0.5, "goal": 0.1}
        boost = calculate_marker_boost(["decision", "goal"], weights)
        assert boost == 0.6


class TestIsCustomMarker:
    """Tests for is_custom_marker."""

    def test_custom_marker(self) -> None:
        """Test with custom marker."""
        assert is_custom_marker("custom:important") is True

    def test_builtin_marker(self) -> None:
        """Test with builtin marker."""
        assert is_custom_marker("decision") is False

    def test_custom_prefix_only(self) -> None:
        """Test with custom: prefix but no name."""
        # This is technically a custom marker format
        assert is_custom_marker("custom:") is True


class TestGetMarkerType:
    """Tests for get_marker_type."""

    def test_valid_marker(self) -> None:
        """Test with valid marker."""
        assert get_marker_type("decision") == MarkerType.DECISION
        assert get_marker_type("constraint") == MarkerType.CONSTRAINT

    def test_custom_marker(self) -> None:
        """Test with custom marker."""
        assert get_marker_type("custom:important") is None

    def test_invalid_marker(self) -> None:
        """Test with invalid marker."""
        assert get_marker_type("invalid") is None
