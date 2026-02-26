"""Diagnose why facts are missing from consolidation.

Wraps OllamaReflector to intercept and print every LLM call
and its parsed output, so we can see exactly what the model
returned vs what made it into storage.

Usage:
    python -m examples.diagnose_missing_facts
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from gleanr import Gleanr, GleanrConfig
from gleanr.core.config import EpisodeBoundaryConfig, RecallConfig, ReflectionConfig
from gleanr.storage import get_sqlite_backend


TURNS: list[tuple[str, str]] = [
    ("user", "I want to generate a landscape image — rolling green hills, a few scattered birds in the sky, and warm daytime lighting."),
    ("assistant", "Got it. I'll start with: rolling green hills, scattered birds, warm daytime lighting. Aspect ratio 16:9 by default."),
    ("user", "Add a small cottage on the left side of the hills."),
    ("assistant", "Updated the prompt to include a small cottage on the left side."),
    ("user", "Actually, change the time of day to evening with a golden sunset. And replace the birds with fireflies."),
    ("assistant", "Understood — switching to evening golden sunset and replacing birds with fireflies."),
    ("user", "Add a winding river through the middle of the landscape. Also, the style should be watercolor, not photorealistic."),
    ("assistant", "Adding a winding river and switching to watercolor style."),
    ("user", "The cottage should be larger and have warm light coming from the windows. Remove the fireflies, they clash with watercolor."),
    ("assistant", "Final prompt: watercolor landscape — rolling green hills, golden sunset evening, large cottage with warm window light on the left, winding river through the middle. 16:9."),
]


class DiagnosticReflector:
    """Wraps OllamaReflector to log every call."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self._call_num = 0

    async def reflect(self, episode: Any, turns: list[Any]) -> list[Any]:
        self._call_num += 1
        print(f"\n{'─' * 60}")
        print(f"  REFLECT CALL #{self._call_num} (legacy path)")
        print(f"  Episode: {episode.id}")
        print(f"  Turns ({len(turns)}):")
        for t in turns:
            print(f"    [{t.role.value}]: {t.content[:80]}")
        print(f"{'─' * 60}")

        facts = await self._inner.reflect(episode, turns)

        print(f"\n  RETURNED {len(facts)} facts:")
        for f in facts:
            print(f"    - ({f.fact_type}) {f.content}")
        print()
        return facts

    async def reflect_with_consolidation(
        self, episode: Any, turns: list[Any], prior_facts: list[Any]
    ) -> list[Any]:
        self._call_num += 1
        print(f"\n{'─' * 60}")
        print(f"  CONSOLIDATION CALL #{self._call_num}")
        print(f"  Episode: {episode.id}")
        print(f"  Prior facts ({len(prior_facts)}):")
        for f in prior_facts:
            print(f"    - [{f.id[:12]}] ({f.fact_type}) {f.content}")
        print(f"  New turns ({len(turns)}):")
        for t in turns:
            print(f"    [{t.role.value}]: {t.content[:80]}")
        print(f"{'─' * 60}")

        actions = await self._inner.reflect_with_consolidation(episode, turns, prior_facts)

        print(f"\n  RETURNED {len(actions)} actions:")
        for a in actions:
            src = f" (source: {a.source_fact_id[:12]})" if a.source_fact_id else ""
            reason = f" reason='{a.reason}'" if a.reason else ""
            print(f"    - {a.action.value:>6s}{src}: {a.content[:70]}{reason}")
        print()
        return actions


async def main() -> None:
    from examples.test_agent.config import OllamaConfig
    from examples.test_agent.llm import OllamaClient, OllamaEmbedder, OllamaReflector

    tmpdir = tempfile.mkdtemp(prefix="gleanr_diag_")
    db_path = Path(tmpdir) / "diag.db"

    client = OllamaClient(OllamaConfig())
    embedder = OllamaEmbedder(client)

    # Use OpenAI-compatible chat endpoint if env vars are set
    chat_client = client
    chat_base_url = os.environ.get("CHAT_BASE_URL")
    chat_model = os.environ.get("CHAT_MODEL")
    if chat_base_url and chat_model:
        from examples.test_agent.config import ChatConfig
        from examples.test_agent.llm import OpenAIChatClient

        chat_client = OpenAIChatClient(ChatConfig(
            base_url=chat_base_url,
            model=chat_model,
            api_key=os.environ.get("CHAT_API_KEY", ""),
        ))
        print(f"Using OpenAI-compatible chat: {chat_base_url} ({chat_model})")

    inner_reflector = OllamaReflector(chat_client, max_facts=8)
    reflector = DiagnosticReflector(inner_reflector)

    SQLiteBackend = get_sqlite_backend()
    storage = SQLiteBackend(db_path)

    config = GleanrConfig(
        auto_detect_markers=True,
        episode_boundary=EpisodeBoundaryConfig(
            max_turns=3,
            max_time_gap_seconds=999999,
            close_on_patterns=[],
        ),
        recall=RecallConfig(default_token_budget=2000),
        reflection=ReflectionConfig(
            enabled=True,
            min_episode_turns=2,
            max_facts_per_episode=8,
            min_confidence=0.5,
            consolidation_similarity_threshold=0.2,
        ),
    )

    gleanr = Gleanr(
        session_id="diag",
        storage=storage,
        embedder=embedder,
        reflector=reflector,
        config=config,
    )
    await gleanr.initialize()

    print("=" * 60)
    print("  DIAGNOSTIC: Tracing every LLM reflection call")
    print("=" * 60)

    for i, (role, content) in enumerate(TURNS, 1):
        print(f"\n  INGEST [{i:2d}] {role}: {content[:60]}...")
        await gleanr.ingest(role, content)

    await gleanr.close_episode()

    print("\n" + "=" * 60)
    print("  FINAL STATE")
    print("=" * 60)

    active = await storage.get_active_facts_by_session("diag")
    print(f"\n  Active facts ({len(active)}):")
    for f in active:
        print(f"    - ({f.fact_type}) {f.content}")

    all_facts = await storage.get_facts_by_session("diag")
    superseded = [f for f in all_facts if f.superseded_by]
    print(f"\n  Superseded facts ({len(superseded)}):")
    for f in superseded:
        print(f"    - ({f.fact_type}) {f.content}  → {f.superseded_by[:20]}")

    await gleanr.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
