"""HTTP-based providers for embeddings and reflection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from gleanr.errors import ProviderError
from gleanr.models import Fact
from gleanr.models.consolidation import ConsolidationAction
from gleanr.providers.parsing import (
    CONSOLIDATION_PROMPT,
    REFLECTION_PROMPT,
    format_prior_facts,
    format_turns,
    parse_consolidation_actions,
    parse_reflection_facts,
)
from gleanr.utils import RetryConfig, with_retry

if TYPE_CHECKING:
    from gleanr.models import Episode, Turn

# Default model dimensions
MODEL_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


class HTTPEmbedder:
    """Embedder using raw HTTP calls to OpenAI-compatible endpoint.

    Works with OpenAI, Azure OpenAI, and any compatible API.
    Requires the httpx optional dependency.
    """

    def __init__(
        self,
        base_url: str,
        model: str = "text-embedding-3-small",
        *,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        dimension: int | None = None,
    ) -> None:
        """Initialize HTTP embedder.

        Args:
            base_url: Base URL for the API (e.g., "https://api.openai.com/v1")
            model: Model name
            api_key: API key (optional, can be set via headers)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            dimension: Override embedding dimension (auto-detected if None)
        """
        try:
            import httpx
        except ImportError as e:
            raise ImportError(
                "httpx is required for HTTPEmbedder. "
                "Install with: pip install gleanr[http]"
            ) from e

        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout
        self._max_retries = max_retries
        self._dimension = dimension or MODEL_DIMENSIONS.get(model, 1536)

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=self._build_headers(),
        )

        self._retry_config = RetryConfig(
            max_attempts=max_retries,
            base_delay=0.5,
            max_delay=30.0,
            retryable_exceptions=(
                httpx.TimeoutException,
                httpx.ConnectError,
                httpx.RemoteProtocolError,
            ),
        )

    def _build_headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {
            "Content-Type": "application/json",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            ProviderError: If embedding fails
        """
        if not texts:
            return []

        try:
            return await with_retry(
                self._embed_request,
                self._retry_config,
                texts=texts,
            )
        except Exception as e:
            raise ProviderError(
                f"Embedding request failed: {e}",
                provider="HTTPEmbedder",
                retryable=True,
                cause=e,
            ) from e

    async def _embed_request(self, texts: list[str]) -> list[list[float]]:
        """Make the actual embedding request."""
        import httpx

        url = f"{self._base_url}/embeddings"
        payload = {
            "model": self._model,
            "input": texts,
        }

        response = await self._client.post(url, json=payload)

        if response.status_code != 200:
            error_text = response.text
            retryable = response.status_code in (429, 500, 502, 503, 504)
            raise ProviderError(
                f"Embedding API error {response.status_code}: {error_text}",
                provider="HTTPEmbedder",
                retryable=retryable,
            )

        data = response.json()
        embeddings = [item["embedding"] for item in data.get("data", [])]

        if len(embeddings) != len(texts):
            raise ProviderError(
                f"Expected {len(texts)} embeddings, got {len(embeddings)}",
                provider="HTTPEmbedder",
                retryable=False,
            )

        return embeddings

    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return self._dimension

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()


class HTTPReflector:
    """Reflector using raw HTTP calls to OpenAI-compatible chat endpoint.

    Extracts semantic facts from episodes using LLM analysis.
    """

    def __init__(
        self,
        base_url: str,
        model: str = "gpt-4o-mini",
        *,
        api_key: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
        max_facts: int = 5,
    ) -> None:
        """Initialize HTTP reflector.

        Args:
            base_url: Base URL for the API
            model: Model name for chat completions
            api_key: API key
            timeout: Request timeout
            max_retries: Maximum retry attempts
            max_facts: Maximum facts to extract per episode
        """
        try:
            import httpx
        except ImportError as e:
            raise ImportError(
                "httpx is required for HTTPReflector. "
                "Install with: pip install gleanr[http]"
            ) from e

        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout
        self._max_retries = max_retries
        self._max_facts = max_facts

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=self._build_headers(),
        )

        self._retry_config = RetryConfig(
            max_attempts=max_retries,
            base_delay=1.0,
            max_delay=60.0,
            retryable_exceptions=(
                httpx.TimeoutException,
                httpx.ConnectError,
                httpx.RemoteProtocolError,
            ),
        )

    def _build_headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {
            "Content-Type": "application/json",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def reflect(self, episode: "Episode", turns: list["Turn"]) -> list[Fact]:
        """Extract semantic facts from an episode.

        Args:
            episode: The episode to reflect on
            turns: Turns belonging to the episode

        Returns:
            List of extracted facts

        Raises:
            ProviderError: If reflection fails
        """
        if not turns:
            return []

        try:
            return await with_retry(
                self._reflect_request,
                self._retry_config,
                episode=episode,
                turns=turns,
            )
        except Exception as e:
            raise ProviderError(
                f"Reflection request failed: {e}",
                provider="HTTPReflector",
                retryable=True,
                cause=e,
            ) from e

    async def _reflect_request(
        self,
        episode: "Episode",
        turns: list["Turn"],
    ) -> list[Fact]:
        """Make the actual reflection request."""
        # Format turns for the prompt
        turns_text = "\n".join(
            f"[{t.role.value}]: {t.content}" for t in turns
        )

        prompt = REFLECTION_PROMPT.format(
            turns=turns_text,
            max_facts=self._max_facts,
        )

        url = f"{self._base_url}/chat/completions"
        payload = {
            "model": self._model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        response = await self._client.post(url, json=payload)

        if response.status_code != 200:
            error_text = response.text
            retryable = response.status_code in (429, 500, 502, 503, 504)
            raise ProviderError(
                f"Reflection API error {response.status_code}: {error_text}",
                provider="HTTPReflector",
                retryable=retryable,
            )

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")

        return self._parse_facts(content, episode)

    def _parse_facts(self, content: str, episode: "Episode") -> list[Fact]:
        """Parse facts from LLM response."""
        return parse_reflection_facts(content, episode)

    async def reflect_with_consolidation(
        self,
        episode: "Episode",
        turns: list["Turn"],
        prior_facts: list[Fact],
    ) -> list[ConsolidationAction]:
        """Consolidate prior facts with new episode content."""
        if not turns:
            return []

        try:
            return await with_retry(
                self._consolidation_request,
                self._retry_config,
                episode=episode,
                turns=turns,
                prior_facts=prior_facts,
            )
        except Exception as e:
            raise ProviderError(
                f"Consolidation request failed: {e}",
                provider="HTTPReflector",
                retryable=True,
                cause=e,
            ) from e

    async def _consolidation_request(
        self,
        episode: "Episode",
        turns: list["Turn"],
        prior_facts: list[Fact],
    ) -> list[ConsolidationAction]:
        """Make the actual consolidation request."""
        prompt = CONSOLIDATION_PROMPT.format(
            prior_facts=format_prior_facts(prior_facts),
            turns=format_turns(turns),
        )

        url = f"{self._base_url}/chat/completions"
        payload = {
            "model": self._model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        response = await self._client.post(url, json=payload)

        if response.status_code != 200:
            error_text = response.text
            retryable = response.status_code in (429, 500, 502, 503, 504)
            raise ProviderError(
                f"Consolidation API error {response.status_code}: {error_text}",
                provider="HTTPReflector",
                retryable=retryable,
            )

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")

        return parse_consolidation_actions(content)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
