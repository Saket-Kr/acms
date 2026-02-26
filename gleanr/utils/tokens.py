"""Token counting utilities."""

from __future__ import annotations

from typing import Protocol


class TokenCounter(Protocol):
    """Protocol for token counting implementations."""

    def count(self, text: str) -> int:
        """Count tokens in text."""
        ...


class HeuristicTokenCounter:
    """Simple heuristic token counter.

    Uses character-based estimation: ~4 characters per token.
    This is a reasonable approximation for English text.
    """

    def __init__(self, chars_per_token: float = 4.0) -> None:
        self.chars_per_token = chars_per_token

    def count(self, text: str) -> int:
        """Count tokens using character-based heuristic."""
        if not text:
            return 0
        return max(1, int(len(text) / self.chars_per_token))


class TiktokenCounter:
    """Token counter using tiktoken library.

    Requires the tiktoken optional dependency.
    """

    def __init__(self, model: str = "gpt-4") -> None:
        try:
            import tiktoken
        except ImportError as e:
            raise ImportError(
                "tiktoken is required for TiktokenCounter. "
                "Install with: pip install gleanr[tiktoken]"
            ) from e

        self._encoding = tiktoken.encoding_for_model(model)

    def count(self, text: str) -> int:
        """Count tokens using tiktoken."""
        if not text:
            return 0
        return len(self._encoding.encode(text))


def get_default_token_counter() -> TokenCounter:
    """Get the default token counter.

    Uses tiktoken if available, falls back to heuristic.
    """
    try:
        return TiktokenCounter()
    except ImportError:
        return HeuristicTokenCounter()
