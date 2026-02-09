"""Unit tests for validation utilities."""

import pytest

from acms.errors import ValidationError
from acms.models import MarkerType, Role
from acms.utils import (
    validate_content,
    validate_markers,
    validate_metadata,
    validate_relevance_threshold,
    validate_role,
    validate_session_id,
    validate_token_budget,
)


class TestValidateRole:
    """Tests for validate_role."""

    def test_valid_role_enum(self) -> None:
        """Test with Role enum."""
        assert validate_role(Role.USER) == Role.USER
        assert validate_role(Role.ASSISTANT) == Role.ASSISTANT

    def test_valid_role_string(self) -> None:
        """Test with valid string."""
        assert validate_role("user") == Role.USER
        assert validate_role("USER") == Role.USER
        assert validate_role("assistant") == Role.ASSISTANT

    def test_invalid_role(self) -> None:
        """Test with invalid role."""
        with pytest.raises(ValidationError) as exc:
            validate_role("invalid")
        assert exc.value.field == "role"


class TestValidateContent:
    """Tests for validate_content."""

    def test_valid_content(self) -> None:
        """Test with valid content."""
        assert validate_content("Hello") == "Hello"
        assert validate_content("  Hello  ") == "Hello"

    def test_empty_content(self) -> None:
        """Test with empty content."""
        with pytest.raises(ValidationError) as exc:
            validate_content("")
        assert exc.value.field == "content"

    def test_whitespace_only(self) -> None:
        """Test with whitespace only."""
        with pytest.raises(ValidationError) as exc:
            validate_content("   ")
        assert exc.value.field == "content"

    def test_non_string_content(self) -> None:
        """Test with non-string content."""
        with pytest.raises(ValidationError) as exc:
            validate_content(123)  # type: ignore
        assert exc.value.field == "content"


class TestValidateMarkers:
    """Tests for validate_markers."""

    def test_none_markers(self) -> None:
        """Test with None."""
        assert validate_markers(None) == []

    def test_empty_markers(self) -> None:
        """Test with empty list."""
        assert validate_markers([]) == []

    def test_valid_marker_type_values(self) -> None:
        """Test with MarkerType values."""
        markers = validate_markers(["decision", "constraint"])
        assert markers == ["decision", "constraint"]

    def test_valid_marker_type_enums(self) -> None:
        """Test with MarkerType enums."""
        markers = validate_markers([MarkerType.DECISION, MarkerType.GOAL])
        assert markers == ["decision", "goal"]

    def test_custom_markers(self) -> None:
        """Test with custom markers."""
        markers = validate_markers(["custom:important", "custom:urgent"])
        assert markers == ["custom:important", "custom:urgent"]

    def test_invalid_custom_marker(self) -> None:
        """Test with invalid custom marker (empty name)."""
        with pytest.raises(ValidationError) as exc:
            validate_markers(["custom:"])
        assert exc.value.field == "markers"

    def test_invalid_marker_value(self) -> None:
        """Test with invalid marker value."""
        with pytest.raises(ValidationError) as exc:
            validate_markers(["invalid_marker"])
        assert exc.value.field == "markers"

    def test_non_list_markers(self) -> None:
        """Test with non-list markers."""
        with pytest.raises(ValidationError) as exc:
            validate_markers("decision")  # type: ignore
        assert exc.value.field == "markers"


class TestValidateTokenBudget:
    """Tests for validate_token_budget."""

    def test_valid_budget(self) -> None:
        """Test with valid budget."""
        assert validate_token_budget(1000) == 1000
        assert validate_token_budget(1) == 1

    def test_zero_budget(self) -> None:
        """Test with zero budget."""
        with pytest.raises(ValidationError) as exc:
            validate_token_budget(0)
        assert exc.value.field == "token_budget"

    def test_negative_budget(self) -> None:
        """Test with negative budget."""
        with pytest.raises(ValidationError) as exc:
            validate_token_budget(-100)
        assert exc.value.field == "token_budget"

    def test_non_integer_budget(self) -> None:
        """Test with non-integer budget."""
        with pytest.raises(ValidationError) as exc:
            validate_token_budget(100.5)  # type: ignore
        assert exc.value.field == "token_budget"


class TestValidateSessionId:
    """Tests for validate_session_id."""

    def test_valid_session_id(self) -> None:
        """Test with valid session ID."""
        assert validate_session_id("session_123") == "session_123"
        assert validate_session_id("test-session") == "test-session"
        assert validate_session_id("ABC123") == "ABC123"

    def test_session_id_with_whitespace(self) -> None:
        """Test trimming whitespace."""
        assert validate_session_id("  session_123  ") == "session_123"

    def test_empty_session_id(self) -> None:
        """Test with empty session ID."""
        with pytest.raises(ValidationError) as exc:
            validate_session_id("")
        assert exc.value.field == "session_id"

    def test_invalid_characters(self) -> None:
        """Test with invalid characters."""
        with pytest.raises(ValidationError) as exc:
            validate_session_id("session/123")
        assert exc.value.field == "session_id"

    def test_non_string_session_id(self) -> None:
        """Test with non-string session ID."""
        with pytest.raises(ValidationError) as exc:
            validate_session_id(123)  # type: ignore
        assert exc.value.field == "session_id"


class TestValidateMetadata:
    """Tests for validate_metadata."""

    def test_none_metadata(self) -> None:
        """Test with None."""
        assert validate_metadata(None) == {}

    def test_valid_metadata(self) -> None:
        """Test with valid metadata."""
        metadata = {"key": "value", "count": 42}
        assert validate_metadata(metadata) == metadata

    def test_non_dict_metadata(self) -> None:
        """Test with non-dict metadata."""
        with pytest.raises(ValidationError) as exc:
            validate_metadata(["key", "value"])  # type: ignore
        assert exc.value.field == "metadata"

    def test_non_string_key(self) -> None:
        """Test with non-string key."""
        with pytest.raises(ValidationError) as exc:
            validate_metadata({123: "value"})  # type: ignore
        assert exc.value.field == "metadata"


class TestValidateRelevanceThreshold:
    """Tests for validate_relevance_threshold."""

    def test_valid_threshold(self) -> None:
        """Test with valid threshold."""
        assert validate_relevance_threshold(0.5) == 0.5
        assert validate_relevance_threshold(0.0) == 0.0
        assert validate_relevance_threshold(1.0) == 1.0

    def test_integer_threshold(self) -> None:
        """Test with integer threshold."""
        assert validate_relevance_threshold(0) == 0.0
        assert validate_relevance_threshold(1) == 1.0

    def test_threshold_too_low(self) -> None:
        """Test with threshold below 0."""
        with pytest.raises(ValidationError) as exc:
            validate_relevance_threshold(-0.1)
        assert exc.value.field == "min_relevance"

    def test_threshold_too_high(self) -> None:
        """Test with threshold above 1."""
        with pytest.raises(ValidationError) as exc:
            validate_relevance_threshold(1.1)
        assert exc.value.field == "min_relevance"
