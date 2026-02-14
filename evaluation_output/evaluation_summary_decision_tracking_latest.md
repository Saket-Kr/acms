# ACMS Evaluation Report

Generated: 2026-02-14 09:00:33
Total Runtime: 11m 48s

## Executive Summary

- **Total sessions**: 10
- **Total turns evaluated**: 150
- **Overall recall hit rate**: 100.0%
- **Consistency score**: 1.00
- **Optimal conversation length**: 20 turns

## ACMS Overhead Analysis

**ACMS adds ~6076ms per turn on average.**

| Turn Count | Avg ACMS Overhead | Avg (excl. Reflection) | Avg Recall | Avg Ingest (User) | Avg Ingest (Asst) |
|------------|-------------------|------------------------|------------|-------------------|-------------------|
| 10 | 4766ms | 996ms | 331ms | 2644ms | 1791ms |
| 20 | 7386ms | 1081ms | 333ms | 5342ms | 1711ms |

## Consolidation Analysis

**Overall staleness rate: 0.0%** (fraction of probes with stale/superseded keywords in recall)

**Overall consolidation ratio: 0.00** (superseded / total facts)

| Turn Count | Avg Staleness | Avg Consolidation Ratio | Avg Active Facts | Avg Superseded Facts |
|------------|---------------|-------------------------|------------------|----------------------|
| 10 | 0% | 0.00 | 17.0 | 0.0 |
| 20 | 0% | 0.01 | 38.0 | 0.2 |

> ✅ **Consolidation is working correctly** — no stale facts appear in recall.

## Configuration

- Scenario: `decision_tracking`
- Turn counts: [10, 20]
- Iterations per turn count: 5
- Max concurrent: 3

## Decision Persistence by Turn Count

| Turns | Iterations | Avg Recall Rate | Std Dev | Avg Score | Min | Max |
|-------|------------|-----------------|---------|-----------|-----|-----|
| 10 | 5 | 100.0% | 0.00 | 1.18 | 1.02 | 1.29 |
| 20 | 5 | 100.0% | 0.00 | 1.07 | 0.98 | 1.23 |

## Detailed Results

### 10-Turn Conversations

- **Average recall hit rate**: 100.0%
- **Standard deviation**: 0.000
- **Score range**: 1.02 - 1.29

#### Iteration 1 ✅

- Session ID: `eval_10t_iter1_f5a53eee`
- Recall Hit Rate: 100.0%
- Average Score: 1.054
- Time: 114.3s
- Episodes closed: 6
- Facts extracted: 29
- Tokens ingested: 9,541
- Avg ACMS overhead: 6549ms/turn
- Avg ACMS overhead (excl reflection): 1019ms/turn
- Reflection turns: 6
- p95 ACMS overhead: 16403ms
- Active facts: 29, Superseded: 0, Consolidation ratio: 0.00
- Staleness rate: 0%

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.010)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision', 'goal']` "Goal: Integrate PostgreSQL into the FastAPI project  

**Decision:**  
We’ll set up asynchronous acc..." (score: 1.010)
    3. [assistant] `['goal']` "**Goal:** Build a FastAPI web API

Got it! FastAPI is a great choice for building modern, high‑perfo..." (score: 0.906)
    4. [assistant] `['goal']` "Build a FastAPI web API" (score: 0.959)
    5. [assistant] `['decision']` "Version the API (e.g., /v1/) and maintain backward compatibility with existing database schema to re..." (score: 0.958)
    ... and 25 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.097)
  - Recalled content:
    1. [assistant] "**High‑level best‑practice checklist for a FastAPI + PostgreSQL API**

| Area | What to do | Why it ..." (score: 1.000)
    2. [user] "How do I test this?" (score: 1.000)
    3. [assistant] "**Testing a FastAPI + PostgreSQL stack in three flavours**

| Test type | What to cover | Typical to..." (score: 1.000)
    4. [user] "What database did we choose?" (score: 1.000)
    5. [assistant] `['decision', 'goal']` "Goal: Integrate PostgreSQL into the FastAPI project  

**Decision:**  
We’ll set up asynchronous acc..." (score: 1.097)
    ... and 41 more items

---

#### Iteration 2 ✅

- Session ID: `eval_10t_iter2_28c7623b`
- Recall Hit Rate: 100.0%
- Average Score: 1.295
- Time: 69.4s
- Episodes closed: 5
- Facts extracted: 7
- Tokens ingested: 8,004
- Avg ACMS overhead: 3213ms/turn
- Avg ACMS overhead (excl reflection): 997ms/turn
- Reflection turns: 5
- p95 ACMS overhead: 7900ms
- Active facts: 7, Superseded: 0, Consolidation ratio: 0.00
- Staleness rate: 0%

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 0.990)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['goal']` "Goal: Build a FastAPI web API.

To get started, could you specify:

1. The main resources/endpoints ..." (score: 0.947)
    3. [assistant] `['goal']` "Goal: Build a FastAPI web API (using PostgreSQL).

Great—choosing PostgreSQL gives us a solid, produ..." (score: 0.719)
    4. [assistant] `['decision']` "**Decision:**  Provide a step‑by‑step checklist to verify that the FastAPI + PostgreSQL stack is wor..." (score: 0.701)
    5. [assistant] `['decision']` "The user decided to use FastAPI as the framework for the web API." (score: 0.990)
    ... and 11 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.600)
  - Recalled content:
    1. [user] "Can you walk me through this?" (score: 1.000)
    2. [assistant] `['decision', 'goal']` "**Decision:** Deliver a concise “step‑by‑step walkthrough” that ties together the key pieces you nee..." (score: 1.600)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision']` "**Decision:** Mention the framework the user will use.

**Answer:** We're using **FastAPI** for the ..." (score: 0.950)
    5. [assistant] `['goal']` "Goal: Build a FastAPI web API.

To get started, could you specify:

1. The main resources/endpoints ..." (score: 0.817)
    ... and 20 more items

---

#### Iteration 3 ✅

- Session ID: `eval_10t_iter3_390ba303`
- Recall Hit Rate: 100.0%
- Average Score: 1.020
- Time: 83.6s
- Episodes closed: 6
- Facts extracted: 11
- Tokens ingested: 8,838
- Avg ACMS overhead: 3902ms/turn
- Avg ACMS overhead (excl reflection): 1010ms/turn
- Reflection turns: 5
- p95 ACMS overhead: 10376ms
- Active facts: 11, Superseded: 0, Consolidation ratio: 0.00
- Staleness rate: 0%

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.022)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision', 'goal']` "**Goal:** Help you integrate a PostgreSQL database with your FastAPI project.

---

### Decision:
I’..." (score: 1.022)
    3. [assistant] `['failure', 'goal']` "**Goal:** Show you a systematic way to debug a FastAPI + PostgreSQL stack when things go wrong.

---..." (score: 0.953)
    4. [assistant] `['goal']` "**Goal:** Create a quick, production‑ready FastAPI web API.

---

## 1. Project setup  
```bash
# Cr..." (score: 0.779)
    5. [assistant] `['goal']` "Create a quick, production‑ready FastAPI web API." (score: 0.927)
    ... and 13 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.018)
  - Recalled content:
    1. [assistant] "## Recommended FastAPI + PostgreSQL stack

Below is a “starter‑kit” that you can copy‑paste into a f..." (score: 1.000)
    2. [user] "What database did we choose?" (score: 1.000)
    3. [assistant] `['decision', 'goal']` "**Goal:** Help you integrate a PostgreSQL database with your FastAPI project.

---

### Decision:
I’..." (score: 1.018)
    4. [assistant] `['decision']` "**Decision:** We are using **FastAPI** as the framework for the API." (score: 0.924)
    5. [assistant] `['failure', 'goal']` "**Goal:** Show you a systematic way to debug a FastAPI + PostgreSQL stack when things go wrong.

---..." (score: 0.914)
    ... and 23 more items

---

#### Iteration 4 ✅

- Session ID: `eval_10t_iter4_b63b7248`
- Recall Hit Rate: 100.0%
- Average Score: 1.266
- Time: 111.1s
- Episodes closed: 5
- Facts extracted: 25
- Tokens ingested: 8,184
- Avg ACMS overhead: 5843ms/turn
- Avg ACMS overhead (excl reflection): 922ms/turn
- Reflection turns: 5
- p95 ACMS overhead: 20363ms
- Active facts: 25, Superseded: 0, Consolidation ratio: 0.00
- Staleness rate: 0%

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.231)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision', 'goal']` "**Goal:** Assist with building a FastAPI web API.

**Decision:** Start by outlining a minimal FastAP..." (score: 1.231)
    3. [assistant] `['decision', 'goal']` "**Goal:** Incorporate PostgreSQL into your FastAPI project.

**Decision:** Gather the remaining deta..." (score: 1.116)
    4. [assistant] `['goal']` "**Goal:** Help you flesh out a FastAPI + PostgreSQL web API project.

---

## 1. Project skeleton

`..." (score: 0.713)
    5. [assistant] `['decision']` "User wants to build a web API using FastAPI" (score: 0.952)
    ... and 21 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [user] "Is this approach scalable?" (score: 1.000)
    2. [assistant] `['decision']` "**Decision:** The core FastAPI + async SQLAlchemy + PostgreSQL stack you sketched is *already* produ..." (score: 1.300)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision', 'goal']` "**Goal:** Incorporate PostgreSQL into your FastAPI project.

**Decision:** Gather the remaining deta..." (score: 1.208)
    5. [assistant] `['decision', 'goal']` "**Goal:** Assist with building a FastAPI web API.

**Decision:** Start by outlining a minimal FastAP..." (score: 1.095)
    ... and 38 more items

---

#### Iteration 5 ✅

- Session ID: `eval_10t_iter5_d89aca7b`
- Recall Hit Rate: 100.0%
- Average Score: 1.287
- Time: 92.8s
- Episodes closed: 6
- Facts extracted: 13
- Tokens ingested: 11,327
- Avg ACMS overhead: 4324ms/turn
- Avg ACMS overhead (excl reflection): 1030ms/turn
- Reflection turns: 6
- p95 ACMS overhead: 12457ms
- Active facts: 13, Superseded: 0, Consolidation ratio: 0.00
- Staleness rate: 0%

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.073)
  - Recalled content:
    1. [assistant] "**Why FastAPI + PostgreSQL?**

| Decision | Reason | What it gives you |
|----------|--------|------..." (score: 1.000)
    2. [user] "What framework are we using for the API?" (score: 1.000)
    3. [assistant] `['decision', 'goal']` "**Goal:** Build a FastAPI web API.

**Decision:** Provide a quick‑start guide + example skeleton.

-..." (score: 1.073)
    4. [assistant] `['goal']` "**Goal:** Help the user debug their FastAPI + PostgreSQL setup.

I need more specifics.  
**Question..." (score: 0.786)
    5. [assistant] `['goal']` "**Goal:** Add PostgreSQL persistence to the FastAPI skeleton.

Below is a one‑page recipe that

| St..." (score: 0.714)
    ... and 9 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.500)
  - Recalled content:
    1. [assistant] `['goal']` "**Goal:** Outline the end‑to‑end workflow for building, integrating, and debugging a FastAPI web API..." (score: 1.300)
    2. [user] "What's the typical workflow?" (score: 1.000)
    3. [assistant] `['failure', 'goal']` "**Goal:** Outline the end‑to‑end workflow for building, integrating, debugging, and publishing a Fas..." (score: 1.500)
    4. [user] "What database did we choose?" (score: 1.000)
    5. [assistant] `['decision', 'goal']` "**Goal:** Build a FastAPI web API.

**Decision:** Provide a quick‑start guide + example skeleton.

-..." (score: 1.007)
    ... and 25 more items

---

### 20-Turn Conversations

- **Average recall hit rate**: 100.0%
- **Standard deviation**: 0.000
- **Score range**: 0.98 - 1.23

#### Iteration 1 ✅

- Session ID: `eval_20t_iter1_6b7f283f`
- Recall Hit Rate: 100.0%
- Average Score: 0.983
- Time: 258.6s
- Episodes closed: 11
- Facts extracted: 53
- Tokens ingested: 15,815
- Avg ACMS overhead: 8965ms/turn
- Avg ACMS overhead (excl reflection): 1068ms/turn
- Reflection turns: 11
- p95 ACMS overhead: 28404ms
- Active facts: 53, Superseded: 0, Consolidation ratio: 0.00
- Staleness rate: 0%

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 0.954)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['goal']` "**Goal:** Build a web API with FastAPI.

---

### 1. Project structure (recommended)

```
my_api/
├─..." (score: 0.711)
    3. [assistant] `['goal']` "**Goal:** Make sure your FastAPI + PostgreSQL stack actually talks to the database and returns data...." (score: 0.678)
    4. [assistant] `['goal']` "Build a web API with FastAPI" (score: 0.954)
    5. [assistant] `['constraint']` "Specify DATABASE_URL in .env with value 'postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbnam..." (score: 0.864)
    ... and 17 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.200)
  - Recalled content:
    1. [user] "What are common mistakes?" (score: 1.000)
    2. [assistant] `['failure']` "**Top pitfalls that trip folks up when wiring a FastAPI‑PostgreSQL stack**

| # | Mistake | Why it h..." (score: 1.200)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['goal']` "**Goal:** Make sure your FastAPI + PostgreSQL stack actually talks to the database and returns data...." (score: 0.700)
    5. [assistant] `['goal']` "**Goal:** Build a web API with FastAPI.

---

### 1. Project structure (recommended)

```
my_api/
├─..." (score: 0.651)
    ... and 37 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 0.779)
  - Recalled content:
    1. [user] "Remind me of our technology choices so far." (score: 1.000)
    2. [assistant] `['decision']` "**Decision:**  
FastAPI + PostgreSQL (asyncpg + AsyncSQLAlchemy) is a solid, modern choice for a CRU..." (score: 0.753)
    3. [assistant] `['goal']` "**Goal:** Make sure your FastAPI + PostgreSQL stack actually talks to the database and returns data...." (score: 0.698)
    4. [assistant] `['goal']` "**Goal:** Build a web API with FastAPI.

---

### 1. Project structure (recommended)

```
my_api/
├─..." (score: 0.665)
    5. [assistant] `['failure']` "**Top pitfalls that trip folks up when wiring a FastAPI‑PostgreSQL stack**

| # | Mistake | Why it h..." (score: 0.598)
    ... and 65 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "**Single‑page “tool‑kit” for a production‑ready FastAPI+PostgreSQL API**

| Layer | Tool | Why we ne..." (score: 1.000)
    2. [user] "What are common mistakes?" (score: 1.000)
    3. [assistant] "**Common pitfalls when wiring a FastAPI + PostgreSQL stack**

| # | Mistake | Why it hurts | Quick f..." (score: 1.000)
    4. [user] "What framework and database are we using?" (score: 1.000)
    5. [assistant] `['decision']` "**Decision:**  
FastAPI + PostgreSQL (asyncpg + AsyncSQLAlchemy) is a solid, modern choice for a CRU..." (score: 0.736)
    ... and 78 more items

---

#### Iteration 2 ✅

- Session ID: `eval_20t_iter2_ed983ce7`
- Recall Hit Rate: 100.0%
- Average Score: 1.087
- Time: 265.2s
- Episodes closed: 10
- Facts extracted: 45
- Tokens ingested: 20,350
- Avg ACMS overhead: 8422ms/turn
- Avg ACMS overhead (excl reflection): 1145ms/turn
- Reflection turns: 10
- p95 ACMS overhead: 28627ms
- Active facts: 45, Superseded: 0, Consolidation ratio: 0.00
- Staleness rate: 0%

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 0.964)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['goal']` "**Goal:**  Build a simple FastAPI web API  

Below is a minimal, step‑by‑step guide you can copy‑pas..." (score: 0.711)
    3. [assistant] `['decision']` "The database chosen for the API is PostgreSQL." (score: 1.009)
    4. [assistant] `['goal']` "The user wants to build a web API using FastAPI." (score: 0.964)
    5. [assistant] `['constraint']` "A DATABASE_URL environment variable must be defined (e.g., in a .env file) for the app to connect." (score: 0.956)
    ... and 18 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.500)
  - Recalled content:
    1. [user] "How would you implement that?" (score: 1.000)
    2. [assistant] `['decision', 'failure']` "Decision: Provide a minimal, working skeleton that follows the described strategy (async FastAPI + P..." (score: 1.500)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['goal']` "**Goal:**  Build a simple FastAPI web API  

Below is a minimal, step‑by‑step guide you can copy‑pas..." (score: 0.683)
    5. [assistant] `['failure']` "**Error handling in FastAPI (PostgreSQL / async‑SQLAlchemy)**  

FastAPI already handles a lot for y..." (score: 0.604)
    ... and 34 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 0.881)
  - Recalled content:
    1. [user] "Remind me of our technology choices so far." (score: 1.000)
    2. [assistant] `['decision', 'failure']` "Decision: Provide a minimal, working skeleton that follows the described strategy (async FastAPI + P..." (score: 0.881)
    3. [assistant] `['decision']` "**Decision:** Provide a clear, bullet‑point rundown of how each common mistake slacks performance in..." (score: 0.736)
    4. [assistant] `['goal']` "**Goal:**  Build a simple FastAPI web API  

Below is a minimal, step‑by‑step guide you can copy‑pas..." (score: 0.679)
    5. [assistant] `['failure']` "**Key performance impacts of common FastAPI‑PostgreSQL pitfalls**

| Pitfall | Typical impact | Why ..." (score: 0.629)
    ... and 37 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.002)
  - Recalled content:
    1. [user] "How do I verify this works?" (score: 1.000)
    2. [assistant] "**Step‑by‑step “how to verify” checklist**  
You can validate your FastAPI + PostgreSQL stack in two..." (score: 1.000)
    3. [user] "What framework and database are we using?" (score: 1.000)
    4. [assistant] `['decision', 'failure']` "Decision: Provide a minimal, working skeleton that follows the described strategy (async FastAPI + P..." (score: 0.928)
    5. [assistant] `['decision']` "**Decision:** Provide a clear, bullet‑point rundown of how each common mistake slacks performance in..." (score: 0.704)
    ... and 20 more items

---

#### Iteration 3 ✅

- Session ID: `eval_20t_iter3_0b571ca8`
- Recall Hit Rate: 100.0%
- Average Score: 1.022
- Time: 242.1s
- Episodes closed: 11
- Facts extracted: 45
- Tokens ingested: 13,682
- Avg ACMS overhead: 8626ms/turn
- Avg ACMS overhead (excl reflection): 1024ms/turn
- Reflection turns: 11
- p95 ACMS overhead: 19652ms
- Active facts: 45, Superseded: 0, Consolidation ratio: 0.00
- Staleness rate: 0%

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.019)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['goal']` "Build a web API with FastAPI framework." (score: 1.019)
    3. [assistant] `['decision']` "Use PostgreSQL as the database for the FastAPI web API." (score: 0.916)
    4. [assistant] `['decision']` "Create central error handler function create_error_handlers that registers DomainError, IntegrityErr..." (score: 0.860)
    5. [assistant] `['decision']` "Full-stack FastAPI + PostgreSQL GitHub repo located at https://github.com/tiangolo/full-stack-fastap..." (score: 0.828)
    ... and 26 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [user] "How do I verify this works?" (score: 1.000)
    2. [assistant] `['goal']` "**Goal:** Quickly confirm that your FastAPI + PostgreSQL stack is wired up correctly.

Below is a pr..." (score: 1.300)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision']` "**Decision:** Offer a concise, side‑by‑side view of the FastAPI + PostgreSQL stack versus a handful ..." (score: 0.814)
    5. [assistant] `['decision']` "Database migrations with Alembic in FastAPI tutorial located at https://testdriven.io/blog/fastapi-s..." (score: 0.885)
    ... and 48 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 0.769)
  - Recalled content:
    1. [user] "Remind me of our technology choices so far." (score: 1.000)
    2. [assistant] `['decision']` "**Decision:** Offer a concise, side‑by‑side view of the FastAPI + PostgreSQL stack versus a handful ..." (score: 0.765)
    3. [assistant] `['decision']` "**Decision:** Summarize the core and optional dependencies for a FastAPI‑+‑PostgreSQL API.

---

## ..." (score: 0.734)
    4. [assistant] `['goal']` "**Goal:** Clarify which part of the FastAPI + Postgres stack you’re looking for best‑practice guidan..." (score: 0.730)
    5. [assistant] `['goal']` "**Goal:**  
Recommend a balanced set of tools for building a FastAPI + PostgreSQL web API that is ea..." (score: 0.697)
    ... and 65 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "**Short‑answer:**  
Yes – there are several full‑stack options you can swap in place of a FastAPI + ..." (score: 1.000)
    2. [user] "Are there any edge cases?" (score: 1.000)
    3. [assistant] "**Edge‑case checklist for a “FastAPI + PostgreSQL” stack**

| # | Edge case | Why it matters | Quick..." (score: 1.000)
    4. [user] "What framework and database are we using?" (score: 1.000)
    5. [assistant] `['goal']` "**Goal:** Clarify which part of the FastAPI + Postgres stack you’re looking for best‑practice guidan..." (score: 0.879)
    ... and 23 more items

---

#### Iteration 4 ✅

- Session ID: `eval_20t_iter4_e0956c8a`
- Recall Hit Rate: 100.0%
- Average Score: 1.049
- Time: 237.0s
- Episodes closed: 11
- Facts extracted: 35
- Tokens ingested: 24,206
- Avg ACMS overhead: 6501ms/turn
- Avg ACMS overhead (excl reflection): 1052ms/turn
- Reflection turns: 11
- p95 ACMS overhead: 19355ms
- Active facts: 34, Superseded: 1, Consolidation ratio: 0.03
- Staleness rate: 0%

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 0.952)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['failure', 'goal']` "**Goal:** Build a simple but production‑ready web API using FastAPI.

Below is a practical, step‑by‑..." (score: 0.915)
    3. [assistant] `['decision']` "**Decision:** The FastAPI + PostgreSQL stack with async SQLAlchemy 2.0 and Alembic migrations is a s..." (score: 0.742)
    4. [assistant] `['goal']` "**Goal:** Add a PostgreSQL data layer to the FastAPI project (async SQLAlchemy 2.0, Alembic migratio..." (score: 0.734)
    5. [assistant] `['goal']` "User wants to build a web API using FastAPI" (score: 0.952)
    ... and 18 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "What's the recommended setup?" (score: 1.000)
    2. [assistant] "**Recommended FastAPI + PostgreSQL (async SQLAlchemy 2.0) stack**

| Layer | What to use | Why it ma..." (score: 1.000)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision']` "**Decision:** The API will be built with **FastAPI** – an asynchronous, type‑driven framework that i..." (score: 0.915)
    5. [assistant] `['failure', 'goal']` "**Goal:** Build a simple but production‑ready web API using FastAPI.

Below is a practical, step‑by‑..." (score: 0.891)
    ... and 11 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 0.946)
  - Recalled content:
    1. [user] "Remind me of our technology choices so far." (score: 1.000)
    2. [assistant] `['failure', 'goal']` "**Goal:** Build a simple but production‑ready web API using FastAPI.

Below is a practical, step‑by‑..." (score: 0.946)
    3. [assistant] `['decision']` "**Decision:** The API will be built with **FastAPI** – an asynchronous, type‑driven framework that i..." (score: 0.817)
    4. [assistant] `['constraint']` "## ✅ Building a FastAPI Web‑API – “From 0 to Ready”

Below is a **road‑map** that takes you from an ..." (score: 0.753)
    5. [assistant] `['decision']` "**Decision:** The FastAPI + PostgreSQL stack with async SQLAlchemy 2.0 and Alembic migrations is a s..." (score: 0.720)
    ... and 45 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [assistant] "**Common pitfalls when building a FastAPI + async PostgreSQL stack**

| # | Mistake | Why it hurts |..." (score: 1.000)
    2. [user] "How do I test this?" (score: 1.000)
    3. [assistant] `['decision']` "**Decision:**  
I’ll give you a full‑stack testing recipe (unit + integration) for the FastAPI + asy..." (score: 1.300)
    4. [user] "What framework and database are we using?" (score: 1.000)
    5. [assistant] `['decision']` "**Decision:** The API will be built with **FastAPI** – an asynchronous, type‑driven framework that i..." (score: 0.914)
    ... and 8 more items

---

#### Iteration 5 ✅

- Session ID: `eval_20t_iter5_ff084f3e`
- Recall Hit Rate: 100.0%
- Average Score: 1.230
- Time: 162.8s
- Episodes closed: 11
- Facts extracted: 13
- Tokens ingested: 18,722
- Avg ACMS overhead: 4416ms/turn
- Avg ACMS overhead (excl reflection): 1116ms/turn
- Reflection turns: 11
- p95 ACMS overhead: 11437ms
- Active facts: 13, Superseded: 0, Consolidation ratio: 0.00
- Staleness rate: 0%

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.164)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['constraint', 'goal']` "**Goal:** Build a web API using FastAPI.

Below are the basic steps to get you started, along with a..." (score: 1.164)
    3. [assistant] `['goal']` "**Goal:** Build a web API using FastAPI.

Below are a few alternatives you might consider if you’d l..." (score: 0.809)
    4. [assistant] `['goal']` "**Goal:** Integrate PostgreSQL into your FastAPI project.

Below is a lightweight “starter‑kit” that..." (score: 0.720)
    5. [assistant] `['goal']` "Build a web API using FastAPI" (score: 0.959)
    ... and 10 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [user] "Can you walk me through this?" (score: 1.000)
    2. [assistant] `['decision']` "**Decision:** Present a step‑by‑step walkthrough for a fresh FastAPI + PostgreSQL project that uses ..." (score: 1.300)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['constraint', 'goal']` "**Goal:** Build a web API using FastAPI.

Below are the basic steps to get you started, along with a..." (score: 1.274)
    5. [assistant] `['goal']` "**Goal:** Build a web API using FastAPI.

Below are a few alternatives you might consider if you’d l..." (score: 0.804)
    ... and 19 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.157)
  - Recalled content:
    1. [user] "Remind me of our technology choices so far." (score: 1.000)
    2. [assistant] `['constraint', 'goal']` "**Goal:** Build a web API using FastAPI.

Below are the basic steps to get you started, along with a..." (score: 1.157)
    3. [assistant] `['goal']` "**Goal:** Build a web API using FastAPI.

Below are a few alternatives you might consider if you’d l..." (score: 0.750)
    4. [assistant] `['goal']` "**Goal:** Build a web API using FastAPI (with PostgreSQL, async‑SQLAlchemy, Alembic, Uvicorn, and te..." (score: 0.742)
    5. [assistant] `['goal']` "**Goal:** Integrate PostgreSQL into your FastAPI project.

Below is a lightweight “starter‑kit” that..." (score: 0.682)
    ... and 30 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [assistant] `['goal']` "**Goal:** Build a web API with FastAPI and test it reliably.

Below is a quick “reason‑to‑why” map f..." (score: 1.300)
    2. [user] "Can you give me an example?" (score: 1.000)
    3. [assistant] `['decision']` "**Decision:** Give a minimal, self‑contained FastAPI example that

1. Uses an async SQLAlchemy engin..." (score: 1.300)
    4. [user] "What framework and database are we using?" (score: 1.000)
    5. [assistant] `['constraint', 'goal']` "**Goal:** Build a web API using FastAPI.

Below are the basic steps to get you started, along with a..." (score: 1.244)
    ... and 12 more items

---

## Consistency Analysis

- **10 turns**: 🟢 All iterations achieved 100% recall (highly consistent)
- **20 turns**: 🟢 All iterations achieved 100% recall (highly consistent)

## Recommendations

- ✅ Recall remains above 85% up to 20 turns.
- 📊 Optimal conversation length: **20 turns** (>85% recall with acceptable variance)
- ✅ Consolidation is working perfectly — zero stale facts in recall.

---

*Report generated by ACMS Evaluation Harness*