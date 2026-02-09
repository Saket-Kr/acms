"""ACMS provider protocols and implementations."""

from acms.providers.base import (
    Embedder,
    NullEmbedder,
    NullReflector,
    Reflector,
    TokenCounter,
)

__all__ = [
    # Protocols
    "Embedder",
    "Reflector",
    "TokenCounter",
    # Null implementations
    "NullEmbedder",
    "NullReflector",
]


def get_http_embedder() -> type:
    """Get HTTPEmbedder class (lazy import)."""
    from acms.providers.http import HTTPEmbedder

    return HTTPEmbedder


def get_http_reflector() -> type:
    """Get HTTPReflector class (lazy import)."""
    from acms.providers.http import HTTPReflector

    return HTTPReflector


def get_openai_embedder() -> type:
    """Get OpenAIEmbedder class (lazy import)."""
    from acms.providers.openai import OpenAIEmbedder

    return OpenAIEmbedder


def get_openai_reflector() -> type:
    """Get OpenAIReflector class (lazy import)."""
    from acms.providers.openai import OpenAIReflector

    return OpenAIReflector


def get_anthropic_reflector() -> type:
    """Get AnthropicReflector class (lazy import)."""
    from acms.providers.anthropic import AnthropicReflector

    return AnthropicReflector
