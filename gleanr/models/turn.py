"""Turn model - L0 memory level (raw turns)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from gleanr.models.types import Role


@dataclass(slots=True)
class Turn:
    """A single turn in a conversation.

    L0 memory - verbatim messages with short TTL and aggressive eviction.
    """

    id: str
    session_id: str
    episode_id: str
    role: Role
    content: str
    created_at: datetime

    # Actor identification
    actor_id: str | None = None

    # Importance markers
    markers: list[str] = field(default_factory=list)

    # Arbitrary metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Token count (computed during ingestion)
    token_count: int = 0

    # Embedding (stored separately but referenced here)
    embedding_id: str | None = None

    # Position within episode (0-indexed)
    position: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "episode_id": self.episode_id,
            "role": self.role.value,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "actor_id": self.actor_id,
            "markers": self.markers,
            "metadata": self.metadata,
            "token_count": self.token_count,
            "embedding_id": self.embedding_id,
            "position": self.position,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Turn:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            episode_id=data["episode_id"],
            role=Role(data["role"]),
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]),
            actor_id=data.get("actor_id"),
            markers=data.get("markers", []),
            metadata=data.get("metadata", {}),
            token_count=data.get("token_count", 0),
            embedding_id=data.get("embedding_id"),
            position=data.get("position", 0),
        )
