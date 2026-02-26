"""Marker detection utilities."""

from __future__ import annotations

import re
from typing import Sequence

from gleanr.models.types import (
    DEFAULT_CUSTOM_MARKER_WEIGHT,
    DEFAULT_MARKER_WEIGHTS,
    MarkerType,
)

# Auto-detection patterns for markers
# Pattern must appear at start of content or after newline
MARKER_PATTERNS: dict[str, list[str]] = {
    MarkerType.DECISION.value: [
        r"(?i)(?:^|\n)\s*(?:decision|decided|choosing|selected|chose|picked|going with):",
    ],
    MarkerType.CONSTRAINT.value: [
        r"(?i)(?:^|\n)\s*(?:constraint|requirement|must|cannot|can't|won't|budget|limit|restriction):",
    ],
    MarkerType.FAILURE.value: [
        r"(?i)(?:^|\n)\s*(?:failed|error|didn't work|didn't succeed|tried but|couldn't|could not):",
    ],
    MarkerType.GOAL.value: [
        r"(?i)(?:^|\n)\s*(?:goal|objective|task|need to|want to|trying to|aim):",
    ],
}


def detect_markers(content: str) -> list[str]:
    """Auto-detect markers from content patterns.

    Args:
        content: Turn content to analyze

    Returns:
        List of detected marker values
    """
    detected: list[str] = []

    for marker_type, patterns in MARKER_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content):
                if marker_type not in detected:
                    detected.append(marker_type)
                break

    return detected


def merge_markers(
    explicit: Sequence[str] | None,
    detected: Sequence[str],
) -> list[str]:
    """Merge explicit markers with auto-detected ones.

    Explicit markers take precedence - if explicit markers are provided,
    detected markers are not added (to avoid duplicate detection).

    Args:
        explicit: Explicitly provided markers
        detected: Auto-detected markers

    Returns:
        Merged list of unique markers
    """
    if explicit:
        # If explicit markers provided, use them as-is
        return list(dict.fromkeys(explicit))

    # No explicit markers, use detected ones
    return list(dict.fromkeys(detected))


def calculate_marker_boost(
    markers: Sequence[str],
    weights: dict[str, float] | None = None,
) -> float:
    """Calculate total marker boost for scoring.

    Args:
        markers: List of marker values
        weights: Custom marker weights (uses defaults if None)

    Returns:
        Total boost value
    """
    if not markers:
        return 0.0

    if weights is None:
        weights = DEFAULT_MARKER_WEIGHTS

    total = 0.0
    for marker in markers:
        if marker in weights:
            total += weights[marker]
        elif marker.startswith("custom:"):
            total += DEFAULT_CUSTOM_MARKER_WEIGHT
        else:
            # Unknown marker, use custom weight
            total += DEFAULT_CUSTOM_MARKER_WEIGHT

    return total


def is_custom_marker(marker: str) -> bool:
    """Check if a marker is a custom marker.

    Args:
        marker: Marker value

    Returns:
        True if custom marker
    """
    return marker.startswith("custom:")


def get_marker_type(marker: str) -> MarkerType | None:
    """Get MarkerType enum for a marker string.

    Args:
        marker: Marker value

    Returns:
        MarkerType enum or None if custom/unknown
    """
    try:
        return MarkerType(marker)
    except ValueError:
        return None
