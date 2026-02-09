"""SQLite storage backend with vector search support."""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from acms.models import Episode, EpisodeStatus, Fact, Turn, VectorSearchResult
from acms.storage.base import StorageBackend

if TYPE_CHECKING:
    import aiosqlite


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(a) != len(b):
        return 0.0

    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class SQLiteBackend(StorageBackend):
    """SQLite storage backend.

    Provides persistent storage with vector search support.
    Uses aiosqlite for async operations.

    Vector search is implemented using in-memory comparison
    (suitable for small-medium workloads). For larger workloads,
    consider sqlite-vec extension.
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS turns (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        episode_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        actor_id TEXT,
        markers TEXT NOT NULL DEFAULT '[]',
        metadata TEXT NOT NULL DEFAULT '{}',
        token_count INTEGER NOT NULL DEFAULT 0,
        embedding_id TEXT,
        position INTEGER NOT NULL DEFAULT 0
    );

    CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id);
    CREATE INDEX IF NOT EXISTS idx_turns_episode ON turns(episode_id);
    CREATE INDEX IF NOT EXISTS idx_turns_created ON turns(created_at);

    CREATE TABLE IF NOT EXISTS episodes (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        closed_at TEXT,
        close_reason TEXT,
        summary TEXT,
        metadata TEXT NOT NULL DEFAULT '{}',
        turn_count INTEGER NOT NULL DEFAULT 0,
        total_tokens INTEGER NOT NULL DEFAULT 0,
        markers TEXT NOT NULL DEFAULT '[]'
    );

    CREATE INDEX IF NOT EXISTS idx_episodes_session ON episodes(session_id);
    CREATE INDEX IF NOT EXISTS idx_episodes_status ON episodes(status);

    CREATE TABLE IF NOT EXISTS facts (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        episode_id TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        fact_type TEXT NOT NULL DEFAULT 'decision',
        confidence REAL NOT NULL DEFAULT 1.0,
        embedding_id TEXT,
        token_count INTEGER NOT NULL DEFAULT 0,
        metadata TEXT NOT NULL DEFAULT '{}'
    );

    CREATE INDEX IF NOT EXISTS idx_facts_session ON facts(session_id);
    CREATE INDEX IF NOT EXISTS idx_facts_episode ON facts(episode_id);

    CREATE TABLE IF NOT EXISTS embeddings (
        id TEXT PRIMARY KEY,
        embedding BLOB NOT NULL,
        metadata TEXT NOT NULL DEFAULT '{}'
    );
    """

    def __init__(
        self,
        path: str | Path = ":memory:",
        *,
        check_same_thread: bool = False,
    ) -> None:
        """Initialize SQLite backend.

        Args:
            path: Path to database file, or ":memory:" for in-memory
            check_same_thread: SQLite thread check setting
        """
        try:
            import aiosqlite
        except ImportError as e:
            raise ImportError(
                "aiosqlite is required for SQLiteBackend. "
                "Install with: pip install acms[sqlite]"
            ) from e

        self._path = str(path)
        self._check_same_thread = check_same_thread
        self._connection: "aiosqlite.Connection | None" = None

    async def initialize(self) -> None:
        """Initialize the database."""
        import aiosqlite

        self._connection = await aiosqlite.connect(
            self._path,
            check_same_thread=self._check_same_thread,
        )
        self._connection.row_factory = aiosqlite.Row

        # Create schema
        await self._connection.executescript(self.SCHEMA)
        await self._connection.commit()

    async def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    def _ensure_connected(self) -> "aiosqlite.Connection":
        """Ensure database is connected."""
        if self._connection is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._connection

    # Turn operations

    async def save_turn(self, turn: Turn) -> None:
        """Save a turn to the database."""
        conn = self._ensure_connected()
        await conn.execute(
            """
            INSERT OR REPLACE INTO turns
            (id, session_id, episode_id, role, content, created_at,
             actor_id, markers, metadata, token_count, embedding_id, position)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                turn.id,
                turn.session_id,
                turn.episode_id,
                turn.role.value,
                turn.content,
                turn.created_at.isoformat(),
                turn.actor_id,
                json.dumps(turn.markers),
                json.dumps(turn.metadata),
                turn.token_count,
                turn.embedding_id,
                turn.position,
            ),
        )
        await conn.commit()

    async def get_turn(self, turn_id: str) -> Turn | None:
        """Get a turn by ID."""
        conn = self._ensure_connected()
        async with conn.execute(
            "SELECT * FROM turns WHERE id = ?", (turn_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return self._row_to_turn(row) if row else None

    async def get_turns_by_episode(self, episode_id: str) -> list[Turn]:
        """Get all turns for an episode."""
        conn = self._ensure_connected()
        async with conn.execute(
            "SELECT * FROM turns WHERE episode_id = ? ORDER BY position",
            (episode_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_turn(row) for row in rows]

    async def get_turns_by_session(
        self,
        session_id: str,
        *,
        limit: int = 1000,
    ) -> list[Turn]:
        """Get all turns for a session."""
        conn = self._ensure_connected()
        async with conn.execute(
            "SELECT * FROM turns WHERE session_id = ? ORDER BY created_at LIMIT ?",
            (session_id, limit),
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_turn(row) for row in rows]

    async def get_marked_turns(
        self,
        session_id: str,
        *,
        exclude_episode_id: str | None = None,
    ) -> list[Turn]:
        """Get all turns with markers."""
        conn = self._ensure_connected()

        if exclude_episode_id:
            async with conn.execute(
                """
                SELECT * FROM turns
                WHERE session_id = ? AND episode_id != ? AND markers != '[]'
                ORDER BY created_at
                """,
                (session_id, exclude_episode_id),
            ) as cursor:
                rows = await cursor.fetchall()
        else:
            async with conn.execute(
                """
                SELECT * FROM turns
                WHERE session_id = ? AND markers != '[]'
                ORDER BY created_at
                """,
                (session_id,),
            ) as cursor:
                rows = await cursor.fetchall()

        return [self._row_to_turn(row) for row in rows]

    def _row_to_turn(self, row: Any) -> Turn:
        """Convert a database row to a Turn."""
        from acms.models import Role

        return Turn(
            id=row["id"],
            session_id=row["session_id"],
            episode_id=row["episode_id"],
            role=Role(row["role"]),
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"]),
            actor_id=row["actor_id"],
            markers=json.loads(row["markers"]),
            metadata=json.loads(row["metadata"]),
            token_count=row["token_count"],
            embedding_id=row["embedding_id"],
            position=row["position"],
        )

    # Episode operations

    async def save_episode(self, episode: Episode) -> None:
        """Save an episode to the database."""
        conn = self._ensure_connected()
        await conn.execute(
            """
            INSERT OR REPLACE INTO episodes
            (id, session_id, status, created_at, closed_at, close_reason,
             summary, metadata, turn_count, total_tokens, markers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                episode.id,
                episode.session_id,
                episode.status.value,
                episode.created_at.isoformat(),
                episode.closed_at.isoformat() if episode.closed_at else None,
                episode.close_reason,
                episode.summary,
                json.dumps(episode.metadata),
                episode.turn_count,
                episode.total_tokens,
                json.dumps(episode.markers),
            ),
        )
        await conn.commit()

    async def get_episode(self, episode_id: str) -> Episode | None:
        """Get an episode by ID."""
        conn = self._ensure_connected()
        async with conn.execute(
            "SELECT * FROM episodes WHERE id = ?", (episode_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return self._row_to_episode(row) if row else None

    async def get_episodes(
        self,
        session_id: str,
        *,
        limit: int = 100,
        status: EpisodeStatus | None = None,
    ) -> list[Episode]:
        """Get episodes for a session."""
        conn = self._ensure_connected()

        if status:
            async with conn.execute(
                """
                SELECT * FROM episodes
                WHERE session_id = ? AND status = ?
                ORDER BY created_at
                LIMIT ?
                """,
                (session_id, status.value, limit),
            ) as cursor:
                rows = await cursor.fetchall()
        else:
            async with conn.execute(
                """
                SELECT * FROM episodes
                WHERE session_id = ?
                ORDER BY created_at
                LIMIT ?
                """,
                (session_id, limit),
            ) as cursor:
                rows = await cursor.fetchall()

        return [self._row_to_episode(row) for row in rows]

    async def update_episode(self, episode: Episode) -> None:
        """Update an existing episode."""
        await self.save_episode(episode)

    def _row_to_episode(self, row: Any) -> Episode:
        """Convert a database row to an Episode."""
        return Episode(
            id=row["id"],
            session_id=row["session_id"],
            status=EpisodeStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            closed_at=(
                datetime.fromisoformat(row["closed_at"])
                if row["closed_at"]
                else None
            ),
            close_reason=row["close_reason"],
            summary=row["summary"],
            metadata=json.loads(row["metadata"]),
            turn_count=row["turn_count"],
            total_tokens=row["total_tokens"],
            markers=json.loads(row["markers"]),
        )

    # Vector operations

    async def save_embedding(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        """Save an embedding vector."""
        conn = self._ensure_connected()

        # Store embedding as JSON blob (simple approach)
        # For production, consider sqlite-vec extension
        embedding_blob = json.dumps(embedding).encode()

        await conn.execute(
            """
            INSERT OR REPLACE INTO embeddings (id, embedding, metadata)
            VALUES (?, ?, ?)
            """,
            (id, embedding_blob, json.dumps(metadata)),
        )
        await conn.commit()

    async def get_embedding(self, id: str) -> list[float] | None:
        """Get an embedding by ID."""
        conn = self._ensure_connected()
        async with conn.execute(
            "SELECT embedding FROM embeddings WHERE id = ?", (id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                result: list[float] = json.loads(row["embedding"])
                return result
            return None

    async def vector_search(
        self,
        embedding: list[float],
        *,
        k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search for similar vectors.

        Note: This is a simple brute-force implementation.
        For production with large datasets, use sqlite-vec.
        """
        conn = self._ensure_connected()

        async with conn.execute(
            "SELECT id, embedding, metadata FROM embeddings"
        ) as cursor:
            rows = await cursor.fetchall()

        results: list[tuple[str, float, dict[str, Any]]] = []

        for row in rows:
            metadata = json.loads(row["metadata"])

            # Apply filter
            if filter:
                match = all(
                    metadata.get(key) == value for key, value in filter.items()
                )
                if not match:
                    continue

            # Calculate similarity
            emb_vector = json.loads(row["embedding"])
            similarity = cosine_similarity(embedding, emb_vector)
            results.append((row["id"], similarity, metadata))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return [
            VectorSearchResult(id=r[0], score=r[1], metadata=r[2])
            for r in results[:k]
        ]

    # Fact operations

    async def save_fact(self, fact: Fact) -> None:
        """Save a fact to the database."""
        conn = self._ensure_connected()
        await conn.execute(
            """
            INSERT OR REPLACE INTO facts
            (id, session_id, episode_id, content, created_at,
             fact_type, confidence, embedding_id, token_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fact.id,
                fact.session_id,
                fact.episode_id,
                fact.content,
                fact.created_at.isoformat(),
                fact.fact_type,
                fact.confidence,
                fact.embedding_id,
                fact.token_count,
                json.dumps(fact.metadata),
            ),
        )
        await conn.commit()

    async def get_facts_by_session(self, session_id: str) -> list[Fact]:
        """Get all facts for a session."""
        conn = self._ensure_connected()
        async with conn.execute(
            "SELECT * FROM facts WHERE session_id = ? ORDER BY created_at",
            (session_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_fact(row) for row in rows]

    async def get_facts_by_episode(self, episode_id: str) -> list[Fact]:
        """Get facts derived from a specific episode."""
        conn = self._ensure_connected()
        async with conn.execute(
            "SELECT * FROM facts WHERE episode_id = ? ORDER BY created_at",
            (episode_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_fact(row) for row in rows]

    def _row_to_fact(self, row: Any) -> Fact:
        """Convert a database row to a Fact."""
        return Fact(
            id=row["id"],
            session_id=row["session_id"],
            episode_id=row["episode_id"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"]),
            fact_type=row["fact_type"],
            confidence=row["confidence"],
            embedding_id=row["embedding_id"],
            token_count=row["token_count"],
            metadata=json.loads(row["metadata"]),
        )

    # Statistics

    async def get_session_stats(
        self,
        session_id: str,
    ) -> dict[str, Any]:
        """Get statistics for a session."""
        conn = self._ensure_connected()

        # Count turns
        async with conn.execute(
            "SELECT COUNT(*) as count, SUM(token_count) as tokens FROM turns WHERE session_id = ?",
            (session_id,),
        ) as cursor:
            turn_row = await cursor.fetchone()
            total_turns = turn_row["count"] if turn_row else 0
            total_tokens = turn_row["tokens"] or 0 if turn_row else 0

        # Count episodes
        async with conn.execute(
            "SELECT COUNT(*) as count FROM episodes WHERE session_id = ?",
            (session_id,),
        ) as cursor:
            ep_row = await cursor.fetchone()
            total_episodes = ep_row["count"] if ep_row else 0

        # Count facts
        async with conn.execute(
            "SELECT COUNT(*) as count FROM facts WHERE session_id = ?",
            (session_id,),
        ) as cursor:
            fact_row = await cursor.fetchone()
            total_facts = fact_row["count"] if fact_row else 0

        # Get open episode
        async with conn.execute(
            "SELECT id FROM episodes WHERE session_id = ? AND status = 'open'",
            (session_id,),
        ) as cursor:
            open_ep = await cursor.fetchone()
            open_episode_id = open_ep["id"] if open_ep else None

        # Get open episode turn count
        open_episode_turn_count = 0
        if open_episode_id:
            async with conn.execute(
                "SELECT COUNT(*) as count FROM turns WHERE episode_id = ?",
                (open_episode_id,),
            ) as cursor:
                count_row = await cursor.fetchone()
                open_episode_turn_count = count_row["count"] if count_row else 0

        # Get timestamps
        async with conn.execute(
            """
            SELECT MIN(created_at) as created, MAX(created_at) as last
            FROM turns WHERE session_id = ?
            """,
            (session_id,),
        ) as cursor:
            time_row = await cursor.fetchone()
            created_at = (
                datetime.fromisoformat(time_row["created"])
                if time_row and time_row["created"]
                else datetime.utcnow()
            )
            last_activity = (
                datetime.fromisoformat(time_row["last"])
                if time_row and time_row["last"]
                else created_at
            )

        return {
            "session_id": session_id,
            "total_turns": total_turns,
            "total_episodes": total_episodes,
            "total_facts": total_facts,
            "open_episode_id": open_episode_id,
            "open_episode_turn_count": open_episode_turn_count,
            "total_tokens_ingested": total_tokens,
            "created_at": created_at,
            "last_activity_at": last_activity,
        }
