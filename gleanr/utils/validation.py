"""Input validation utilities."""

from __future__ import annotations

import re
from typing import Any

from gleanr.errors import ValidationError
from gleanr.models.types import MarkerType, Role


def validate_role(role: str | Role) -> Role:
    """Validate and convert role input to Role enum.

    Args:
        role: Role as string or enum

    Returns:
        Validated Role enum

    Raises:
        ValidationError: If role is invalid
    """
    if isinstance(role, Role):
        return role

    try:
        return Role(role.lower())
    except ValueError:
        valid_roles = [r.value for r in Role]
        raise ValidationError(
            f"Invalid role: {role}. Must be one of: {valid_roles}",
            field="role",
        )


def validate_content(content: str) -> str:
    """Validate turn content.

    Args:
        content: Content string

    Returns:
        Validated content (stripped)

    Raises:
        ValidationError: If content is invalid
    """
    if not isinstance(content, str):
        raise ValidationError(
            f"Content must be a string, got {type(content).__name__}",
            field="content",
        )

    content = content.strip()
    if not content:
        raise ValidationError(
            "Content cannot be empty",
            field="content",
        )

    return content


def validate_markers(markers: list[str] | None) -> list[str]:
    """Validate markers list.

    Args:
        markers: List of marker strings

    Returns:
        Validated markers list

    Raises:
        ValidationError: If markers are invalid
    """
    if markers is None:
        return []

    if not isinstance(markers, list):
        raise ValidationError(
            f"Markers must be a list, got {type(markers).__name__}",
            field="markers",
        )

    validated = []
    for marker in markers:
        if isinstance(marker, MarkerType):
            validated.append(marker.value)
        elif isinstance(marker, str):
            # Allow MarkerType values and custom:* markers
            if marker in [m.value for m in MarkerType]:
                validated.append(marker)
            elif marker.startswith("custom:"):
                if len(marker) <= 7:  # "custom:" with nothing after
                    raise ValidationError(
                        f"Custom marker must have a name after 'custom:': {marker}",
                        field="markers",
                    )
                validated.append(marker)
            else:
                raise ValidationError(
                    f"Invalid marker: {marker}. Must be a MarkerType value or 'custom:*'",
                    field="markers",
                )
        else:
            raise ValidationError(
                f"Marker must be a string, got {type(marker).__name__}",
                field="markers",
            )

    return validated


def validate_token_budget(budget: int) -> int:
    """Validate token budget.

    Args:
        budget: Token budget

    Returns:
        Validated budget

    Raises:
        ValidationError: If budget is invalid
    """
    if not isinstance(budget, int):
        raise ValidationError(
            f"Token budget must be an integer, got {type(budget).__name__}",
            field="token_budget",
        )

    if budget <= 0:
        raise ValidationError(
            f"Token budget must be positive, got {budget}",
            field="token_budget",
        )

    return budget


def validate_session_id(session_id: str) -> str:
    """Validate session ID.

    Args:
        session_id: Session identifier

    Returns:
        Validated session ID

    Raises:
        ValidationError: If session ID is invalid
    """
    if not isinstance(session_id, str):
        raise ValidationError(
            f"Session ID must be a string, got {type(session_id).__name__}",
            field="session_id",
        )

    session_id = session_id.strip()
    if not session_id:
        raise ValidationError(
            "Session ID cannot be empty",
            field="session_id",
        )

    # Allow alphanumeric, hyphens, underscores
    if not re.match(r"^[a-zA-Z0-9_-]+$", session_id):
        raise ValidationError(
            "Session ID must be alphanumeric with hyphens/underscores only",
            field="session_id",
        )

    return session_id


def validate_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    """Validate metadata dictionary.

    Args:
        metadata: Metadata dictionary

    Returns:
        Validated metadata

    Raises:
        ValidationError: If metadata is invalid
    """
    if metadata is None:
        return {}

    if not isinstance(metadata, dict):
        raise ValidationError(
            f"Metadata must be a dictionary, got {type(metadata).__name__}",
            field="metadata",
        )

    # Ensure all keys are strings
    for key in metadata:
        if not isinstance(key, str):
            raise ValidationError(
                f"Metadata keys must be strings, got {type(key).__name__}",
                field="metadata",
            )

    return metadata


def validate_relevance_threshold(threshold: float) -> float:
    """Validate relevance threshold.

    Args:
        threshold: Relevance threshold (0-1)

    Returns:
        Validated threshold

    Raises:
        ValidationError: If threshold is invalid
    """
    if not isinstance(threshold, (int, float)):
        raise ValidationError(
            f"Relevance threshold must be a number, got {type(threshold).__name__}",
            field="min_relevance",
        )

    if threshold < 0.0 or threshold > 1.0:
        raise ValidationError(
            f"Relevance threshold must be between 0 and 1, got {threshold}",
            field="min_relevance",
        )

    return float(threshold)
