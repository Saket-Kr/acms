"""ACMS - Agent Context Management System.

A session-scoped memory layer for AI agents, providing intelligent,
token-budgeted context assembly.

Example:
    >>> from acms import ACMS
    >>> from acms.storage import InMemoryBackend
    >>>
    >>> async def main():
    ...     storage = InMemoryBackend()
    ...     async with ACMS("session_123", storage) as acms:
    ...         await acms.ingest("user", "Hello!")
    ...         await acms.ingest("assistant", "Hi there!")
    ...         context = await acms.recall("greeting")
    ...         print(f"Found {len(context)} items")
"""

from acms.core import (
    ACMS,
    ACMSConfig,
    EpisodeBoundaryConfig,
    RecallConfig,
    ReflectionConfig,
    create_config,
)
from acms.errors import (
    ACMSError,
    ConfigurationError,
    EpisodeNotFoundError,
    ProviderError,
    ReflectionError,
    RetryExhaustedError,
    SessionNotFoundError,
    StorageError,
    TokenBudgetExceededError,
    TurnNotFoundError,
    ValidationError,
)
from acms.models import (
    ContextItem,
    Episode,
    EpisodeStatus,
    Fact,
    MarkerType,
    Role,
    SessionStats,
    Turn,
)
from acms.providers import Embedder, NullEmbedder, NullReflector, Reflector, TokenCounter
from acms.storage import InMemoryBackend, StorageBackend

__version__ = "0.1.0"

__all__ = [
    # Main class
    "ACMS",
    # Configuration
    "ACMSConfig",
    "EpisodeBoundaryConfig",
    "RecallConfig",
    "ReflectionConfig",
    "create_config",
    # Models
    "Turn",
    "Episode",
    "Fact",
    "ContextItem",
    "SessionStats",
    # Enums
    "Role",
    "EpisodeStatus",
    "MarkerType",
    # Protocols
    "Embedder",
    "Reflector",
    "TokenCounter",
    # Null implementations
    "NullEmbedder",
    "NullReflector",
    # Storage
    "StorageBackend",
    "InMemoryBackend",
    # Exceptions
    "ACMSError",
    "ConfigurationError",
    "ValidationError",
    "StorageError",
    "ProviderError",
    "TokenBudgetExceededError",
    "SessionNotFoundError",
    "EpisodeNotFoundError",
    "TurnNotFoundError",
    "ReflectionError",
    "RetryExhaustedError",
]
