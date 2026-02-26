"""Turn ingestion pipeline."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from gleanr.errors import ProviderError, ValidationError
from gleanr.models import Role, Turn
from gleanr.utils import (
    TokenCounter,
    detect_markers,
    generate_embedding_id,
    generate_turn_id,
    merge_markers,
    validate_content,
    validate_markers,
    validate_metadata,
    validate_role,
)

if TYPE_CHECKING:
    from gleanr.core.config import GleanrConfig
    from gleanr.memory.episode_manager import EpisodeManager
    from gleanr.providers import Embedder
    from gleanr.storage import StorageBackend


class IngestionPipeline:
    """Pipeline for ingesting turns into memory.

    Handles:
    - Turn creation and validation
    - Marker detection and assignment
    - Episode assignment
    - Embedding generation
    - Storage persistence
    """

    def __init__(
        self,
        session_id: str,
        storage: "StorageBackend",
        embedder: "Embedder",
        token_counter: TokenCounter,
        episode_manager: "EpisodeManager",
        config: "GleanrConfig",
    ) -> None:
        self._session_id = session_id
        self._storage = storage
        self._embedder = embedder
        self._token_counter = token_counter
        self._episode_manager = episode_manager
        self._config = config
        self._turn_position = 0

    async def initialize(self) -> None:
        """Initialize the pipeline."""
        # Get current turn count for position tracking
        turns = await self._storage.get_turns_by_session(self._session_id)
        self._turn_position = len(turns)

    async def ingest(
        self,
        role: str | Role,
        content: str,
        *,
        actor_id: str | None = None,
        markers: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Ingest a turn into memory.

        Args:
            role: Who produced this turn (user, assistant, tool)
            content: The turn content
            actor_id: Optional identifier for the actor
            markers: Optional importance markers
            metadata: Optional arbitrary metadata

        Returns:
            Turn ID

        Raises:
            ValidationError: If input is invalid
            ProviderError: If embedding fails
        """
        # Validate inputs
        validated_role = validate_role(role)
        validated_content = validate_content(content)
        validated_markers = validate_markers(markers)
        validated_metadata = validate_metadata(metadata)

        # Check content length
        if len(validated_content) > self._config.max_content_length:
            raise ValidationError(
                f"Content exceeds maximum length of {self._config.max_content_length}",
                field="content",
            )

        # Auto-detect markers if enabled
        if self._config.auto_detect_markers:
            detected = detect_markers(validated_content)
            validated_markers = merge_markers(validated_markers or None, detected)

        # Count tokens
        token_count = self._token_counter.count(validated_content)

        # Create turn
        turn = Turn(
            id=generate_turn_id(),
            session_id=self._session_id,
            episode_id="",  # Will be assigned by episode manager
            role=validated_role,
            content=validated_content,
            created_at=datetime.utcnow(),
            actor_id=actor_id,
            markers=validated_markers,
            metadata=validated_metadata,
            token_count=token_count,
            position=self._turn_position,
        )

        # Assign to episode (may trigger episode close)
        episode_id = await self._episode_manager.assign_episode(turn)
        turn.episode_id = episode_id

        # Generate and store embedding
        embedding_id = await self._generate_embedding(turn)
        turn.embedding_id = embedding_id

        # Save turn
        await self._storage.save_turn(turn)
        self._turn_position += 1

        return turn.id

    async def _generate_embedding(self, turn: Turn) -> str | None:
        """Generate and store embedding for a turn.

        Args:
            turn: Turn to embed

        Returns:
            Embedding ID, or None if embedding is skipped
        """
        try:
            # Generate embedding
            embeddings = await self._embedder.embed([turn.content])
            if not embeddings:
                return None

            embedding = embeddings[0]
            embedding_id = generate_embedding_id()

            # Store embedding with metadata for filtering
            await self._storage.save_embedding(
                id=embedding_id,
                embedding=embedding,
                metadata={
                    "session_id": turn.session_id,
                    "episode_id": turn.episode_id,
                    "turn_id": turn.id,
                    "type": "turn",
                    "role": turn.role.value,
                    "has_markers": bool(turn.markers),
                },
            )

            return embedding_id

        except Exception as e:
            # Log but don't fail ingestion if embedding fails
            # The turn is still valuable without its embedding
            if isinstance(e, ProviderError):
                raise
            raise ProviderError(
                f"Failed to generate embedding: {e}",
                provider="embedder",
                retryable=True,
                cause=e,
            ) from e
