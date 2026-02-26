"""Episode model - L1 memory level (grouped turns)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from gleanr.models.types import EpisodeStatus


@dataclass(slots=True)
class Episode:
    """A group of related turns forming a coherent interaction unit.

    L1 memory - mandatory grouping of turns around goals/tasks.
    Episodes are session-bound and provide logical segmentation.
    """

    id: str
    session_id: str
    status: EpisodeStatus
    created_at: datetime

    # Episode boundaries
    closed_at: datetime | None = None
    close_reason: str | None = None

    # Summary/metadata
    summary: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # Statistics
    turn_count: int = 0
    total_tokens: int = 0

    # Markers aggregated from turns
    markers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "close_reason": self.close_reason,
            "summary": self.summary,
            "metadata": self.metadata,
            "turn_count": self.turn_count,
            "total_tokens": self.total_tokens,
            "markers": self.markers,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Episode:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            status=EpisodeStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            closed_at=(
                datetime.fromisoformat(data["closed_at"]) if data.get("closed_at") else None
            ),
            close_reason=data.get("close_reason"),
            summary=data.get("summary"),
            metadata=data.get("metadata", {}),
            turn_count=data.get("turn_count", 0),
            total_tokens=data.get("total_tokens", 0),
            markers=data.get("markers", []),
        )
