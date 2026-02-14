# ACMS Implementation Plan

## Overview

Build a production-grade Python SDK for session-scoped agent context management. This replaces raw chat history accumulation with intelligent, token-budgeted context assembly.

**Target:** OSS library that senior engineers would confidently use in production.

---

## Design Principles

1. **Extensibility over configuration** - Plugin architecture, not flags
2. **Fail gracefully** - Degrade, don't crash
3. **Zero magic** - Explicit is better than implicit
4. **Minimal dependencies** - Core has no required external deps
5. **Test everything** - High coverage, property-based tests where appropriate

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage | Pluggable backends | SQLite, ChromaDB, Postgres, Redis, custom |
| LLM/Embeddings | Provider abstraction | HTTP, OpenAI SDK, Anthropic SDK, custom |
| Token counting | Pluggable, default heuristic | `len(text) // 4` default, tiktoken optional |
| API style | Async-first | Native async, fits modern agent frameworks |
| Error handling | Custom exception hierarchy | Typed errors, retryable vs fatal |
| Logging | Structured logging | JSON-compatible, correlation IDs |
| Embedding timing | Await during ingest | Correctness over latency; extensible for fire-and-forget later |
| Session model | One ACMS instance = one session | Simpler, cleaner isolation |
| Caching | Built-in LRU cache | In-memory cache in front of storage for hot data |

**Core Principle:** Correctness > Latency. The system must be useful and reliable first.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ACMS SDK                                │
├─────────────────────────────────────────────────────────────────┤
│  Public API                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ACMS(session_id, storage, embedder, config)             │   │
│  │ ├── await ingest(role, content, metadata) → TurnID      │   │
│  │ ├── await recall(query, token_budget) → ContextItems    │   │
│  │ ├── await close_episode(reason) → EpisodeID             │   │
│  │ └── await get_session_stats() → SessionStats            │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  Memory Levels                                                  │
│  ├── L0: Raw turns (TTL-based eviction)                        │
│  ├── L1: Episodes (mandatory, rule-based grouping)             │
│  └── L2: Semantic facts (optional, reflector-generated)        │
├─────────────────────────────────────────────────────────────────┤
│  Core Services                                                  │
│  ├── Ingestion Pipeline   (turn → validate → store → embed)    │
│  ├── Recall Pipeline      (query → search → rank → budget)     │
│  ├── Episode Manager      (boundary detection, lifecycle)      │
│  └── Reflection Runner    (async, optional, LLM-assisted)      │
├─────────────────────────────────────────────────────────────────┤
│  Provider Layer (Pluggable)                                     │
│  ├── Embedder: HTTP | OpenAI | Anthropic | Custom              │
│  ├── Reflector: HTTP | OpenAI | Anthropic | Custom             │
│  └── TokenCounter: Heuristic | Tiktoken | Custom               │
├─────────────────────────────────────────────────────────────────┤
│  Storage Layer (Pluggable)                                      │
│  ├── InMemory (testing/dev)                                    │
│  ├── SQLite + sqlite-vec (local production)                    │
│  ├── ChromaDB (vector-first)                                   │
│  └── PostgreSQL + pgvector (scaled production)                 │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure                                                 │
│  ├── Error handling (exception hierarchy, retries)             │
│  ├── Observability (structured logging, metrics hooks)         │
│  └── Validation (pydantic models, runtime checks)              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

```
acms/
├── __init__.py                 # Public API: ACMS, exceptions, types
├── py.typed                    # PEP 561 marker
│
├── core/
│   ├── __init__.py
│   ├── session.py              # ACMS main class
│   ├── config.py               # ACMSConfig with validation
│   └── context.py              # ContextItem, ContextAssembly
│
├── models/
│   ├── __init__.py
│   ├── turn.py                 # Turn dataclass
│   ├── episode.py              # Episode dataclass
│   ├── fact.py                 # Fact dataclass (L2)
│   └── types.py                # Enums, TypedDicts, type aliases
│
├── memory/
│   ├── __init__.py
│   ├── ingestion.py            # IngestionPipeline
│   ├── recall.py               # RecallPipeline
│   ├── episode_manager.py      # EpisodeManager (boundary detection)
│   └── reflection.py           # ReflectionRunner (async)
│
├── storage/
│   ├── __init__.py
│   ├── base.py                 # StorageBackend ABC
│   ├── memory.py               # InMemoryBackend
│   ├── sqlite.py               # SQLiteBackend
│   ├── chroma.py               # ChromaBackend (optional dep)
│   └── postgres.py             # PostgresBackend (optional dep)
│
├── providers/
│   ├── __init__.py
│   ├── base.py                 # Embedder, Reflector, TokenCounter protocols
│   ├── http.py                 # HTTPEmbedder, HTTPReflector
│   ├── openai.py               # OpenAIEmbedder, OpenAIReflector (optional dep)
│   ├── anthropic.py            # AnthropicReflector (optional dep)
│   └── registry.py             # Provider registration & discovery
│
├── errors/
│   ├── __init__.py
│   └── exceptions.py           # Full exception hierarchy
│
├── cache/
│   ├── __init__.py
│   ├── lru.py                  # LRU cache implementation
│   └── config.py               # CacheConfig
│
├── utils/
│   ├── __init__.py
│   ├── tokens.py               # Token counting implementations
│   ├── retry.py                # Retry with exponential backoff
│   ├── validation.py           # Input validation helpers
│   ├── serialization.py        # JSON/dict serialization
│   ├── ids.py                  # ID generation (UUIDs, etc.)
│   └── logging.py              # Structured logging setup
│
└── contrib/                    # Community/optional extensions
    ├── __init__.py
    └── langchain.py            # LangChain integration (future)

tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── test_models.py
│   ├── test_episode_manager.py
│   ├── test_ingestion.py
│   ├── test_recall.py
│   └── test_providers.py
├── integration/
│   ├── test_full_cycle.py
│   ├── test_sqlite_backend.py
│   └── test_long_conversation.py
└── benchmarks/
    ├── bench_ingest.py
    └── bench_recall.py
```

---

## Core Interfaces

### 1. ACMS (Main Entry Point)

```python
class ACMS:
    """Session-scoped context manager for agents."""

    def __init__(
        self,
        session_id: str,
        storage: StorageBackend,
        embedder: Embedder,
        *,
        reflector: Reflector | None = None,
        token_counter: TokenCounter | None = None,
        config: ACMSConfig | None = None,
    ) -> None: ...

    async def ingest(
        self,
        role: Role,  # "user" | "assistant" | "tool"
        content: str,
        *,
        actor_id: str | None = None,
        markers: list[str] | None = None,  # ["decision", "constraint", "failure", "goal"]
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Ingest a turn into memory.

        Args:
            role: Who produced this turn (user, assistant, tool)
            content: The turn content
            actor_id: Optional identifier for the actor
            markers: Optional importance markers (decision, constraint, failure, goal, custom:*)
            metadata: Optional arbitrary metadata

        Returns turn_id. Raises ValidationError on invalid input.
        Embedding happens synchronously (correctness > latency).
        """

    async def recall(
        self,
        query: str,
        *,
        token_budget: int = 4000,
        include_current_episode: bool = True,
        min_relevance: float = 0.0,
    ) -> list[ContextItem]:
        """
        Recall relevant context for a query.

        Returns ordered list of context items within token budget.
        Target latency: <50ms (excluding network I/O).
        """

    async def close_episode(
        self,
        reason: str = "manual",
    ) -> str:
        """Manually close the current episode. Returns episode_id."""

    async def get_session_stats(self) -> SessionStats:
        """Get statistics about the current session."""

    async def close(self) -> None:
        """Clean up resources. Flush pending writes."""
```

### 2. Storage Backend

```python
class StorageBackend(ABC):
    """Abstract base for all storage backends."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize storage (create tables, etc.)."""

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""

    # Turn operations
    @abstractmethod
    async def save_turn(self, turn: Turn) -> None: ...

    @abstractmethod
    async def get_turn(self, turn_id: str) -> Turn | None: ...

    @abstractmethod
    async def get_turns_by_episode(self, episode_id: str) -> list[Turn]: ...

    # Episode operations
    @abstractmethod
    async def save_episode(self, episode: Episode) -> None: ...

    @abstractmethod
    async def get_episode(self, episode_id: str) -> Episode | None: ...

    @abstractmethod
    async def get_episodes(
        self,
        session_id: str,
        *,
        limit: int = 100,
        status: EpisodeStatus | None = None,
    ) -> list[Episode]: ...

    # Vector operations
    @abstractmethod
    async def save_embedding(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None: ...

    @abstractmethod
    async def vector_search(
        self,
        embedding: list[float],
        *,
        k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]: ...

    # Fact operations (L2)
    @abstractmethod
    async def save_fact(self, fact: Fact) -> None: ...

    @abstractmethod
    async def get_facts_by_session(self, session_id: str) -> list[Fact]: ...
```

### 3. Provider Protocols

```python
class Embedder(Protocol):
    """Protocol for embedding providers."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts. Raises ProviderError on failure."""
        ...

    @property
    def dimension(self) -> int:
        """Embedding dimension (e.g., 1536 for text-embedding-3-small)."""
        ...


class Reflector(Protocol):
    """Protocol for reflection providers (LLM-assisted fact extraction)."""

    async def reflect(self, episode: Episode, turns: list[Turn]) -> list[Fact]:
        """Extract semantic facts from an episode. Raises ProviderError on failure."""
        ...


class TokenCounter(Protocol):
    """Protocol for token counting."""

    def count(self, text: str) -> int:
        """Count tokens in text."""
        ...
```

### 4. HTTP Provider Example

```python
class HTTPEmbedder:
    """Embedder using raw HTTP calls to OpenAI-compatible endpoint."""

    def __init__(
        self,
        base_url: str,
        model: str = "text-embedding-3-small",
        *,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    @property
    def dimension(self) -> int: ...
```

### 5. OpenAI SDK Provider Example

```python
class OpenAIEmbedder:
    """Embedder using OpenAI Python SDK."""

    def __init__(
        self,
        client: AsyncOpenAI,  # User provides configured client
        model: str = "text-embedding-3-small",
    ) -> None: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    @property
    def dimension(self) -> int: ...
```

---

## Exception Hierarchy

```python
class ACMSError(Exception):
    """Base exception for all ACMS errors."""
    pass


class ConfigurationError(ACMSError):
    """Invalid configuration."""
    pass


class ValidationError(ACMSError):
    """Input validation failed."""
    pass


class StorageError(ACMSError):
    """Storage operation failed."""
    pass


class ProviderError(ACMSError):
    """Provider operation failed (embedder, reflector, etc.)."""

    def __init__(
        self,
        message: str,
        *,
        provider: str,
        retryable: bool = False,
        cause: Exception | None = None,
    ) -> None: ...


class TokenBudgetExceededError(ACMSError):
    """Token budget cannot be satisfied."""
    pass


class SessionNotFoundError(ACMSError):
    """Session does not exist."""
    pass


class EpisodeNotFoundError(ACMSError):
    """Episode does not exist."""
    pass
```

---

## Episode Boundary Rules

```python
@dataclass
class EpisodeBoundaryConfig:
    """Configuration for automatic episode boundaries."""

    max_turns: int = 6
    """Close episode after this many turns."""

    max_time_gap_seconds: int = 1800  # 30 minutes
    """Close episode if gap between turns exceeds this."""

    close_on_tool_result: bool = True
    """Close episode after a tool result."""

    close_on_patterns: list[str] = field(default_factory=lambda: [
        r"(?i)\b(done|finished|complete|thanks|thank you)\b",
    ])
    """Regex patterns that trigger episode closure."""
```

---

## Markers (Lightweight Importance Signals)

Markers provide correctness benefits without requiring full LLM reflection. Critical turns are prioritized in recall regardless of when they occurred.

### Marker Types (Enum)

```python
from enum import Enum

class MarkerType(str, Enum):
    """Built-in marker types with default boost weights."""
    DECISION = "decision"      # Choices made - maintain consistency
    CONSTRAINT = "constraint"  # Limitations/requirements - always relevant
    FAILURE = "failure"        # What didn't work - prevent repeated attempts
    GOAL = "goal"              # Task objectives - anchor for relevance
```

### Default Boost Weights

| Marker | Default Boost | Rationale |
|--------|---------------|-----------|
| `constraint` | 0.4 | Constraints are critical - violating them = failure |
| `decision` | 0.3 | Decisions drive consistency |
| `goal` | 0.3 | Goals anchor relevance |
| `failure` | 0.2 | Failures prevent waste but less critical |
| `custom:*` | 0.2 | Conservative default for custom markers |

Weights are configurable via `ACMSConfig.marker_weights`.

### Explicit Marking

```python
await acms.ingest(
    role="assistant",
    content="Using PostgreSQL for the database",
    markers=[MarkerType.DECISION],  # Type-safe
)

# Custom markers also allowed
await acms.ingest(
    role="user",
    content="Remember this",
    markers=["custom:important"],
)
```

### Auto-Detection (Default: Enabled)

ACMS auto-detects markers from content patterns. Can be disabled via `ACMSConfig.auto_detect_markers = False`.

| Pattern | Detected Marker |
|---------|-----------------|
| `Decision:`, `Decided:`, `Choosing:`, `Selected:` | `decision` |
| `Constraint:`, `Requirement:`, `Must:`, `Cannot:`, `Budget:`, `Limit:` | `constraint` |
| `Failed:`, `Error:`, `Didn't work:`, `Tried but:` | `failure` |
| `Goal:`, `Objective:`, `Task:`, `Need to:` | `goal` |

**Pattern matching rules:**
- Case-insensitive
- Must appear at start of content or after newline
- Explicit markers override auto-detected ones

---

## Recall Algorithm

**Key design:** No recency scoring. Current episode provides implicit recency; past turns compete on relevance + markers only.

```
┌─────────────────────────────────────────────────────────────┐
│                    Recall Pipeline                          │
├─────────────────────────────────────────────────────────────┤
│ 1. Embed query                                              │
│    └── embedder.embed([query])                              │
├─────────────────────────────────────────────────────────────┤
│ 2. Gather candidates (4 sources)                            │
│    ├── [ALWAYS] Current episode turns (implicit recency)    │
│    ├── [PRIORITY] Marked turns from past episodes           │
│    ├── [IF ENABLED] L2 facts                                │
│    └── [SEARCH] Vector search on past unmarked turns        │
├─────────────────────────────────────────────────────────────┤
│ 3. Score candidates (NO RECENCY)                            │
│                                                             │
│    For past turns:                                          │
│    score = relevance + marker_boost                         │
│                                                             │
│    Where:                                                   │
│    - relevance = cosine_similarity(query_emb, turn_emb)     │
│    - marker_boost = sum(weights[marker] for marker in turn) │
│                                                             │
│    Current episode: not scored, always included first       │
├─────────────────────────────────────────────────────────────┤
│ 4. Budget allocation                                        │
│                                                             │
│    Step 1: Reserve for current episode                      │
│            (up to current_episode_budget_pct, default 40%)  │
│                                                             │
│    Step 2: Include marked turns by score                    │
│            (constrained by remaining budget)                │
│                                                             │
│    Step 3: Fill remaining with L2 facts + vector results    │
│            (by score until budget exhausted)                │
├─────────────────────────────────────────────────────────────┤
│ 5. Handle edge cases                                        │
│    ├── Current episode > budget: truncate oldest turns,     │
│    │   keep most recent + any marked turns in episode       │
│    ├── No relevant results: return current episode only     │
│    └── Marked turns exceed budget: include by score,        │
│        log warning about overflow                           │
├─────────────────────────────────────────────────────────────┤
│ 6. Assemble context                                         │
│    Order: L2 facts → marked past turns → current episode    │
│    (chronological within each group)                        │
└─────────────────────────────────────────────────────────────┘
```

### Why No Recency?

| Concern | How ACMS Handles It |
|---------|---------------------|
| Recent context matters | Current episode always included first |
| Old decisions still relevant | Markers boost old important turns |
| Don't repeat old failures | Failure markers surface old mistakes |
| Semantic drift over time | Vector search finds relevant old content |

### What Agents Need vs. How ACMS Provides It

| Agent Need | ACMS Feature | Confidence |
|------------|--------------|------------|
| Task continuity | Current episode + goal markers | High |
| Decision history | Decision markers + L2 facts | High |
| Constraint awareness | Constraint markers + L2 facts | High |
| Failure memory | Failure markers + L2 facts | High |
| Current state | Current episode always included | High |

---

## Cache Layer

Built-in LRU cache sits between ACMS and storage backend for hot data access.

```python
@dataclass
class CacheConfig:
    """Configuration for the in-memory cache."""

    enabled: bool = True
    max_turns: int = 1000
    """Maximum number of turns to cache."""

    max_episodes: int = 100
    """Maximum number of episodes to cache."""

    max_embeddings: int = 1000
    """Maximum number of embeddings to cache."""

    ttl_seconds: int | None = None
    """Optional TTL for cache entries. None = no expiry."""
```

### Cache Behavior

- **Reads**: Check cache first, fall through to storage on miss
- **Writes**: Write-through (write to both cache and storage)
- **Invalidation**: LRU eviction when limits reached
- **Session isolation**: Cache is per-session (one ACMS = one session)

### What Gets Cached

| Data | Cached | Rationale |
|------|--------|-----------|
| Current episode turns | Yes | Hot path for recall |
| Recent embeddings | Yes | Avoid re-computing |
| Marked turns | Yes | High priority in recall |
| Old episodes | No | Accessed via vector search |
| L2 facts | Yes | Small, frequently accessed |

---

## Retry & Resilience

```python
@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 0.5
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
    )


async def with_retry(
    fn: Callable[..., Awaitable[T]],
    config: RetryConfig,
    *,
    on_retry: Callable[[int, Exception], None] | None = None,
) -> T:
    """Execute function with retry logic."""
```

---

## Implementation Phases

### Phase 1: Foundation (~2-3 days)
**Goal:** Project skeleton, core types, basic abstractions

- [ ] Project setup
  - [ ] `pyproject.toml` with optional dependencies groups
  - [ ] pytest, ruff, mypy configuration
  - [ ] GitHub Actions CI/CD skeleton
- [ ] Core models
  - [ ] `Turn`, `Episode`, `Fact` dataclasses
  - [ ] `ContextItem`, `SessionStats` types
  - [ ] `Role`, `EpisodeStatus` enums
- [ ] Exception hierarchy
- [ ] `ACMSConfig` with validation
- [ ] Protocol definitions (`Embedder`, `Reflector`, `TokenCounter`)
- [ ] `InMemoryBackend` for testing

**Verification:** Unit tests pass, types check

### Phase 2: Core Pipeline (~3-4 days)
**Goal:** Working ingest/recall with in-memory backend

- [ ] `ACMS` class skeleton
- [ ] `IngestionPipeline`
  - [ ] Turn creation and validation
  - [ ] Episode assignment
  - [ ] Background embedding task
- [ ] `EpisodeManager`
  - [ ] Boundary detection rules
  - [ ] Episode lifecycle (open → closed)
- [ ] `RecallPipeline`
  - [ ] Basic recency-based recall (no vectors)
  - [ ] Token budgeting

**Verification:** Integration test - 20 turn conversation with ingest/recall

### Phase 3: Semantic Recall (~2-3 days)
**Goal:** Vector-based recall with scoring

- [ ] Vector search integration in recall
- [ ] Scoring algorithm (relevance + recency + coherence)
- [ ] `HeuristicTokenCounter` (chars/4)
- [ ] Token-budgeted context assembly

**Verification:** Recall returns semantically relevant results

### Phase 4: HTTP Providers (~2-3 days)
**Goal:** Production-ready HTTP providers

- [ ] `HTTPEmbedder` (OpenAI-compatible `/embeddings`)
- [ ] `HTTPReflector` (OpenAI-compatible `/chat/completions`)
- [ ] Retry logic with exponential backoff
- [ ] Timeout handling
- [ ] Connection pooling (httpx)

**Verification:** End-to-end test with real HTTP endpoint (mock server)

### Phase 5: SQLite Backend (~3-4 days)
**Goal:** Persistent local storage with vector search

- [ ] Schema design (turns, episodes, facts, vectors)
- [ ] `SQLiteBackend` implementation
- [ ] sqlite-vec integration for vector search
- [ ] Async write flushing
- [ ] Connection pooling (aiosqlite)

**Verification:** 60+ turn conversation persists across restarts

### Phase 6: Reflection (~2-3 days)
**Goal:** Optional LLM-assisted fact extraction

- [ ] `ReflectionRunner` (async background task)
- [ ] L1→L2 fact extraction
- [ ] Integration with recall (L2 facts as candidates)
- [ ] Graceful degradation when reflection fails

**Verification:** Facts extracted from episodes, improve recall quality

### Phase 7: SDK Providers (Optional, ~2-3 days)
**Goal:** First-class support for OpenAI/Anthropic SDKs

- [ ] `OpenAIEmbedder`, `OpenAIReflector`
- [ ] `AnthropicReflector`
- [ ] Optional dependency handling

**Verification:** Works with user-provided SDK clients

### Phase 8: Polish (~2-3 days)
**Goal:** Production readiness

- [ ] Structured logging throughout
- [ ] Observability hooks (metrics, traces)
- [ ] ChromaDB backend (optional)
- [ ] Documentation (README, API docs, examples)
- [ ] PyPI packaging

**Verification:** Full test suite, benchmarks meet targets

---

## Verification Plan

### Unit Tests
- Models: serialization, validation
- Episode manager: boundary detection
- Recall: scoring, budgeting
- Providers: retry logic, error handling

### Integration Tests
- Full ingest→recall cycle
- SQLite persistence across restarts
- Long conversation (60+ turns)
- Concurrent operations

### Benchmarks
| Operation | Target | Measured |
|-----------|--------|----------|
| `ingest()` | <5ms | TBD |
| `recall()` | <50ms | TBD |
| SQLite write | <10ms | TBD |
| Vector search (1k items) | <20ms | TBD |

### Manual Testing
- Real conversation with Claude/GPT
- Edge cases: empty sessions, huge messages, rapid turns

---

## Files to Create (Phase 1)

```
acms/
├── __init__.py
├── py.typed
├── core/
│   ├── __init__.py
│   ├── session.py          # ACMS stub
│   └── config.py           # ACMSConfig
├── models/
│   ├── __init__.py
│   ├── turn.py
│   ├── episode.py
│   ├── fact.py
│   └── types.py
├── storage/
│   ├── __init__.py
│   ├── base.py
│   └── memory.py
├── providers/
│   ├── __init__.py
│   └── base.py
├── errors/
│   ├── __init__.py
│   └── exceptions.py
└── utils/
    ├── __init__.py
    ├── tokens.py
    └── ids.py

tests/
├── __init__.py
├── conftest.py
└── unit/
    ├── __init__.py
    └── test_models.py

pyproject.toml
```

---

## Dependencies

### Core (Required)
```toml
[project]
dependencies = [
    "pydantic>=2.0",  # Validation
]
```

### Optional Groups
```toml
[project.optional-dependencies]
sqlite = ["aiosqlite", "sqlite-vec"]
chroma = ["chromadb"]
postgres = ["asyncpg", "pgvector"]
openai = ["openai>=1.0"]
anthropic = ["anthropic>=0.20"]
tiktoken = ["tiktoken"]
dev = ["pytest", "pytest-asyncio", "ruff", "mypy", "httpx"]
all = ["acms[sqlite,chroma,openai,anthropic,tiktoken]"]
```

---

## Resolved Decisions

| Question | Decision |
|----------|----------|
| Cache layer | Yes, built-in LRU cache |
| Async embedding | Await during ingest (correctness first) |
| Multi-session | One instance = one session |
| Recency in scoring | No - current episode = implicit recency |
| Marker types | Enum (MarkerType) with configurable weights |
| Marker auto-detection | Enabled by default, configurable patterns |

## Open Questions

1. **Embedding batching** - Should we batch embedding calls? What's the max batch size?
2. **Marker persistence** - Should markers survive L0→L1 compaction or be extracted into L2?

---

## Evaluation Plan — Stress-Testing ACMS

### Current Baseline

The initial evaluation harness (`examples/evaluation/`) runs the `decision_tracking` scenario across 10–80 turn conversations. Results show **100% recall hit rate** with avg scores above 1.0 (marker-boosted).

**Why the current tests pass easily:**

1. All setup messages trigger ACMS marker auto-detection ("Decision:", "Constraint:", etc.) — marked turns get priority in recall regardless of age
2. Keywords are highly distinctive (FastAPI, PostgreSQL, Redis, PyJWT) — minimal chance of embedding confusion
3. Filler messages are semantically bland ("Can you elaborate?") — they don't compete with setup facts for vector similarity
4. Token budget (2000 tokens) is generous relative to fact volume (2–5 facts)
5. Only one scenario runs per evaluation

To produce meaningful, publishable benchmarks we need to find the **failure boundaries** — the conditions under which ACMS recall degrades — and then demonstrate that ACMS handles them gracefully or identify where improvements are needed.

---

### Phase E1: Adversarial Scenarios (Hardened Recall)

**Goal:** Create scenarios where recall is *genuinely difficult* and 100% hit rate is no longer guaranteed.

#### E1.1 — Semantic Distractor Fillers

Replace bland filler messages with topically relevant distractors that compete for embedding similarity.

```
Setup: "Decision: We'll use PostgreSQL for the database."
Fillers (hard): "I've been reading about MySQL vs MariaDB performance benchmarks."
              "The database migration strategy should account for schema changes."
              "SQLite is great for testing but won't scale for production."
Probe: "What database did we choose?"
```

Why this is hard: fillers about databases push PostgreSQL recall down in vector ranking. Tests whether markers actually rescue important turns.

#### E1.2 — Overlapping / Ambiguous Facts

Inject multiple facts in the same domain that could be confused.

```
Setup turn 1: "Use PostgreSQL for the users table."
Setup turn 4: "Use Redis for the session cache."
Setup turn 7: "Use MongoDB for the analytics pipeline."
Probe: "What database do we use for analytics?"  → expected: MongoDB (not PostgreSQL)
Probe: "What stores our sessions?"              → expected: Redis (not PostgreSQL)
```

Tests whether recall retrieves the *right* fact from the same domain, not just *any* database-related turn.

#### E1.3 — Fact Correction / Overwriting

Test whether later corrections supersede earlier decisions.

```
Setup turn 2: "Decision: We'll use Flask for the API framework."
Setup turn 15: "Decision: Actually, we're switching from Flask to FastAPI for async support."
Probe turn 30: "What API framework are we using?"
  → expected: FastAPI (must surface turn 15, ideally both for context)
  → failure: if only Flask is recalled
```

This tests whether ACMS recall pipeline handles temporal ordering — both turns will have markers, but the correction must be surfaced.

#### E1.4 — Unmarked Facts (Pure Semantic Recall)

Setup messages that do NOT trigger auto-detection, testing recall without marker boosts.

```
Setup: "The client specifically asked for a blue color scheme with rounded corners."
       "We agreed to deploy on AWS us-east-1."
       "The team prefers to use Tailwind CSS over Bootstrap."
```

None of these start with "Decision:", "Constraint:", etc. Without markers, ACMS must rely purely on semantic similarity. This isolates vector search quality from marker boosting.

#### E1.5 — High Fact Density

Inject 15–20 distinct facts across the first 20 turns. Probe each one individually later.

```
Facts: user name, project name, framework, database, deployment target,
       auth method, CSS framework, test framework, CI/CD tool, monitoring,
       team size, deadline, budget, primary language, API style, cache layer,
       message queue, search engine, CDN provider, feature flags
```

Tests whether recall degrades when many facts compete for limited token budget (2000 tokens). With 20 facts, some must be excluded — measures which ones survive and whether the right one surfaces per probe.

---

### Phase E2: Parameter Sensitivity Analysis

**Goal:** Find the degradation curves for key ACMS configuration knobs.

#### E2.1 — Token Budget Sweep

Run the same scenario with token_budget values: `500, 750, 1000, 1500, 2000, 3000, 4000`.

Expected behavior: recall should degrade at lower budgets (especially with many facts). Produces a **budget → recall curve** that's directly useful for documentation.

Implementation: Add `--token-budget` CLI flag, propagate to `AgentConfig.token_budget`.

#### E2.2 — Episode Length Sensitivity

Vary `max_turns_per_episode`: `4, 6, 8, 12, 16`.

Shorter episodes = more episode boundaries = more reflection runs = more L2 facts, but current episode context is smaller. Longer episodes = fewer reflections but larger current episode buffer.

Implementation: Add `--episode-length` CLI flag, propagate to `AgentConfig.max_turns_per_episode`.

#### E2.3 — Current Episode Budget Percentage

Vary `current_episode_budget_pct`: `0.2, 0.3, 0.4, 0.5, 0.6`.

Lower values give more room for past facts/turns; higher values prioritize recent context. The optimal balance depends on fact density.

Implementation: Requires exposing this knob through `AgentConfig` → `ACMSConfig.recall`.

---

### Phase E3: Scale and Endurance

**Goal:** Test ACMS at scale beyond what any reasonable demo would show.

#### E3.1 — Long Conversations

Extend turn counts to `[50, 100, 150, 200, 300]` with facts injected early (turns 1–10) and probes spread throughout.

Key question: Does recall degrade as conversation grows to 200+ turns and 25+ episodes?

#### E3.2 — Many-Episode Cross-Boundary Recall

With `max_turns_per_episode=4`, an 80-turn conversation generates ~20 episodes. Setup facts in episode 1, probe in episode 15+.

Tests whether L2 facts (reflection output) carry forward reliably across many episode boundaries.

#### E3.3 — Latency Under Load

Measure how ACMS overhead grows as the session database accumulates:
- At 10, 50, 100, 200 turns, what's the recall latency?
- Does vector search slow as embedding count grows?
- Does reflection time grow with episode count?

Already partially measured by our TurnLatency instrumentation — need to add a **latency-vs-turn-count curve** to the report.

---

### Phase E4: Quality Metrics Enhancement

**Goal:** Move beyond simple keyword hit rate to metrics that matter for a published benchmark.

#### E4.1 — Precision Measurement

Current metric: "Was the expected keyword found anywhere in recalled items?" (recall only, no precision).

Add: "What fraction of recalled items are actually relevant to the probe?" High recall with low precision means ACMS is flooding the context window with irrelevant content.

Implementation: For probe turns, classify each recalled item as relevant/irrelevant (keyword presence in the item). Report `precision = relevant_recalled / total_recalled`.

#### E4.2 — Rank-Aware Scoring (nDCG)

Not just "was it recalled?" but "was it recalled near the top?"

For each probe, compute nDCG@5 where relevance grades are:
- 2 = contains expected keyword + high score
- 1 = contains expected keyword
- 0 = irrelevant

This penalizes a system that recalls the right fact but buries it at position 8 behind 7 irrelevant items.

#### E4.3 — LLM-as-Judge (Response Quality)

The current harness only checks what ACMS recalls, not what the agent says. A complete evaluation checks the agent's actual response.

For each probe, run a separate LLM call:
```
Given:
  Question: "What database did we choose?"
  Agent response: "We chose PostgreSQL for the database."
  Expected keywords: ["PostgreSQL"]

Score the response: Does it correctly answer the question using the expected information?
Rating: 1 (correct), 0.5 (partial), 0 (wrong/missing)
```

This catches cases where ACMS recalls the right content but the agent hallucinates or ignores it.

#### E4.4 — Composite Cross-Scenario Score

Run all 5 scenarios (+ new ones) and produce a single weighted composite score:

| Scenario | Weight | Rationale |
|----------|--------|-----------|
| Decision tracking | 1.0 | Core use case |
| Constraint awareness | 1.2 | Constraints are safety-critical |
| Failure memory | 1.0 | Prevents waste |
| Multi-fact tracking | 1.5 | Real conversations have many facts |
| Goal tracking | 0.8 | Goals are less precise |
| Unmarked facts | 1.5 | Tests semantic recall without crutch |
| Fact correction | 1.3 | Tests temporal reasoning |
| High density | 1.5 | Tests budget allocation |

Implementation: Add `--all-scenarios` flag that runs every scenario and produces a unified report.

---

### Phase E5: New Targeted Scenarios

#### E5.1 — Contradiction Resolution

```
Turn 3: "Decision: Use JWT tokens for auth."
Turn 25: "Decision: We're switching to session cookies — JWT was too complex."
Probe turn 40: "What auth method are we using?"
  → Expected: session cookies (the later decision)
```

#### E5.2 — Cascading Decisions

```
Turn 2: "Decision: We're building a Python backend."
Turn 5: "Decision: Since we chose Python, we'll use SQLAlchemy as the ORM."
Turn 8: "Decision: SQLAlchemy needs us to define models — using the declarative base pattern."
Probe: "What ORM pattern are we using?"
  → Expected: declarative base
  → Bonus: Does ACMS also surface the chain (Python → SQLAlchemy → declarative base)?
```

#### E5.3 — Temporal Degradation Curve

Same single fact, same probe repeated at turns 10, 20, 30, 50, 75, 100, 150, 200. Produces a **recall score vs. turn distance** curve showing how memory fades (or doesn't) over time.

#### E5.4 — Budget Pressure

20 marked facts, token_budget=1000. More important content than budget can hold. Tests whether ACMS's scoring algorithm surfaces the *most relevant* facts for each probe rather than just the highest-marker-boosted ones.

#### E5.5 — Noise Injection

50% of filler messages are rephrased versions of setup facts with slightly different details:
```
Setup: "Decision: Use PostgreSQL."
Filler: "I've heard that MySQL is a good database choice for many teams."
Filler: "PostgreSQL is popular but some teams prefer MongoDB."
```

Tests whether near-duplicate noise degrades precision by pulling in confusable content.

---

### Implementation Priority

| Phase | Difficulty | Value | Priority |
|-------|-----------|-------|----------|
| E1.1 Semantic distractors | Low | High | **P0** |
| E1.4 Unmarked facts | Low | High | **P0** |
| E1.5 High fact density | Medium | High | **P0** |
| E4.1 Precision metric | Low | High | **P0** |
| E2.1 Token budget sweep | Low | High | **P1** |
| E1.2 Overlapping facts | Medium | High | **P1** |
| E1.3 Fact correction | Medium | High | **P1** |
| E4.4 Composite scoring | Medium | High | **P1** |
| E3.1 Long conversations | Low | Medium | **P1** |
| E4.2 nDCG scoring | Medium | Medium | **P2** |
| E5.3 Temporal curve | Low | Medium | **P2** |
| E2.2 Episode length sweep | Low | Medium | **P2** |
| E5.4 Budget pressure | Medium | Medium | **P2** |
| E4.3 LLM-as-judge | High | High | **P3** |
| E5.1 Contradiction | Medium | Medium | **P3** |
| E5.2 Cascading decisions | Medium | Medium | **P3** |
| E5.5 Noise injection | Medium | Medium | **P3** |

P0 items are achievable with minimal framework changes (new scenarios + one new metric). P1 adds config knobs and cross-scenario orchestration. P2/P3 require deeper framework extensions.

---

### Report Deliverables (for OSS README / Blog)

Once the above phases are implemented, the evaluation should produce:

1. **Decision Persistence Curve** — Recall hit rate vs. conversation length (10–200 turns)
2. **Token Budget Sensitivity** — Recall vs. budget (500–4000 tokens)
3. **ACMS Overhead Profile** — Milliseconds per turn breakdown (ingest, recall, reflection)
4. **Precision-Recall Tradeoff** — Hit rate vs. precision across scenarios
5. **Scenario Difficulty Spectrum** — Composite score across easy → hard scenarios
6. **Temporal Degradation** — Score vs. turn distance from fact injection
7. **Comparison Table** — Marked vs. unmarked fact recall to quantify marker value

These charts and tables form the evidence section of the ACMS README and any blog/paper about the project.

---

## Changelog

- **v0.2** (2025-02-10): Added evaluation stress-testing plan (Phases E1–E5)
- **v0.1** (2024-XX-XX): Initial plan
