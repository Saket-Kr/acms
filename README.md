# ACMS — Agent Context Management System

**Session-scoped memory for AI agents that actually remembers.**

ACMS is a Python SDK that gives your AI agents persistent, structured memory across conversations. Unlike RAG systems that retrieve external knowledge, ACMS manages the agent's *internal state*—what it decided, what constraints it discovered, what failed, and what the user prefers.

```python
from acms import ACMS

# Initialize with your session
acms = ACMS(session_id="user_123", storage=storage, embedder=embedder)
await acms.initialize()

# Ingest conversation turns
await acms.ingest("user", "Let's use PostgreSQL for the database")
await acms.ingest("assistant", "Decision: We'll use PostgreSQL for its robust JSON support")

# Recall relevant context (token-budgeted)
context = await acms.recall("What database are we using?", token_budget=2000)
# Returns: [ContextItem(content="Decision: We'll use PostgreSQL...", markers=["decision"], ...)]
```

## Why ACMS?

Current LLM applications treat agent memory as a search problem. But **agent memory is not knowledge retrieval**:

| Aspect | Knowledge Retrieval (RAG) | Agent Memory (ACMS) |
|--------|--------------------------|---------------------|
| Scope | External corpus | Internal session state |
| Lifespan | Persistent | Session-bound with decay |
| Trigger | Explicit queries | Every turn, automatically |
| Content | Documents, facts | Decisions, constraints, outcomes |

After 30-40 turns, agents without proper memory:
- Forget decisions made earlier ("Didn't we decide to use PostgreSQL?")
- Repeat failed approaches
- Lose track of user preferences
- Contradict themselves

ACMS solves this by automatically tracking what matters and recalling it when relevant.

## Key Features

- **Automatic marker detection** — Identifies decisions, constraints, failures, and goals in conversation
- **Token-budgeted recall** — Always fits in your context window
- **Episode management** — Groups related turns, triggers reflection on close
- **LLM reflection with consolidation** — Extracts durable facts and keeps them accurate as requirements evolve
- **Fact supersession** — When facts change, old versions are superseded (not deleted), maintaining an audit trail
- **Deduplication** — Embedding-based duplicate detection prevents redundant facts
- **Contradiction detection** — Consolidation prompt identifies and resolves conflicting facts
- **Observability** — Built-in reflection tracing for debugging and monitoring
- **Pluggable storage** — SQLite for persistence, in-memory for testing
- **Provider agnostic** — Works with OpenAI, Anthropic, Ollama, or any embedder
- **Evaluation harness** — Automated testing across 6 scenarios with latency profiling

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/acms.git
cd acms

# Install with your preferred extras
pip install -e ".[sqlite]"           # SQLite storage backend
pip install -e ".[openai]"           # OpenAI embeddings
pip install -e ".[anthropic]"        # Anthropic embeddings
pip install -e ".[examples]"         # Test agent dependencies
pip install -e ".[dev]"              # Development tools
```

## Quick Start

### 1. Basic Usage

```python
import asyncio
from acms import ACMS, ACMSConfig
from acms.storage import InMemoryBackend

async def main():
    # Setup
    storage = InMemoryBackend()

    acms = ACMS(
        session_id="demo",
        storage=storage,
        embedder=your_embedder,  # See Providers section
    )
    await acms.initialize()

    # Conversation
    await acms.ingest("user", "I need help building a REST API")
    await acms.ingest("assistant", "I'll help you build a REST API. Decision: We'll use FastAPI for its automatic OpenAPI docs.")

    # Later in conversation...
    context = await acms.recall("What framework are we using?")
    print(context[0].content)  # "Decision: We'll use FastAPI..."

    await acms.close()

asyncio.run(main())
```

### 2. With SQLite Persistence

```python
from acms.storage import get_sqlite_backend

SQLiteBackend = get_sqlite_backend()
storage = SQLiteBackend("./agent_memory.db")

acms = ACMS(
    session_id="user_123",
    storage=storage,
    embedder=embedder,
)
```

Sessions persist across restarts. Resume anytime with the same `session_id`.

### 3. With Reflection and Consolidation

```python
from acms import ACMSConfig
from acms.core.config import ReflectionConfig

config = ACMSConfig(
    reflection=ReflectionConfig(
        enabled=True,
        min_episode_turns=3,
        max_facts_per_episode=5,
        dedup_similarity_threshold=0.95,  # Prevent duplicate facts
    )
)

acms = ACMS(
    session_id="demo",
    storage=storage,
    embedder=embedder,
    reflector=your_reflector,  # LLM-based fact extractor
    config=config,
)
```

When episodes close, ACMS reflects on the conversation and extracts durable facts. On subsequent episodes, **consolidation** kicks in — existing facts are sent alongside new turns, and the reflector returns actions (keep/update/add/remove) to keep facts accurate:

```
Episode 1 → Reflects → "Database is PostgreSQL", "API style is REST"
Episode 2 → User says "switch to MySQL"
         → Consolidates → UPDATE "Database is MySQL" (supersedes PostgreSQL fact)
                        → KEEP "API style is REST"
```

The old "PostgreSQL" fact is preserved with a `superseded_by` pointer for audit trail, but only the current "MySQL" fact appears in recall results.

**Short episode carry-forward**: If an episode has fewer turns than `min_episode_turns`, those turns are buffered and included in the next episode's reflection. No data is ever silently dropped.

## Memory Model

ACMS uses a three-level memory hierarchy:

### L0: Raw Turns
Every message in the conversation. Short-lived, used for immediate context.

### L1: Episodes
Groups of related turns around a goal or task. Automatically detected via:
- Turn count thresholds
- Time gaps between messages
- Topic boundaries
- Tool result patterns

### L2: Semantic Facts
Extracted from episodes via LLM reflection. Captures:
- **Decisions** — Choices made and their rationale
- **Constraints** — Limitations discovered
- **Failures** — What didn't work (to avoid repeating)
- **Goals** — User objectives

### 4. Observability (Reflection Tracing)

```python
from acms import ACMS, ReflectionTrace

def on_trace(trace: ReflectionTrace):
    print(f"Reflection on episode {trace.episode_id} ({trace.mode})")
    print(f"  Input: {trace.input_turn_count} turns")
    if trace.prior_facts:
        print(f"  Prior facts: {len(trace.prior_facts)}")
    print(f"  Saved: {len(trace.saved_facts)} facts")
    print(f"  Superseded: {len(trace.superseded_facts)} facts")
    print(f"  Elapsed: {trace.elapsed_ms}ms")

acms = ACMS(session_id="demo", storage=storage, embedder=embedder, reflector=reflector)
acms.set_trace_callback(on_trace)
await acms.initialize()
```

Traces capture the full reflection pipeline: input turns, prior facts, scoped facts, raw LLM output (actions or facts), saved facts, and superseded facts. Use `trace.to_dict()` for JSON serialization.

## Markers

ACMS uses markers to signal importance. They're auto-detected or manually specified:

```python
# Auto-detected from content
await acms.ingest("assistant", "Decision: We'll use React for the frontend")
# Marker "decision" auto-detected

# Manually specified
await acms.ingest("user", "Important: Never use eval() in this codebase", markers=["constraint"])
```

Built-in marker types:
- `decision` — Choices made
- `constraint` — Limitations/requirements
- `failure` — Things that didn't work
- `goal` — Objectives to achieve
- `custom:*` — Your own markers

Marked content gets priority in recall and influences fact extraction.

## Recall

Recall is automatic and token-budgeted:

```python
context = await acms.recall(
    query="authentication",
    token_budget=2000,  # Max tokens to return
)

for item in context:
    print(f"[{item.role}] {item.content}")
    print(f"  Score: {item.score}, Markers: {item.markers}")
```

Recall prioritizes:
1. High-relevance semantic matches
2. Marked content (decisions, constraints, etc.)
3. Current episode turns
4. L2 facts from past episodes

## Providers

### Embeddings

**OpenAI:**
```python
from acms.providers.openai import OpenAIEmbedder
embedder = OpenAIEmbedder(api_key="sk-...")
```

**Anthropic:**
```python
from acms.providers.anthropic import AnthropicEmbedder
embedder = AnthropicEmbedder(api_key="sk-ant-...")
```

**Ollama (local):**
```python
# See examples/test_agent/llm.py for implementation
embedder = OllamaEmbedder(client)
```

**Custom:**
```python
from acms.providers import Embedder

class MyEmbedder(Embedder):
    async def embed(self, texts: list[str]) -> list[list[float]]:
        # Your implementation
        ...

    @property
    def dimension(self) -> int:
        return 384
```

### Reflection

Reflection requires an LLM to extract facts:

```python
from acms.providers.openai import OpenAIReflector
reflector = OpenAIReflector(api_key="sk-...")
```

Or implement your own:
```python
from acms.providers import Reflector

class MyReflector(Reflector):
    async def reflect(self, episode, turns) -> list[Fact]:
        # Call your LLM to extract facts
        ...
```

## Test Agent

ACMS includes a fully functional test agent powered by Ollama for interactive experimentation.

### Setup

```bash
# Install example dependencies
pip install -e ".[examples]"

# Start Ollama (if not running)
ollama serve

# Pull required models
ollama pull mistral:7b-instruct
ollama pull nomic-embed-text
```

### Run

```bash
# Start a new session
python -m examples.test_agent.run --session my_test

# Resume an existing session
python -m examples.test_agent.run --session my_test

# Debug mode (shows recall items and ACMS timings)
python -m examples.test_agent.run --session my_test --debug
```

Commands:
- `/stats` — Show session statistics (turns, episodes, facts)
- `/recall <query>` — Test recall directly
- `/episode` — Close current episode (triggers reflection)
- `/debug` — Toggle debug mode
- `/help` — Show all commands
- `/quit` — Exit

## Evaluation Harness

ACMS ships with an automated evaluation framework for measuring memory accuracy and latency across multi-turn conversations.

### Quick Test

```bash
# Sanity check — 1 iteration, 10 turns
python -m examples.evaluation.run --quick
```

### Full Evaluation

```bash
# Default: 80 sessions across 8 turn counts (10-80), decision_tracking scenario
python -m examples.evaluation.run

# Test consolidation accuracy with the progressive_requirements scenario
python -m examples.evaluation.run --scenario progressive_requirements --quick

# Custom configuration
python -m examples.evaluation.run \
    --scenario progressive_requirements \
    --turns 10,20,30,40 \
    --iterations 5 \
    --max-concurrent 3 \
    --verbose

# List all scenarios
python -m examples.evaluation.run --list-scenarios
```

### Available Scenarios

| Scenario | Tests |
|----------|-------|
| `decision_tracking` | Recall of architectural decisions over time |
| `constraint_awareness` | Recall of constraints when relevant |
| `failure_memory` | Avoiding repeated failures |
| `multi_fact_tracking` | Independent recall of multiple facts |
| `goal_tracking` | Persistence of goals and objectives |
| `progressive_requirements` | Fact updates via consolidation — probes check updated facts, not originals |

Reports are saved as JSON and Markdown in `./evaluation_output/`.

## Configuration

```python
from acms import ACMSConfig
from acms.core.config import EpisodeBoundaryConfig, RecallConfig, ReflectionConfig

config = ACMSConfig(
    auto_detect_markers=True,  # Auto-detect decision/constraint/etc.

    episode_boundary=EpisodeBoundaryConfig(
        max_turns=20,              # Close episode after N turns
        max_time_gap_seconds=1800, # Close after 30min gap
        close_on_tool_result=True, # Close after tool completion
    ),

    recall=RecallConfig(
        default_token_budget=2000,
        current_episode_budget_pct=0.5,  # 50% budget for current episode
    ),

    reflection=ReflectionConfig(
        enabled=True,
        min_episode_turns=3,
        max_facts_per_episode=5,
        consolidation_similarity_threshold=0.3,  # Scoping threshold for prior facts
        dedup_similarity_threshold=0.95,          # Duplicate detection threshold
    ),
)
```

## API Reference

### ACMS Class

```python
class ACMS:
    async def initialize() -> None
    async def ingest(role: str, content: str, markers: list[str] = None) -> Turn
    async def recall(query: str, token_budget: int = None) -> list[ContextItem]
    async def close_episode(reason: str = "manual") -> str | None
    async def get_session_stats() -> SessionStats
    async def close() -> None
```

### Models

```python
@dataclass
class Turn:
    id: str
    session_id: str
    episode_id: str
    role: Role
    content: str
    markers: list[str]
    token_count: int
    created_at: datetime

@dataclass
class ContextItem:
    content: str
    role: Role
    markers: list[str]
    score: float
    token_count: int
    source_type: str  # "turn", "fact"
    source_id: str
```

## Design Philosophy

ACMS follows these principles:

1. **Store conclusions, not evidence** — Don't store raw RAG results or chain-of-thought. Store what was decided and why.

2. **Memory is always-on** — Unlike tools that are invoked, memory recall happens every turn automatically.

3. **Token budgets are hard limits** — Never exceed the budget. Gracefully degrade by dropping lower-priority items.

4. **Episodes are mandatory** — All turns belong to episodes. This enables reflection and provides natural grouping.

5. **Reflection is optional but valuable** — The system works without it (L1 episodes remain functional), but L2 facts dramatically improve long-term recall.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=acms

# Type checking
mypy acms
```

## Roadmap

- [x] Consolidating reflection — Facts update as requirements change
- [x] Deduplication — Embedding-based duplicate prevention
- [x] Contradiction detection — Resolve conflicting facts during consolidation
- [x] Observability — Reflection tracing with full input/output visibility
- [x] Evaluation harness — Automated accuracy and latency testing
- [ ] L3 Themes — Cross-episode patterns and user profiles
- [ ] Async reflection queue — Non-blocking fact extraction
- [ ] Multi-agent support — Shared memory across agents
- [ ] Cloud storage backends — Redis, PostgreSQL

## License

MIT License — See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read the design docs in `PLAN.md` to understand the architecture before submitting PRs.

---

**ACMS** — Because agents should remember what matters.
