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

## Changelog

- **v0.1** (2024-XX-XX): Initial plan
