# Agent Context Management System (ACMS)

**Version:** v0.2  
**Status:** Requirements Locked (Pre-Implementation)

---

## 1. Background & Motivation

As our agent ecosystem grows in complexity, several agents now sustain **long-running conversations (50–60+ turns)** and make decisions incrementally over time. While some agents use Retrieval-Augmented Generation (RAG) or web search tools to fetch *external knowledge*, there is currently **no unified, principled mechanism for managing internal, session-level context and continuity**.

This has led to:
- Excessive prompt growth and token usage
- Loss of earlier decisions or constraints
- Repeated reasoning and duplicated tool calls
- Ad-hoc, agent-specific memory logic

This document defines the **requirements, goals, and locked design decisions** for a shared **Agent Context Management System (ACMS)** that provides structured, persistent, and scalable session memory for all agents.

---

## 2. Core Design Principle

> **Agent Memory is not Knowledge Retrieval.**

- RAG, web search, and databases are **knowledge tools** (external, stateless, query-driven)
- ACMS is **internal agent state** (experience-driven, persistent, continuity-focused)

ACMS runs **independently** of RAG and tools and is injected automatically into every agent turn.

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
- ❌ Cross-session or long-term memory
- ❌ User profiling across sessions
- ❌ Replacing RAG or search systems
- ❌ Storing retrieved documents or web content
- ❌ Autonomous reasoning or planning logic

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
5. Production-grade defaults, not research prototypes

---

## 5. Non-Goals (Hard Constraints)

ACMS is **not intended to**:
- Act as a search engine
- Store raw retrieved knowledge
- Replace conversation history entirely
- Perform chain-of-thought reasoning
- Decide *what* the agent should do

ACMS only decides **what past experience is relevant**.

---

## 6. Conceptual Model

### Three Planes of an Agent System

1. **Memory Plane (ACMS)**
   - Internal, persistent (session-scoped)
   - Experience- and decision-based
   - Always-on per turn

2. **Knowledge Plane (Tools)**
   - RAG, web search, APIs
   - External, stateless
   - Invoked conditionally by the agent

3. **Reasoning Plane (LLM / Planner)**
   - Consumes context from both planes
   - Produces actions and new memory

ACMS operates **before tool invocation** and **after agent output**.

---

## 7. Memory Abstractions

### Mandatory Memory Levels

- **L0 – Raw Turns**  
  Verbatim user / agent / tool messages. Short-lived.

- **L1 – Episodes (Mandatory)**  
  Deterministic grouping of turns around a goal or task.

### Optional Memory Levels

- **L2 – Semantic Facts (Reflection-Generated)**  
  Decisions, constraints, outcomes, failures.

- **L3 – Themes (Future)**  
  Recurring high-level patterns.

> **Design Rule:** L1 Episodes MUST exist even if reflection is disabled.

---

## 8. Turn Lifecycle Integration

ACMS is **implicit and always-on**, not an explicit tool.

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

Agents never manually decide *when* to recall memory.

---

## 9. Memory Ingestion Rules

### What Should Be Stored
- Decisions made
- Constraints discovered
- Failures and retries
- Tool usage outcomes
- Session-scoped user preferences

### What Must NOT Be Stored
- Raw RAG results
- Web pages or documents
- Redundant paraphrases
- Chain-of-thought or hidden reasoning

> **Rule of thumb:** Store conclusions, not evidence.

---

## 10. Reflection (Locked Decision)

### Default Behavior
- **Reflection is ENABLED by default**
- Reflection is **LLM-assisted but deterministic in control**
- Reflection runs **asynchronously**

### Responsibilities of Reflection
- Group raw turns into episodes (L0 → L1)
- Extract semantic facts (L1 → L2)
- Compact and prune memory

### Reflection-Free Fallback (Mandatory)

If reflection is disabled:
- Deterministic episodic memory (L1) remains active
- Episode boundaries are formed via rules (tool calls, turn limits, task completion)
- No semantic facts or themes are generated

> Reflection improves memory quality but is **not required for correctness**.

---

## 11. Recall Requirements

Memory recall must be:
- Query-aware
- Hierarchical (when levels exist)
- Token-budgeted (hard limits)
- Gracefully degrading based on available levels

Without reflection, recall operates at **episode level only**.

---

## 12. Memory Lifetime & Decay (Locked Decision)

| Level | Policy |
|----|----|
| L0 Raw turns | Aggressive TTL |
| L1 Episodes | Session-bound |
| L2 Semantic facts | Usage-based decay |
| L3 Themes | Not applicable (v1) |

All memory items track creation time and recall metadata.

---

## 13. Actor Model

- All memory events include:
  - `actor_type` (user | agent | tool)
  - `actor_id`

Sessions may contain multiple actors.

---

## 14. Pluggability & Reuse

The system must:
- Support multiple agents
- Support multiple sessions per agent
- Be independent of LLM provider
- Be independent of orchestration framework

Public APIs are stable and minimal.

---

## 15. Observability & Safety

Required features:
- Recall traces (why a memory was included)
- Token usage accounting
- Memory versioning
- Global and per-agent kill switches

---

## 16. Versioning Strategy

- v0.x: Requirements & design
- **v1.0: Session-scoped episodic memory with reflection**
- No breaking behavioral changes within v1.x

---

## 17. Success Criteria

The system is successful if:
- Agents maintain coherence beyond 50–60 turns
- Prompt sizes stabilize
- Reasoning quality improves
- Memory logic is removed from agent code
- New agents adopt ACMS by default

---

## 18. Summary

ACMS is a **session-scoped, always-on memory substrate** for agents. It cleanly separates **memory from knowledge retrieval**, mandates episodic structure, enables reflection by default, and degrades gracefully when reflection is unavailable.

This document (v0.2) locks the requirements for implementation.

