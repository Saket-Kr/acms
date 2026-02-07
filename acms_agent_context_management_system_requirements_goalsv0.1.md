# Agent Context Management System (ACMS)

## 1. Background & Motivation

As our agent ecosystem grows in complexity, several agents now sustain **long-running conversations (50–60+ turns)** and make decisions incrementally over time. While some agents use Retrieval-Augmented Generation (RAG) or web search tools to fetch *external knowledge*, there is currently **no unified, principled mechanism for managing internal, session-level context and continuity**.

This has led to:
- Excessive prompt growth and token usage
- Loss of earlier decisions or constraints
- Repeated reasoning and duplicated tool calls
- Ad-hoc, agent-specific memory logic

This document defines the **requirements, goals, and non-goals** for a shared **Agent Context Management System (ACMS)** that provides structured, persistent, and scalable session memory for all agents.

---

## 2. Core Design Principle

> **Agent Memory is not Knowledge Retrieval.**

- RAG, web search, and databases are **knowledge tools** (external, stateless, query-driven)
- ACMS is **internal agent state** (experience-driven, persistent, continuity-focused)

The system must remain **orthogonal to RAG and tools**, while seamlessly integrating into every agent turn.

---

## 3. Scope Definition

### In Scope
- Session-level context management
- Agent-internal memory across turns
- Long-running conversations
- Multi-agent reuse via a common interface
- Structured memory abstraction (not raw chat logs)
- Token-efficient context assembly

### Explicitly Out of Scope (v1)
- Replacing RAG or vector search systems
- Global, cross-user knowledge bases
- Long-term user profiling across sessions
- Interactive or UI-facing memory inspection tools
- Model-specific prompt engineering

---

## 4. High-Level Goals

### Functional Goals
1. Preserve **continuity of reasoning** across long sessions
2. Remember **decisions, constraints, outcomes, and failures**
3. Provide agents with **relevant prior context automatically**
4. Reduce prompt size without reducing reasoning quality
5. Support agents **with or without RAG / web tools**

### Engineering Goals
1. Pluggable, agent-agnostic design
2. Minimal integration overhead (≤10 LOC per agent)
3. Deterministic and debuggable behavior
4. Incremental adoption (hybrid with existing systems)
5. Production-ready, not research-only

---

## 5. Non-Goals (Important Constraints)

The system is **not intended to**:
- Act as a search engine
- Store raw retrieved documents
- Replace conversation history entirely
- Perform autonomous reasoning or planning
- Decide *what* the agent should do

It only decides **what past experience is relevant**.

---

## 6. Conceptual Model

### Three Planes of an Agent System

1. **Memory Plane (ACMS)**
   - Internal, persistent
   - Experience- and decision-based
   - Runs automatically per turn

2. **Knowledge Plane (Tools)**
   - RAG, web search, APIs
   - External, stateless
   - Invoked conditionally

3. **Reasoning Plane (LLM / Planner)**
   - Consumes context from both planes
   - Produces actions and new memory

ACMS operates **independently** of the knowledge plane.

---

## 7. Memory Abstractions

### Memory Levels (Hierarchical)

The system must support multiple abstraction levels:

- **L0 – Raw Turns**  
  Verbatim user / agent / tool messages (short-lived)

- **L1 – Episodes**  
  Groups of turns centered around a goal or task

- **L2 – Semantic Facts**  
  Decisions, constraints, outcomes, failures

- **L3 – Themes (Future)**  
  Recurring patterns or high-level concepts

Each level:
- Has its own lifecycle
- Has its own embedding (if applicable)
- Is retrieved differently

---

## 8. Turn Lifecycle Integration

ACMS is **always-on**, not an explicit tool.

### Per-Turn Flow

1. **Begin Turn**
   - User input received
   - Relevant memory recalled automatically

2. **Reasoning & Tools**
   - Agent plans
   - Optional RAG / web search invoked

3. **End Turn**
   - Agent response produced
   - Memory-worthy information ingested
   - Reflection scheduled asynchronously

Agents should never manually decide *when* to recall memory.

---

## 9. Memory Ingestion Rules

### What Should Be Stored
- Decisions made
- Constraints discovered
- Failures and retries
- Tool usage outcomes
- User-provided preferences (session-level)

### What Should NOT Be Stored
- Raw RAG results
- Full web pages or documents
- Redundant paraphrases
- Model chain-of-thought

Rule of thumb:
> **Store conclusions, not evidence.**

---

## 10. Recall Requirements

Memory recall must be:
- **Query-aware** (based on current user intent)
- **Hierarchical** (top-down abstraction)
- **Token-budgeted** (hard limits)
- **Expandable** (raw turns only if needed)

The output should be **structured context**, not raw text dumps.

---

## 11. Reflection & Consolidation

Reflection is a background process that:
- Groups turns into episodes
- Extracts durable semantic facts
- Promotes recurring facts
- Prunes obsolete or low-value memory

Reflection must:
- Be asynchronous
- Never block agent responses
- Be safe to disable

---

## 12. Pluggability & Reuse

The system must:
- Support multiple agents
- Support multiple sessions per agent
- Be independent of LLM provider
- Be independent of orchestration framework

Public APIs should be stable and minimal.

---

## 13. Observability & Safety

Minimum required features:
- Recall traces (why a memory was included)
- Token usage accounting
- Memory versioning
- Kill-switch per agent or globally

Debuggability is a first-class requirement.

---

## 14. Adoption Strategy

### Phase 1 (MVP)
- Episodes only (L0 + L1)
- Replace raw chat stuffing
- Session-scoped memory

### Phase 2
- Semantic facts (L2)
- Hierarchical recall
- Token-aware expansion

### Phase 3
- Themes (L3)
- Decay and reinforcement
- Cross-session intelligence (optional)

---

## 15. Success Criteria

The system is successful if:
- Agents maintain coherence beyond 50–60 turns
- Prompt sizes stabilize
- Reasoning quality improves subjectively
- Memory logic is removed from agent code
- New agents adopt ACMS by default

---

## 16. Open Questions (To Be Decided)

- Session vs cross-session persistence
- Memory TTL policies
- Degree of LLM involvement in reflection
- Multi-user vs single-user sessions
- OSS vs internal-only library

---

## 17. Summary

ACMS is a **shared, foundational layer** that provides structured, persistent, and efficient context management for long-running agents. It deliberately separates **memory** from **knowledge retrieval**, enabling scalable and maintainable agent architectures.

This document serves as the baseline for design, implementation, and future iteration.

