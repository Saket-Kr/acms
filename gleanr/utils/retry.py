"""Retry utilities with exponential backoff."""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, TypeVar

from gleanr.errors import RetryExhaustedError

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 0.5
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = field(
        default_factory=lambda: (
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
        )
    )


def calculate_delay(
    attempt: int,
    config: RetryConfig,
) -> float:
    """Calculate delay for a retry attempt.

    Uses exponential backoff with optional jitter.
    """
    delay = config.base_delay * (config.exponential_base ** (attempt - 1))
    delay = min(delay, config.max_delay)

    if config.jitter:
        # Add jitter: ±25% of calculated delay
        jitter_range = delay * 0.25
        delay = delay + random.uniform(-jitter_range, jitter_range)

    return max(0.0, delay)


async def with_retry(
    fn: Callable[..., Awaitable[T]],
    config: RetryConfig | None = None,
    *,
    on_retry: Callable[[int, Exception], None] | None = None,
    **kwargs: Any,
) -> T:
    """Execute an async function with retry logic.

    Args:
        fn: Async function to execute
        config: Retry configuration (uses defaults if None)
        on_retry: Optional callback called on each retry with (attempt, error)
        **kwargs: Arguments to pass to the function

    Returns:
        Result of the function

    Raises:
        RetryExhaustedError: If all retry attempts fail
        Exception: If a non-retryable exception occurs
    """
    if config is None:
        config = RetryConfig()

    last_error: Exception | None = None

    for attempt in range(1, config.max_attempts + 1):
        try:
            return await fn(**kwargs)
        except config.retryable_exceptions as e:
            last_error = e

            if attempt == config.max_attempts:
                break

            if on_retry:
                on_retry(attempt, e)

            delay = calculate_delay(attempt, config)
            await asyncio.sleep(delay)

    raise RetryExhaustedError(
        f"All {config.max_attempts} retry attempts exhausted",
        attempts=config.max_attempts,
        last_error=last_error,
    )


async def retry_with_fallback(
    primary: Callable[..., Awaitable[T]],
    fallback: Callable[..., Awaitable[T]],
    config: RetryConfig | None = None,
    **kwargs: Any,
) -> T:
    """Execute primary function with retries, fall back on exhaustion.

    Args:
        primary: Primary async function to execute
        fallback: Fallback function if primary fails
        config: Retry configuration
        **kwargs: Arguments to pass to both functions

    Returns:
        Result from primary or fallback
    """
    try:
        return await with_retry(primary, config, **kwargs)
    except RetryExhaustedError:
        return await fallback(**kwargs)
