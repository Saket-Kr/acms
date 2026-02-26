"""Exception hierarchy for Gleanr."""

from __future__ import annotations


class GleanrError(Exception):
    """Base exception for all Gleanr errors."""

    pass


class ConfigurationError(GleanrError):
    """Invalid configuration.

    Raised when Gleanr is configured with invalid parameters.
    """

    pass


class ValidationError(GleanrError):
    """Input validation failed.

    Raised when input to Gleanr methods fails validation.
    """

    def __init__(self, message: str, *, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field


class StorageError(GleanrError):
    """Storage operation failed.

    Raised when a storage backend operation fails.
    """

    def __init__(
        self,
        message: str,
        *,
        operation: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.operation = operation
        self.cause = cause


class ProviderError(GleanrError):
    """Provider operation failed.

    Raised when an embedder, reflector, or other provider fails.
    """

    def __init__(
        self,
        message: str,
        *,
        provider: str,
        retryable: bool = False,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.retryable = retryable
        self.cause = cause


class TokenBudgetExceededError(GleanrError):
    """Token budget cannot be satisfied.

    Raised when the minimum required context exceeds the budget.
    """

    def __init__(
        self,
        message: str,
        *,
        budget: int,
        required: int,
    ) -> None:
        super().__init__(message)
        self.budget = budget
        self.required = required


class SessionNotFoundError(GleanrError):
    """Session does not exist.

    Raised when attempting to access a non-existent session.
    """

    def __init__(self, session_id: str) -> None:
        super().__init__(f"Session not found: {session_id}")
        self.session_id = session_id


class EpisodeNotFoundError(GleanrError):
    """Episode does not exist.

    Raised when attempting to access a non-existent episode.
    """

    def __init__(self, episode_id: str) -> None:
        super().__init__(f"Episode not found: {episode_id}")
        self.episode_id = episode_id


class TurnNotFoundError(GleanrError):
    """Turn does not exist.

    Raised when attempting to access a non-existent turn.
    """

    def __init__(self, turn_id: str) -> None:
        super().__init__(f"Turn not found: {turn_id}")
        self.turn_id = turn_id


class ReflectionError(GleanrError):
    """Reflection operation failed.

    Raised when LLM-assisted reflection fails.
    """

    def __init__(
        self,
        message: str,
        *,
        episode_id: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.episode_id = episode_id
        self.cause = cause


class RetryExhaustedError(GleanrError):
    """All retry attempts exhausted.

    Raised when an operation fails after all retry attempts.
    """

    def __init__(
        self,
        message: str,
        *,
        attempts: int,
        last_error: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error
