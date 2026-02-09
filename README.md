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
- **LLM reflection** — Extracts durable facts from episodes (optional)
- **Pluggable storage** — SQLite for persistence, in-memory for testing
- **Provider agnostic** — Works with OpenAI, Anthropic, Ollama, or any embedder

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

### 3. With Reflection (L2 Facts)

```python
from acms import ACMSConfig
from acms.core.config import ReflectionConfig

config = ACMSConfig(
    reflection=ReflectionConfig(
        enabled=True,
        min_episode_turns=3,  # Reflect after 3+ turn episodes
        max_facts_per_episode=5,
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

When episodes close, the reflector extracts durable facts like:
- "User prefers PostgreSQL over MySQL"
- "The /api/users endpoint must support pagination"
- "JWT auth failed due to clock skew; switched to session tokens"

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

ACMS includes a test agent for interactive experimentation:

```bash
# Install example dependencies
pip install -e ".[examples]"

# Start Ollama (if not running)
ollama serve

# Pull required models
ollama pull mistral:7b-instruct
ollama pull nomic-embed-text

# Run the test agent
python -m examples.test_agent.run --session my_test
```

Commands:
- `/stats` — Show session statistics
- `/recall <query>` — Test recall directly
- `/episode` — Close current episode
- `/debug` — Toggle debug mode
- `/help` — Show all commands
- `/quit` — Exit

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

- [ ] L3 Themes — Cross-episode patterns and user profiles
- [ ] Async reflection queue — Non-blocking fact extraction
- [ ] Memory compaction — Merge redundant facts
- [ ] Multi-agent support — Shared memory across agents
- [ ] Cloud storage backends — Redis, PostgreSQL

## License

MIT License — See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read the design docs in `PLAN.md` to understand the architecture before submitting PRs.

---

**ACMS** — Because agents should remember what matters.
