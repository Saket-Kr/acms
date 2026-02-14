"""LLM client wrappers for chat and embeddings."""

from __future__ import annotations

import asyncio
import json
import logging
import random
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

import httpx

logger = logging.getLogger(__name__)

from examples.test_agent.config import ChatConfig, OllamaConfig

# Maximum retries and base delay for transient API errors.
_MAX_RETRIES = 8
_BASE_DELAY = 1.0  # seconds
_RETRIABLE_EXCEPTIONS = (
    httpx.HTTPStatusError,
    httpx.ReadTimeout,
    httpx.ReadError,
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.RemoteProtocolError,
    ValueError,
)
# OpenAI SDK exceptions added separately to avoid import at module level.
try:
    from openai import APIConnectionError, APITimeoutError, APIStatusError

    _RETRIABLE_EXCEPTIONS = (  # type: ignore[misc]
        *_RETRIABLE_EXCEPTIONS,
        APIConnectionError,
        APITimeoutError,
        APIStatusError,
    )
except ImportError:
    pass


async def _retry_request(
    fn: Any,
    *,
    max_retries: int = _MAX_RETRIES,
    label: str = "request",
) -> Any:
    """Execute *fn* (an async callable returning a value) with retries.

    Uses exponential backoff with jitter. Retries on any exception in
    ``_RETRIABLE_EXCEPTIONS``.
    """
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            return await fn()
        except _RETRIABLE_EXCEPTIONS as exc:
            last_error = exc
            if attempt < max_retries - 1:
                delay = _BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    "%s failed (attempt %d/%d), retrying in %.1fs: %s",
                    label, attempt + 1, max_retries, delay, exc,
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "%s failed after %d attempts: %s",
                    label, max_retries, exc,
                )
                raise


@dataclass
class Message:
    """A chat message."""

    role: str  # "system", "user", "assistant", "tool"
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


@dataclass
class ToolCall:
    """A tool call from the LLM."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ChatResponse:
    """Response from chat completion."""

    content: str
    tool_calls: list[ToolCall]
    finish_reason: str


@runtime_checkable
class ChatClient(Protocol):
    """Protocol for any client that can do chat completions."""

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatResponse: ...


class OllamaClient:
    """Client for Ollama API."""

    def __init__(self, config: OllamaConfig) -> None:
        self.config = config
        self._client = httpx.AsyncClient(timeout=300.0)  # 5 min timeout for longer conversations

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatResponse:
        """Send a chat completion request.

        Args:
            messages: Conversation messages
            tools: Optional tool definitions

        Returns:
            Chat response with content and/or tool calls
        """
        url = f"{self.config.host}/api/chat"

        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            m: dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                m["tool_calls"] = msg.tool_calls
            ollama_messages.append(m)

        payload: dict[str, Any] = {
            "model": self.config.chat_model,
            "messages": ollama_messages,
            "stream": False,
        }

        if tools:
            payload["tools"] = tools

        async def _do_ollama_chat() -> dict:
            resp = await self._client.post(url, json=payload)
            resp.raise_for_status()
            d = resp.json()
            if not d:
                raise ValueError(f"Empty Ollama response: {resp.text[:200]}")
            return d

        data = await _retry_request(_do_ollama_chat, label="ollama-chat")

        msg = data.get("message", {})

        # Parse tool calls if present
        tool_calls = []
        if "tool_calls" in msg:
            for tc in msg["tool_calls"]:
                func = tc.get("function", {})
                tool_calls.append(
                    ToolCall(
                        id=tc.get("id", f"call_{len(tool_calls)}"),
                        name=func.get("name", ""),
                        arguments=func.get("arguments", {}),
                    )
                )

        return ChatResponse(
            content=msg.get("content", ""),
            tool_calls=tool_calls,
            finish_reason=data.get("done_reason", "stop"),
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        url = f"{self.config.host}/api/embed"

        embeddings = []
        for text in texts:
            payload = {
                "model": self.config.embed_model,
                "input": text,
            }

            async def _do_embed() -> dict:
                resp = await self._client.post(url, json=payload)
                resp.raise_for_status()
                d = resp.json()
                if not d or ("embeddings" not in d and "embedding" not in d):
                    raise ValueError(f"Unexpected embedding response: {resp.text[:200]}")
                return d

            data = await _retry_request(_do_embed, label="embed")

            # Ollama returns embeddings in "embeddings" field (list of lists)
            # or sometimes in "embedding" field (single list)
            if "embeddings" in data:
                embeddings.append(data["embeddings"][0])
            elif "embedding" in data:
                embeddings.append(data["embedding"])
            else:
                raise ValueError(f"Unexpected embedding response: {data}")

        return embeddings

    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return self.config.embed_dimension


class OpenAIChatClient:
    """Client for OpenAI-compatible chat API using the official OpenAI SDK.

    Uses streaming to match production behavior and avoid null responses
    from inference servers that time out on non-streaming requests.
    """

    def __init__(self, config: ChatConfig) -> None:
        self.config = config
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(
            api_key=config.api_key or "no-key",
            base_url=config.base_url,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.close()

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatResponse:
        """Send a streaming chat completion request via OpenAI SDK."""
        openai_messages: list[dict[str, Any]] = []
        for msg in messages:
            m: dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                m["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                m["tool_call_id"] = msg.tool_call_id
            openai_messages.append(m)

        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": openai_messages,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools

        async def _do_chat() -> ChatResponse:
            stream = await self._client.chat.completions.create(**kwargs)

            content_parts: list[str] = []
            tool_calls_map: dict[int, dict[str, Any]] = {}
            finish_reason = "stop"

            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason

                # Accumulate content — some models put the response in
                # reasoning_content instead of content (thinking mode).
                if delta.content:
                    content_parts.append(delta.content)
                elif hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    content_parts.append(delta.reasoning_content)

                # Accumulate tool calls
                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        if idx not in tool_calls_map:
                            tool_calls_map[idx] = {
                                "id": tc_delta.id or "",
                                "name": "",
                                "arguments": "",
                            }
                        entry = tool_calls_map[idx]
                        if tc_delta.id:
                            entry["id"] = tc_delta.id
                        if tc_delta.function:
                            if tc_delta.function.name:
                                entry["name"] = tc_delta.function.name
                            if tc_delta.function.arguments:
                                entry["arguments"] += tc_delta.function.arguments

            # Parse accumulated tool calls
            tool_calls: list[ToolCall] = []
            for idx in sorted(tool_calls_map):
                entry = tool_calls_map[idx]
                arguments = entry["arguments"]
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except (json.JSONDecodeError, TypeError):
                        arguments = {}
                tool_calls.append(
                    ToolCall(
                        id=entry["id"] or f"call_{idx}",
                        name=entry["name"],
                        arguments=arguments,
                    )
                )

            content = "".join(content_parts)
            if not content and not tool_calls:
                raise ValueError("Empty streaming response: no content or tool calls")

            return ChatResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
            )

        return await _retry_request(_do_chat, label="chat")


class OllamaEmbedder:
    """ACMS-compatible embedder using Ollama."""

    def __init__(self, client: OllamaClient) -> None:
        self._client = client

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts."""
        return await self._client.embed(texts)

    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return self._client.dimension


class OllamaReflector:
    """ACMS-compatible reflector using an LLM for fact extraction."""

    def __init__(self, client: ChatClient, max_facts: int = 5) -> None:
        self._client = client
        self._max_facts = max_facts

    async def reflect(
        self, episode: Any, turns: list[Any]
    ) -> list[Any]:
        """Extract semantic facts from an episode."""
        from datetime import datetime

        from acms.models import Fact, MarkerType
        from acms.utils import generate_fact_id

        if not turns:
            return []

        # Format turns for the prompt
        turns_text = "\n".join(f"[{t.role.value}]: {t.content}" for t in turns)

        from acms.providers.parsing import REFLECTION_PROMPT

        prompt = REFLECTION_PROMPT.format(
            turns=turns_text,
            max_facts=self._max_facts,
        )

        # Call LLM
        response = await self._client.chat([Message(role="user", content=prompt)])

        # Parse facts from response
        return self._parse_facts(response.content, episode)

    def _parse_facts(self, content: str, episode: Any) -> list[Any]:
        """Parse facts from LLM response."""
        from acms.providers.parsing import parse_reflection_facts

        return parse_reflection_facts(content, episode)

    async def reflect_with_consolidation(
        self,
        episode: Any,
        turns: list[Any],
        prior_facts: list[Any],
    ) -> list[Any]:
        """Consolidate prior facts with new episode content."""
        from acms.models.consolidation import ConsolidationAction
        from acms.providers.parsing import (
            CONSOLIDATION_PROMPT,
            format_prior_facts,
            format_turns,
            parse_consolidation_actions,
        )

        if not turns:
            return []

        prompt = CONSOLIDATION_PROMPT.format(
            prior_facts=format_prior_facts(prior_facts),
            turns=format_turns(turns),
        )

        response = await self._client.chat([Message(role="user", content=prompt)])
        return parse_consolidation_actions(response.content)
