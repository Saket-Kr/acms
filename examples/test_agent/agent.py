"""Main test agent with ACMS integration."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from acms import ACMS, ACMSConfig, MarkerType
from acms.core.config import EpisodeBoundaryConfig, RecallConfig, ReflectionConfig
from acms.storage import get_sqlite_backend

from examples.test_agent.config import SYSTEM_PROMPT, AgentConfig
from examples.test_agent.llm import (
    Message,
    OllamaClient,
    OllamaEmbedder,
    OllamaReflector,
    OpenAIChatClient,
)
from examples.test_agent.tools import TOOL_DEFINITIONS, ToolExecutor

if TYPE_CHECKING:
    from acms.models import ContextItem


@dataclass
class ChatTimings:
    """Timing breakdown from a single chat() call.

    All values are in milliseconds, measured with ``time.perf_counter()``
    for monotonic high-resolution timing.
    """

    ingest_user_ms: int
    recall_ms: int
    ingest_assistant_ms: int
    ingest_facts_ms: int


@dataclass
class AgentResponse:
    """Response from the agent."""

    content: str
    recalled_items: list["ContextItem"]
    tool_calls: list[tuple[str, str]]  # (tool_name, result)
    timings: ChatTimings | None = None


class TestAgent:
    """A conversational agent that uses ACMS for memory management."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self._ollama: OllamaClient | None = None
        self._chat_client: OllamaClient | OpenAIChatClient | None = None
        self._acms: ACMS | None = None
        self._tool_executor: ToolExecutor | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the agent."""
        if self._initialized:
            return

        # Create LLM clients
        self._ollama = OllamaClient(self.config.ollama)
        if self.config.chat_config:
            self._chat_client = OpenAIChatClient(self.config.chat_config)
        else:
            self._chat_client = self._ollama

        # Create ACMS components
        SQLiteBackend = get_sqlite_backend()
        storage = SQLiteBackend(self.config.db_path)

        embedder = OllamaEmbedder(self._ollama)
        reflector = OllamaReflector(self._chat_client)

        # Configure ACMS
        acms_config = ACMSConfig(
            auto_detect_markers=True,
            episode_boundary=EpisodeBoundaryConfig(
                max_turns=self.config.max_turns_per_episode,
                max_time_gap_seconds=1800,
                close_on_tool_result=False,  # Don't close on tool results
            ),
            recall=RecallConfig(
                default_token_budget=self.config.token_budget,
                current_episode_budget_pct=0.5,
            ),
            reflection=ReflectionConfig(
                enabled=True,
                min_episode_turns=3,
                max_facts_per_episode=5,
            ),
        )

        # Create ACMS
        self._acms = ACMS(
            session_id=self.config.session_id,
            storage=storage,
            embedder=embedder,
            reflector=reflector,
            config=acms_config,
        )
        await self._acms.initialize()

        # Create tool executor
        self._tool_executor = ToolExecutor(self._chat_client)

        self._initialized = True

    async def close(self) -> None:
        """Close the agent and release resources."""
        if self._acms:
            await self._acms.close()
        if self._chat_client and self._chat_client is not self._ollama:
            await self._chat_client.close()
        if self._ollama:
            await self._ollama.close()
        self._initialized = False

    async def chat(self, user_message: str) -> AgentResponse:
        """Process a user message and return a response.

        Args:
            user_message: The user's message

        Returns:
            Agent response with content and metadata
        """
        if not self._initialized:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        assert self._acms is not None
        assert self._chat_client is not None
        assert self._tool_executor is not None

        # 1. Ingest user message (timed)
        t0 = time.perf_counter()
        await self._acms.ingest("user", user_message)
        ingest_user_ms = int((time.perf_counter() - t0) * 1000)

        # 2. Recall relevant context (timed)
        t0 = time.perf_counter()
        recalled = await self._acms.recall(
            user_message,
            token_budget=self.config.token_budget,
        )
        recall_ms = int((time.perf_counter() - t0) * 1000)

        # 3. Build conversation messages
        messages = self._build_messages(user_message, recalled)

        # 4. Call LLM (with tool loop) — not timed as ACMS overhead
        tool_calls_made: list[tuple[str, str]] = []
        response = await self._chat_client.chat(messages, tools=TOOL_DEFINITIONS)

        # Tool execution loop
        while response.tool_calls:
            for tool_call in response.tool_calls:
                result = await self._tool_executor.execute(
                    tool_call.name,
                    tool_call.arguments,
                )
                tool_calls_made.append((tool_call.name, result))

                # Add tool result to messages
                messages.append(
                    Message(
                        role="assistant",
                        content="",
                        tool_calls=[
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.name,
                                    "arguments": tool_call.arguments,
                                },
                            }
                        ],
                    )
                )
                messages.append(
                    Message(
                        role="tool",
                        content=result,
                        tool_call_id=tool_call.id,
                    )
                )

            # Continue the conversation
            response = await self._chat_client.chat(messages, tools=TOOL_DEFINITIONS)

        # 5. Ingest assistant response with marker detection (timed)
        t0 = time.perf_counter()
        markers = self._detect_explicit_markers(response.content)
        await self._acms.ingest("assistant", response.content, markers=markers)
        ingest_assistant_ms = int((time.perf_counter() - t0) * 1000)

        # 6. Handle any pending remember facts (timed)
        t0 = time.perf_counter()
        for fact in self._tool_executor.get_pending_facts():
            await self._acms.ingest(
                "assistant",
                f"[Remembered] {fact}",
                markers=["custom:explicit_memory"],
            )
        ingest_facts_ms = int((time.perf_counter() - t0) * 1000)

        timings = ChatTimings(
            ingest_user_ms=ingest_user_ms,
            recall_ms=recall_ms,
            ingest_assistant_ms=ingest_assistant_ms,
            ingest_facts_ms=ingest_facts_ms,
        )

        return AgentResponse(
            content=response.content,
            recalled_items=recalled,
            tool_calls=tool_calls_made,
            timings=timings,
        )

    def _build_messages(
        self,
        current_message: str,
        recalled: list["ContextItem"],
    ) -> list[Message]:
        """Build the message list for the LLM."""
        messages = [Message(role="system", content=SYSTEM_PROMPT)]

        # Add recalled context as conversation history
        if recalled:
            context_text = "Previous relevant context:\n"
            for item in recalled:
                marker_str = f" [{', '.join(item.markers)}]" if item.markers else ""
                context_text += f"[{item.role.value}{marker_str}]: {item.content}\n"

            messages.append(
                Message(
                    role="system",
                    content=f"---\n{context_text}---\n\nNow respond to the current message:",
                )
            )

        # Add current message
        messages.append(Message(role="user", content=current_message))

        return messages

    def _detect_explicit_markers(self, content: str) -> list[str]:
        """Detect explicit markers from response content."""
        markers = []
        content_lower = content.lower()

        if "decision:" in content_lower:
            markers.append(MarkerType.DECISION.value)
        if "constraint:" in content_lower:
            markers.append(MarkerType.CONSTRAINT.value)
        if "failed:" in content_lower or "error:" in content_lower:
            markers.append(MarkerType.FAILURE.value)
        if "goal:" in content_lower:
            markers.append(MarkerType.GOAL.value)

        return markers

    async def get_stats(self) -> dict[str, int | str | None]:
        """Get session statistics."""
        if not self._acms:
            return {}

        stats = await self._acms.get_session_stats()
        return {
            "session_id": stats.session_id,
            "turns": stats.total_turns,
            "episodes": stats.total_episodes,
            "facts": stats.total_facts,
            "open_episode": stats.open_episode_id,
            "open_episode_turns": stats.open_episode_turn_count,
            "tokens_ingested": stats.total_tokens_ingested,
        }

    async def close_episode(self, reason: str = "manual") -> str | None:
        """Manually close the current episode."""
        if not self._acms:
            return None
        return await self._acms.close_episode(reason)

    async def recall(self, query: str) -> list["ContextItem"]:
        """Directly test recall with a query."""
        if not self._acms:
            return []
        return await self._acms.recall(query, token_budget=self.config.token_budget)

    async def get_consolidation_stats(self) -> dict[str, int | float] | None:
        """Get consolidation statistics (active vs superseded facts).

        Returns:
            Dict with active_facts_count, superseded_facts_count,
            total_facts_count, consolidation_ratio. Or None if ACMS
            is not initialized.
        """
        if not self._acms:
            return None
        storage = self._acms._storage  # noqa: SLF001
        session_id = self.config.session_id
        all_facts = await storage.get_facts_by_session(session_id)
        active_facts = await storage.get_active_facts_by_session(session_id)
        total = len(all_facts)
        active = len(active_facts)
        superseded = total - active
        return {
            "active_facts_count": active,
            "superseded_facts_count": superseded,
            "total_facts_count": total,
            "consolidation_ratio": superseded / total if total > 0 else 0.0,
        }
