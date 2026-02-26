"""ID generation utilities."""

from __future__ import annotations

import uuid
from datetime import datetime


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix.

    Args:
        prefix: Optional prefix (e.g., "turn", "episode", "fact")

    Returns:
        Unique ID string
    """
    uid = uuid.uuid4().hex[:16]
    if prefix:
        return f"{prefix}_{uid}"
    return uid


def generate_turn_id() -> str:
    """Generate a unique turn ID."""
    return generate_id("turn")


def generate_episode_id() -> str:
    """Generate a unique episode ID."""
    return generate_id("ep")


def generate_fact_id() -> str:
    """Generate a unique fact ID."""
    return generate_id("fact")


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return generate_id("sess")


def generate_embedding_id() -> str:
    """Generate a unique embedding ID."""
    return generate_id("emb")


def timestamp_id(prefix: str = "") -> str:
    """Generate a timestamp-based ID for ordering.

    Format: {prefix}_{timestamp}_{random}
    """
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    rand = uuid.uuid4().hex[:8]
    if prefix:
        return f"{prefix}_{ts}_{rand}"
    return f"{ts}_{rand}"
