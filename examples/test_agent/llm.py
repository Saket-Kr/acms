"""Ollama API wrapper for chat and embeddings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

from examples.test_agent.config import OllamaConfig


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

        response = await self._client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
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

            response = await self._client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
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
    """ACMS-compatible reflector using Ollama for fact extraction."""

    REFLECTION_PROMPT = """Analyze this conversation episode and extract key facts.

Focus on:
- DECISIONS: Choices made (what was decided and why)
- CONSTRAINTS: Limitations discovered (what cannot/should not be done)
- FAILURES: What didn't work (to avoid repeating)
- GOALS: Objectives established (what the user wants to achieve)

Episode turns:
{turns}

Extract up to {max_facts} facts. For each fact:
1. State it concisely (one sentence)
2. Classify its type (decision/constraint/failure/goal)
3. Rate your confidence (0-1)

Respond ONLY with valid JSON in this exact format, no other text:
{{"facts": [
  {{"content": "...", "type": "decision", "confidence": 0.9}},
  ...
]}}"""

    def __init__(self, client: OllamaClient, max_facts: int = 5) -> None:
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

        prompt = self.REFLECTION_PROMPT.format(
            turns=turns_text,
            max_facts=self._max_facts,
        )

        # Call LLM
        response = await self._client.chat([Message(role="user", content=prompt)])

        # Parse facts from response
        return self._parse_facts(response.content, episode)

    def _parse_facts(self, content: str, episode: Any) -> list[Any]:
        """Parse facts from LLM response."""
        from datetime import datetime

        from acms.models import Fact, MarkerType
        from acms.utils import generate_fact_id

        try:
            # Find JSON in response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
                facts_data = data.get("facts", [])
            else:
                return []
        except json.JSONDecodeError:
            return []

        facts = []
        for item in facts_data:
            fact_type = item.get("type", "decision")
            if fact_type not in [m.value for m in MarkerType]:
                fact_type = MarkerType.DECISION.value

            facts.append(
                Fact(
                    id=generate_fact_id(),
                    session_id=episode.session_id,
                    episode_id=episode.id,
                    content=item.get("content", ""),
                    created_at=datetime.utcnow(),
                    fact_type=fact_type,
                    confidence=float(item.get("confidence", 0.8)),
                )
            )

        return facts
