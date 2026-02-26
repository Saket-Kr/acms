"""Smoke test: 10 progressive messages, inspect what Gleanr stores.

Simulates the image-generation use case: a user builds and revises
requirements over 10 turns spanning multiple episodes. At the end
we print every fact (active + superseded) so you can see consolidation
in action.

Usage:
    python -m examples.smoke_test_consolidation [--session SESSION_ID]
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Lazy imports so the script can report a clear error if Ollama is down.
# ---------------------------------------------------------------------------

from gleanr import Gleanr, GleanrConfig
from gleanr.core.config import (
    EpisodeBoundaryConfig,
    RecallConfig,
    ReflectionConfig,
)
from gleanr.storage import get_sqlite_backend


# ---------------------------------------------------------------------------
# Conversation: 10 turns that progressively evolve an image prompt.
# ---------------------------------------------------------------------------

TURNS: list[tuple[str, str]] = [
    # --- Episode 1 (turns 1-3): initial requirements ---
    (
        "user",
        "I want to generate a landscape image — rolling green hills, "
        "a few scattered birds in the sky, and warm daytime lighting.",
    ),
    (
        "assistant",
        "Got it. I'll start with: rolling green hills, scattered birds, "
        "warm daytime lighting. Aspect ratio 16:9 by default.",
    ),
    (
        "user",
        "Add a small cottage on the left side of the hills.",
    ),
    # --- Episode 2 (turns 4-6): revisions ---
    (
        "assistant",
        "Updated the prompt to include a small cottage on the left side.",
    ),
    (
        "user",
        "Actually, change the time of day to evening with a golden sunset. "
        "And replace the birds with fireflies.",
    ),
    (
        "assistant",
        "Understood — switching to evening golden sunset and replacing "
        "birds with fireflies.",
    ),
    # --- Episode 3 (turns 7-9): more changes + new constraint ---
    (
        "user",
        "Add a winding river through the middle of the landscape. "
        "Also, the style should be watercolor, not photorealistic.",
    ),
    (
        "assistant",
        "Adding a winding river and switching to watercolor style.",
    ),
    (
        "user",
        "The cottage should be larger and have warm light coming from "
        "the windows. Remove the fireflies, they clash with watercolor.",
    ),
    # --- Turn 10: final state ---
    (
        "assistant",
        "Final prompt: watercolor landscape — rolling green hills, "
        "golden sunset evening, large cottage with warm window light "
        "on the left, winding river through the middle. 16:9.",
    ),
]


def _separator(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


async def main(session_id: str) -> None:
    # --- Setup -----------------------------------------------------------
    try:
        from examples.test_agent.llm import OllamaClient, OllamaEmbedder, OllamaReflector
        from examples.test_agent.config import OllamaConfig
    except ImportError:
        print("ERROR: Could not import Ollama components from examples/test_agent.")
        print("Make sure you're running from the repo root.")
        sys.exit(1)

    tmpdir = tempfile.mkdtemp(prefix="gleanr_smoke_")
    db_path = Path(tmpdir) / f"{session_id}.db"

    ollama_config = OllamaConfig()
    client = OllamaClient(ollama_config)
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

    reflector = OllamaReflector(chat_client)

    SQLiteBackend = get_sqlite_backend()
    storage = SQLiteBackend(db_path)

    config = GleanrConfig(
        auto_detect_markers=True,
        episode_boundary=EpisodeBoundaryConfig(
            max_turns=3,             # 3 turns per episode → ~3 episodes + tail
            max_time_gap_seconds=999999,  # effectively disabled for smoke test
            close_on_patterns=[],       # disabled — we want predictable boundaries
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
        session_id=session_id,
        storage=storage,
        embedder=embedder,
        reflector=reflector,
        config=config,
    )
    await gleanr.initialize()

    _separator("Gleanr Smoke Test — Consolidating Reflection")
    print(f"Session:  {session_id}")
    print(f"DB:       {db_path}")
    print(f"Episodes: max_turns=3 (auto boundary)")
    print(f"Turns:    {len(TURNS)}")

    # --- Ingest 10 turns -------------------------------------------------
    for i, (role, content) in enumerate(TURNS, 1):
        print(f"\n  [{i:2d}] {role:>9s}: {content[:70]}{'...' if len(content) > 70 else ''}")
        await gleanr.ingest(role, content)

    # Close the final episode so reflection runs on the last batch.
    await gleanr.close_episode()

    # --- Inspect storage -------------------------------------------------
    _separator("ALL FACTS (including superseded)")

    all_facts = await storage.get_facts_by_session(session_id)
    if not all_facts:
        print("  (no facts extracted — LLM may not have returned valid JSON)")
    else:
        for f in all_facts:
            status = "SUPERSEDED" if f.superseded_by else "ACTIVE"
            print(f"  [{status:10s}] {f.id[:12]}  ({f.fact_type or 'unknown':>12s})  {f.content}")
            if f.superseded_by:
                print(f"               └── superseded_by: {f.superseded_by[:20]}...")
            if f.supersedes:
                print(f"               └── supersedes: {f.supersedes}")

    _separator("ACTIVE FACTS (what recall would use)")

    active_facts = await storage.get_active_facts_by_session(session_id)
    if not active_facts:
        print("  (no active facts)")
    else:
        for i, f in enumerate(active_facts, 1):
            print(f"  {i}. [{f.fact_type or 'unknown':>12s}]  {f.content}")

    _separator("STATS")

    stats = await storage.get_session_stats(session_id)
    print(f"  Total turns:    {stats['total_turns']}")
    print(f"  Total episodes: {stats['total_episodes']}")
    print(f"  Total facts:    {stats['total_facts']} (all)")
    print(f"  Active facts:   {len(active_facts)}")
    superseded = len(all_facts) - len(active_facts)
    print(f"  Superseded:     {superseded}")

    # --- Recall test -----------------------------------------------------
    _separator("RECALL (simulating 'what is the current image prompt?')")

    items = await gleanr.recall(query="current image prompt requirements")
    total_tokens = sum(item.token_count for item in items)
    print(f"  Budget used:    {total_tokens} tokens")
    print(f"  Items returned: {len(items)}")
    for item in items:
        label = item.source
        preview = item.content[:80].replace("\n", " ")
        print(f"    [{label:>8s}]  {preview}{'...' if len(item.content) > 80 else ''}")

    # --- Cleanup ---------------------------------------------------------
    await gleanr.close()
    await client.close()

    _separator("DONE")
    print(f"  Database kept at: {db_path}")
    print(f"  Inspect with: sqlite3 {db_path} 'SELECT id, content, superseded_by FROM facts;'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gleanr consolidation smoke test")
    parser.add_argument("--session", default="smoke_test", help="Session ID")
    args = parser.parse_args()

    asyncio.run(main(args.session))
