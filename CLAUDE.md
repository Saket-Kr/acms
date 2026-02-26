# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gleanr (Agent Context Management System) is a session-scoped memory layer for AI agents. It provides structured, persistent context management that is distinct from knowledge retrieval (RAG/search).

**Core principle:** Agent memory is not knowledge retrieval. Gleanr handles internal agent state (experience-driven, persistent, continuity-focused), not external knowledge queries.

## Architecture

### Three Planes Model
1. **Memory Plane (Gleanr)** - Internal, session-scoped, always-on per turn
2. **Knowledge Plane (Tools)** - RAG, web search, APIs (external, stateless)
3. **Reasoning Plane (LLM)** - Consumes context from both planes

Gleanr operates **before tool invocation** and **after agent output**.

### Memory Levels
- **L0 (Raw Turns)** - Verbatim messages, short-lived with aggressive TTL
- **L1 (Episodes)** - Mandatory grouping of turns around goals/tasks, session-bound
- **L2 (Semantic Facts)** - Optional, reflection-generated (decisions, constraints, outcomes)
- **L3 (Themes)** - Future, not in v1

### Turn Lifecycle
1. Begin Turn: User input received → relevant memory recalled automatically
2. Reasoning & Tools: Agent plans, optional RAG/search
3. End Turn: Response produced → memory-worthy info ingested → reflection scheduled async

## Key Design Decisions

- Reflection enabled by default but system works without it (L1 episodes remain functional)
- Store conclusions, not evidence (no raw RAG results, no chain-of-thought)
- Token-budgeted recall with hard limits
- All memory events track `actor_type` (user|agent|tool) and `actor_id`
- Integration target: ≤10 LOC per agent

## What to Store vs Not Store

**Store:** Decisions made, constraints discovered, failures/retries, tool outcomes, session preferences

**Never store:** Raw RAG results, web pages, redundant paraphrases, hidden reasoning
