"""Consolidation action models for fact merging across episodes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConsolidationActionType(str, Enum):
    """Type of action to take on a fact during consolidation."""

    KEEP = "keep"
    UPDATE = "update"
    ADD = "add"
    REMOVE = "remove"


@dataclass(frozen=True, slots=True)
class ConsolidationAction:
    """A single consolidation action returned by a consolidating reflector.

    Each action describes what to do with an existing fact (keep/update/remove)
    or introduces a new fact (add).

    Attributes:
        action: The type of consolidation action.
        content: The fact content (original for keep/remove, revised for update, new for add).
        fact_type: Marker type for the fact (e.g. "decision", "constraint").
        confidence: Confidence score from the reflector (0-1).
        source_fact_id: ID of the prior fact this action references (None for add).
        reason: Explanation for update/remove actions (empty for keep/add).
    """

    action: ConsolidationActionType
    content: str
    fact_type: str = "decision"
    confidence: float = 0.9
    source_fact_id: str | None = None
    reason: str = ""
