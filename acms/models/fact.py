"""Fact model - L2 memory level (semantic facts)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from acms.models.types import MarkerType


@dataclass(slots=True)
class Fact:
    """A semantic fact extracted from episode reflection.

    L2 memory - optional, reflection-generated conclusions.
    Facts represent decisions, constraints, outcomes, etc.
    """

    id: str
    session_id: str
    episode_id: str  # Source episode
    content: str
    created_at: datetime

    # Fact type (maps to marker type or custom)
    fact_type: str = MarkerType.DECISION.value

    # Confidence score from reflection (0-1)
    confidence: float = 1.0

    # Embedding for semantic search
    embedding_id: str | None = None

    # Token count
    token_count: int = 0

    # Arbitrary metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "episode_id": self.episode_id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "fact_type": self.fact_type,
            "confidence": self.confidence,
            "embedding_id": self.embedding_id,
            "token_count": self.token_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Fact:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            episode_id=data["episode_id"],
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]),
            fact_type=data.get("fact_type", MarkerType.DECISION.value),
            confidence=data.get("confidence", 1.0),
            embedding_id=data.get("embedding_id"),
            token_count=data.get("token_count", 0),
            metadata=data.get("metadata", {}),
        )
