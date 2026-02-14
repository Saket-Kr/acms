# ACMS Evaluation Report

Generated: 2026-02-10 19:28:41
Total Runtime: 6h 48m

## Executive Summary

- **Total sessions**: 16
- **Total turns evaluated**: 720
- **Overall recall hit rate**: 100.0%
- **Consistency score**: 1.00
- **Optimal conversation length**: 80 turns

## ACMS Overhead Analysis

**ACMS adds ~5253ms per turn on average.**

| Turn Count | Avg ACMS Overhead | Avg (excl. Reflection) | Avg Recall | Avg Ingest (User) | Avg Ingest (Asst) |
| ---------- | ----------------- | ---------------------- | ---------- | ----------------- | ----------------- |
| 10         | 5163ms            | 285ms                  | 30ms       | 2217ms            | 2916ms            |
| 20         | 4208ms            | 248ms                  | 39ms       | 3972ms            | 196ms             |
| 30         | 5529ms            | 269ms                  | 52ms       | 1133ms            | 4343ms            |
| 40         | 5238ms            | 251ms                  | 49ms       | 5008ms            | 181ms             |
| 50         | 5424ms            | 258ms                  | 49ms       | 4428ms            | 947ms             |
| 60         | 5073ms            | 277ms                  | 66ms       | 2938ms            | 2070ms            |
| 70         | 5889ms            | 324ms                  | 65ms       | 189ms             | 5636ms            |
| 80         | 5500ms            | 276ms                  | 64ms       | 246ms             | 5190ms            |

## Configuration

- Scenario: `decision_tracking`
- Turn counts: [10, 20, 30, 40, 50, 60, 70, 80]
- Iterations per turn count: 2
- Max concurrent: 1

## Decision Persistence by Turn Count

| Turns | Iterations | Avg Recall Rate | Std Dev | Avg Score | Min  | Max  |
| ----- | ---------- | --------------- | ------- | --------- | ---- | ---- |
| 10    | 2          | 100.0%          | 0.00    | 1.16      | 1.01 | 1.30 |
| 20    | 2          | 100.0%          | 0.00    | 1.10      | 1.06 | 1.15 |
| 30    | 2          | 100.0%          | 0.00    | 1.24      | 1.20 | 1.28 |
| 40    | 2          | 100.0%          | 0.00    | 1.19      | 1.06 | 1.33 |
| 50    | 2          | 100.0%          | 0.00    | 1.13      | 1.08 | 1.17 |
| 60    | 2          | 100.0%          | 0.00    | 1.31      | 1.05 | 1.56 |
| 70    | 2          | 100.0%          | 0.00    | 1.08      | 1.08 | 1.08 |
| 80    | 2          | 100.0%          | 0.00    | 1.16      | 1.12 | 1.20 |

## Detailed Results

### 10-Turn Conversations

- **Average recall hit rate**: 100.0%
- **Standard deviation**: 0.000
- **Score range**: 1.01 - 1.30

#### Iteration 1 ✅

- Session ID: `eval_10t_iter1_a4623dff`
- Recall Hit Rate: 100.0%
- Average Score: 1.011
- Time: 329.1s
- Episodes closed: 3
- Facts extracted: 10
- Tokens ingested: 3,670
- Avg ACMS overhead: 4731ms/turn
- Avg ACMS overhead (excl reflection): 253ms/turn
- Reflection turns: 3
- p95 ACMS overhead: 23515ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"

  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.001)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision']` "Decision: To build a web API, I will use FastAPI as the framework. Now let's set up the environment ..." (score: 1.001)
    3. [assistant] `['constraint']` "Constraint: When working with databases in FastAPI, make sure to properly handle exceptions that mig..." (score: 0.994)
    4. [assistant] `['decision']` "Decision: To use a database for our web API, we will go with PostgreSQL. First, let's install it by ..." (score: 0.887)
    5. [assistant] `['constraint']` "Exceptions should be properly handled in the code for error management." (score: 1.035)
       ... and 9 more items
- **Turn 10**: "What database did we choose?"

  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.022)
  - Recalled content:
    1. [user] "How do I test this?" (score: 1.000)
    2. [assistant] "To test your FastAPI application, you can follow these steps:

1. Run the FastAPI server in developm..." (score: 1.000)
   3. [user] "What database did we choose?" (score: 1.000)
   4. [assistant] `['constraint']` "Constraint: When working with databases in FastAPI, make sure to properly handle exceptions that mig..." (score: 0.984)
   5. [assistant] `['constraint']` "Constraint: When working with databases in FastAPI, make sure to properly handle exceptions that mig..." (score: 0.984)
   ... and 8 more items

---

#### Iteration 2 ✅

- Session ID: `eval_10t_iter2_aea26854`
- Recall Hit Rate: 100.0%
- Average Score: 1.300
- Time: 297.0s
- Episodes closed: 4
- Facts extracted: 14
- Tokens ingested: 3,479
- Avg ACMS overhead: 5595ms/turn
- Avg ACMS overhead (excl reflection): 316ms/turn
- Reflection turns: 4
- p95 ACMS overhead: 23500ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [assistant] `['decision']` "Decision: To connect a FastAPI web API with a PostgreSQL database, we will need to:

1. Install the ..." (score: 1.300)
   2. [user] "How do I verify this works?" (score: 1.000)
   3. [user] "How do I test this?" (score: 1.000)
   4. [assistant] "To test your FastAPI project with a PostgreSQL database, follow these steps:
2. Install the require..." (score: 1.000)
   5. [user] "What framework are we using for the API?" (score: 1.000)
   ... and 7 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [user] "What are common mistakes?" (score: 1.000)
    2. [user] "What are the main considerations here?" (score: 1.000)
    3. [assistant] `['goal']` "Goal: To test the FastAPI web API with PostgreSQL database connection.

To test your FastAPI web API..." (score: 1.300)
    4. [user] "Can you walk me through this?" (score: 1.000)
    5. [assistant] "Sure! To build a FastAPI web API with PostgreSQL, let's follow these steps:

1. Install necessary pa..." (score: 1.000)
   ... and 20 more items

---

### 20-Turn Conversations

- **Average recall hit rate**: 100.0%
- **Standard deviation**: 0.000
- **Score range**: 1.06 - 1.15

#### Iteration 1 ✅

- Session ID: `eval_20t_iter1_2c2fa275`
- Recall Hit Rate: 100.0%
- Average Score: 1.145
- Time: 622.2s
- Episodes closed: 5
- Facts extracted: 20
- Tokens ingested: 6,992
- Avg ACMS overhead: 4369ms/turn
- Avg ACMS overhead (excl reflection): 284ms/turn
- Reflection turns: 5
- p95 ACMS overhead: 21687ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 0.999)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision']` "Decision: To proceed with building a web API using FastAPI, follow these steps:

1. Install FastAPI ..." (score: 0.976)
   3. [assistant] `['decision']` "[assistant]
   Decision: To proceed with using PostgreSQL as the database for your web API, follow thes..." (score: 0.913)
   4. [assistant] `['decision']` "The user decided to build a web API using FastAPI." (score: 0.999)
   5. [assistant] `['decision']` "The user chose PostgreSQL as the database for their web API." (score: 0.979)
   ... and 9 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.145)
  - Recalled content:
    1. [user] "What are common mistakes?" (score: 1.000)
    2. [assistant] "When working with FastAPI, some common mistakes and pitfalls you might encounter include:

1. Not pr..." (score: 1.000)
   3. [user] "What database did we choose?" (score: 1.000)
   4. [assistant] `['decision']` "[assistant]
   Decision: To proceed with using PostgreSQL as the database for your web API, follow thes..." (score: 0.917)
   5. [assistant] `['decision']` "Decision: To proceed with building a web API using FastAPI, follow these steps:
2. Install FastAPI ..." (score: 0.830)
   ... and 20 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [user] "What do you think about that approach?" (score: 1.000)
    2. [assistant] `['decision']` "Decision: I believe that the approach you have outlined for building a web API using FastAPI and Pos..." (score: 1.300)
    3. [user] "How would you implement that?" (score: 1.000)
    4. [assistant] "To proceed with building a web API using FastAPI and PostgreSQL, follow these steps:

1. Install Fas..." (score: 1.000)
   5. [user] "Remind me of our technology choices so far." (score: 1.000)
   ... and 24 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.136)
  - Recalled content:
    1. [user] "What documentation should I read?" (score: 1.000)
    2. [assistant] "To help you make the most out of FastAPI and PostgreSQL for your web API, here are some resources yo..." (score: 1.000)
    3. [user] "What tools should I use?" (score: 1.000)
    4. [assistant] "To summarize, for building your web API using FastAPI and PostgreSQL, you'll need the following tool..." (score: 1.000)
    5. [user] "What are common mistakes?" (score: 1.000)
       ... and 21 more items

---

#### Iteration 2 ✅

- Session ID: `eval_20t_iter2_02bbc1bc`
- Recall Hit Rate: 100.0%
- Average Score: 1.059
- Time: 491.7s
- Episodes closed: 5
- Facts extracted: 20
- Tokens ingested: 5,712
- Avg ACMS overhead: 4047ms/turn
- Avg ACMS overhead (excl reflection): 213ms/turn
- Reflection turns: 5
- p95 ACMS overhead: 23893ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"

  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.063)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision']` "Decision: For building a web API, we will use FastAPI as the framework. Here are some resources you ..." (score: 0.995)
    3. [assistant] `['decision']` "[assistant] Decision: For the database you have chosen, we will utilize PostgreSQL. Here are some re..." (score: 0.961)
    4. [assistant] `['decision']` "The chosen framework for building a web API is FastAPI." (score: 1.063)
    5. [assistant] `['goal']` "The approach of using FastAPI and PostgreSQL is considered well-thought-out." (score: 1.023)
       ... and 9 more items
- **Turn 10**: "What database did we choose?"

  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.106)
  - Recalled content:
    1. [user] "How would you implement that?" (score: 1.000)
    2. [assistant] "To integrate PostgreSQL with FastAPI, follow these steps:

1. Install necessary dependencies:

```sh
..." (score: 1.000)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision']` "[assistant] Decision: For the database you have chosen, we will utilize PostgreSQL. Here are some re..." (score: 0.977)
    5. [assistant] `['decision']` "Decision: For building a web API, we will use FastAPI as the framework. Here are some resources you ..." (score: 0.882)
    ... and 22 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "What's the performance impact?" (score: 1.000)
    2. [assistant] "The choice of PostgreSQL as the database can have a positive impact on the performance of your FastA..." (score: 1.000)
    3. [user] "Can you explain the reasoning?" (score: 1.000)
    4. [assistant] "Certainly! Here is the reasoning behind my previous responses regarding PostgreSQL and FastAPI for b..." (score: 1.000)
    5. [user] "Remind me of our technology choices so far." (score: 1.000)
    ... and 33 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.067)
  - Recalled content:
    1. [user] "How do I debug this?" (score: 1.000)
    2. [user] "How do I test this?" (score: 1.000)
    3. [assistant] "To test a FastAPI application with PostgreSQL, you can follow these steps:

1. Write unit tests for ..." (score: 1.000)
    4. [user] "How do I verify this works?" (score: 1.000)
    5. [assistant] "To verify that your FastAPI application with PostgreSQL is functioning correctly, you can follow the..." (score: 1.000)
    ... and 32 more items

---

### 30-Turn Conversations

- **Average recall hit rate**: 100.0%
- **Standard deviation**: 0.000
- **Score range**: 1.20 - 1.28

#### Iteration 1 ✅

- Session ID: `eval_30t_iter1_bbcc5be6`
- Recall Hit Rate: 100.0%
- Average Score: 1.199
- Time: 882.7s
- Episodes closed: 9
- Facts extracted: 35
- Tokens ingested: 9,608
- Avg ACMS overhead: 5357ms/turn
- Avg ACMS overhead (excl reflection): 280ms/turn
- Reflection turns: 9
- p95 ACMS overhead: 22835ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.261)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision', 'goal']` "Decision: To build a web API using FastAPI, we will follow these steps:

1. Install FastAPI by runni..." (score: 1.261)
    3. [assistant] `['decision', 'goal']` "Decision: To use PostgreSQL as the database for our FastAPI web API, we will follow these additional..." (score: 1.209)
    4. [assistant] `['decision']` "The decision is to use FastAPI as the framework for building a web API." (score: 1.056)
    5. [assistant] `['decision']` "The decision is to use PostgreSQL as the database for the FastAPI web API." (score: 1.029)
    ... and 9 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.218)
  - Recalled content:
    1. [user] "How do I integrate this?" (score: 1.000)
    2. [assistant] "To integrate a web API using FastAPI with PostgreSQL as the database, follow these steps:

1. Make s..." (score: 1.000)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision', 'goal']` "Decision: To use PostgreSQL as the database for our FastAPI web API, we will follow these additional..." (score: 1.218)
    5. [assistant] `['decision', 'goal']` "Decision: To build a web API using FastAPI, we will follow these steps:

1. Install FastAPI by runni..." (score: 1.115)
    ... and 20 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.124)
  - Recalled content:
    1. [assistant] "To build a FastAPI web API with PostgreSQL as the database, follow these steps:

1. Install Python a..." (score: 1.000)
    2. [user] "Remind me of our technology choices so far." (score: 1.000)
    3. [assistant] `['decision', 'goal']` "Decision: To build a web API using FastAPI, we will follow these steps:

1. Install FastAPI by runni..." (score: 1.124)
    4. [assistant] `['decision', 'goal']` "Decision: To use PostgreSQL as the database for our FastAPI web API, we will follow these additional..." (score: 1.092)
    5. [assistant] `['decision']` "Decision: To build a FastAPI web API with PostgreSQL as the database, we will keep in mind some pote..." (score: 0.840)
    ... and 31 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.276)
  - Recalled content:
    1. [assistant] "To build a FastAPI web API with PostgreSQL, you will need to have the following prerequisites in pla..." (score: 1.000)
    2. [user] "How does this compare to other options?" (score: 1.000)
    3. [assistant] "When building a web API, there are several popular choices for both the web framework and database. ..." (score: 1.000)
    4. [user] "What framework and database are we using?" (score: 1.000)
    5. [assistant] `['decision', 'goal']` "Decision: To use PostgreSQL as the database for our FastAPI web API, we will follow these additional..." (score: 1.276)
    ... and 21 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.116)
  - Recalled content:
    1. [user] "What's the expected behavior?" (score: 1.000)
    2. [user] "Can you explain the reasoning?" (score: 1.000)
    3. [assistant] "To explain the reasoning, I'll break down the steps and goals in building a FastAPI web API with Pos..." (score: 1.000)
    4. [user] "How do I verify this works?" (score: 1.000)
    5. [assistant] "To verify that the FastAPI web API with PostgreSQL is working, follow these steps:

1. Install both ..." (score: 1.000)
    ... and 20 more items

---

#### Iteration 2 ✅

- Session ID: `eval_30t_iter2_efd8875a`
- Recall Hit Rate: 100.0%
- Average Score: 1.279
- Time: 1023.5s
- Episodes closed: 10
- Facts extracted: 40
- Tokens ingested: 11,615
- Avg ACMS overhead: 5701ms/turn
- Avg ACMS overhead (excl reflection): 258ms/turn
- Reflection turns: 10
- p95 ACMS overhead: 23185ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.600)
  - Recalled content:
    1. [assistant] `['decision', 'goal']` "Goal: Use PostgreSQL as the database for our FastAPI application.

Decision: I will search for infor..." (score: 1.600)
    2. [user] "What are common mistakes?" (score: 1.000)
    3. [user] "How do I integrate this?" (score: 1.000)
    4. [assistant] "To integrate FastAPI and PostgreSQL, you can follow these steps:

1. Install the required packages f..." (score: 1.000)
    5. [user] "What framework are we using for the API?" (score: 1.000)
    ... and 8 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.225)
  - Recalled content:
    1. [user] "How would you implement that?" (score: 1.000)
    2. [assistant] "To test the FastAPI application with PostgreSQL as the database, follow these steps:

1. Make sure y..." (score: 1.000)
    3. [user] "How do I integrate this?" (score: 1.000)
    4. [user] "What's the performance impact?" (score: 1.000)
    5. [assistant] "The performance of FastAPI is one of its key advantages. It is designed to be very fast, with speeds..." (score: 1.000)
    ... and 15 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.150)
  - Recalled content:
    1. [assistant] "To test your FastAPI application with PostgreSQL as the database, follow these steps:

1. Start the ..." (score: 1.000)
    2. [user] "Remind me of our technology choices so far." (score: 1.000)
    3. [assistant] `['decision', 'goal']` "Goal: Build a web API using FastAPI.

Decision: I will search for more information about FastAPI and..." (score: 1.150)
    4. [assistant] `['decision', 'goal']` "Goal: Use PostgreSQL as the database for our FastAPI application.

Decision: I will search for infor..." (score: 1.101)
    5. [assistant] `['decision']` "The decision was made to use PostgreSQL as the database for the FastAPI application." (score: 0.908)
    ... and 35 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.289)
  - Recalled content:
    1. [assistant] "To test your FastAPI application with PostgreSQL as the database, follow these steps:

1. Start the ..." (score: 1.000)
    2. [user] "How do I test this?" (score: 1.000)
    3. [assistant] "To test your FastAPI application with PostgreSQL as the database, follow these steps:

1. First, mak..." (score: 1.000)
    4. [user] "What framework and database are we using?" (score: 1.000)
    5. [assistant] `['decision', 'goal']` "Goal: Use PostgreSQL as the database for our FastAPI application.

Decision: I will search for infor..." (score: 1.289)
    ... and 17 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.131)
  - Recalled content:
    1. [assistant] "To build a web API using FastAPI and PostgreSQL, you have already set up the necessary steps to inte..." (score: 1.000)
    2. [user] "Can you summarize our tech stack decisions?" (score: 1.000)
    3. [assistant] `['decision', 'goal']` "Goal: Build a web API using FastAPI.

Decision: I will search for more information about FastAPI and..." (score: 1.131)
    4. [assistant] `['decision', 'goal']` "Goal: Use PostgreSQL as the database for our FastAPI application.

Decision: I will search for infor..." (score: 1.109)
    5. [assistant] `['constraint']` "Constraint: The user must replace 'your_postgres_host,' 'your_database_name,' 'your_username,' and '..." (score: 0.900)
    ... and 34 more items

---

### 40-Turn Conversations

- **Average recall hit rate**: 100.0%
- **Standard deviation**: 0.000
- **Score range**: 1.06 - 1.33

#### Iteration 1 ✅

- Session ID: `eval_40t_iter1_53e6f148`
- Recall Hit Rate: 100.0%
- Average Score: 1.056
- Time: 1367.8s
- Episodes closed: 10
- Facts extracted: 45
- Tokens ingested: 16,102
- Avg ACMS overhead: 5310ms/turn
- Avg ACMS overhead (excl reflection): 259ms/turn
- Reflection turns: 10
- p95 ACMS overhead: 28761ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.140)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision']` "Decision: To build a web API using FastAPI, we will follow these steps:

1. Install FastAPI and nece..." (score: 0.970)
    3. [assistant] `['decision']` "Decision: To use PostgreSQL as the database for our web API, we can follow these steps:

1. Install ..." (score: 0.913)
    4. [assistant] `['decision']` "FastAPI is chosen as the web API framework." (score: 1.140)
    5. [assistant] `['decision']` "Uvicorn is used to run the FastAPI application." (score: 1.105)
    ... and 9 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.104)
  - Recalled content:
    1. [user] "What are the trade-offs?" (score: 1.000)
    2. [assistant] "The trade-offs for using FastAPI with PostgreSQL as the database include:

**Advantages:**

1. **Fas..." (score: 1.000)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision']` "Decision: To use PostgreSQL as the database for our web API, we can follow these steps:

1. Install ..." (score: 0.929)
    5. [assistant] `['decision']` "Decision: To build a web API using FastAPI, we will follow these steps:

1. Install FastAPI and nece..." (score: 0.840)
    ... and 20 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "What are the prerequisites?" (score: 1.000)
    2. [user] "What should I watch out for?" (score: 1.000)
    3. [assistant] "When building a web API with FastAPI and PostgreSQL, there are some factors to keep in mind to ensur..." (score: 1.000)
    4. [user] "Remind me of our technology choices so far." (score: 1.000)
    5. [assistant] `['decision']` "Decision: To build a web API using FastAPI, we will follow these steps:

1. Install FastAPI and nece..." (score: 0.850)
    ... and 31 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.090)
  - Recalled content:
    1. [user] "Can you explain the reasoning?" (score: 1.000)
    2. [assistant] "To build a web API using FastAPI, we will follow these steps:

1. Install FastAPI and necessary depe..." (score: 1.000)
    3. [user] "What tools should I use?" (score: 1.000)
    4. [assistant] "To build a web API using FastAPI, you will need the following tools and software packages:
1. Python..." (score: 1.000)
    5. [user] "What's the next step?" (score: 1.000)
    ... and 41 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "What tools should I use?" (score: 1.000)
    2. [assistant] "To build a web API, you can use FastAPI as the framework and PostgreSQL as the database. Here's a re..." (score: 1.000)
    3. [user] "Can you summarize our tech stack decisions?" (score: 1.000)
    4. [assistant] `['decision']` "Decision: To build a web API using FastAPI, we will follow these steps:

1. Install FastAPI and nece..." (score: 0.818)
    5. [assistant] `['decision']` "Decision: To use PostgreSQL as the database for our web API, we can follow these steps:

1. Install ..." (score: 0.768)
    ... and 44 more items

- **Turn 40**: "What were our initial technology decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "What's the best practice for this?" (score: 1.000)
    2. [assistant] "To build a web API, you can follow these best practices:

1. Use FastAPI as your framework, which pr..." (score: 1.000)
    3. [user] "What are the prerequisites?" (score: 1.000)
    4. [assistant] "To build a web API using FastAPI with PostgreSQL, you will need the following prerequisites:

1. Pyt..." (score: 1.000)
    5. [user] "Is this approach scalable?" (score: 1.000)
    ... and 19 more items

---

#### Iteration 2 ✅

- Session ID: `eval_40t_iter2_d192d4db`
- Recall Hit Rate: 100.0%
- Average Score: 1.334
- Time: 1294.2s
- Episodes closed: 10
- Facts extracted: 45
- Tokens ingested: 15,344
- Avg ACMS overhead: 5166ms/turn
- Avg ACMS overhead (excl reflection): 243ms/turn
- Reflection turns: 10
- p95 ACMS overhead: 25963ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.345)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision', 'goal']` "Goal: Build a web API using FastAPI as the framework.

Decision: To achieve this goal, we can use th..." (score: 1.345)
    3. [assistant] `['goal']` "[assistant]
Goal: Use PostgreSQL as the database for the FastAPI web API.

To connect FastAPI with a..." (score: 0.904)
    4. [assistant] `['goal']` "The user decides to build a web API using FastAPI as the framework" (score: 1.075)
    5. [assistant] `['goal']` "The user decides to use PostgreSQL as the database for the FastAPI web API" (score: 0.995)
    ... and 9 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.277)
  - Recalled content:
    1. [user] "What are the main considerations here?" (score: 1.000)
    2. [assistant] "To summarize the main considerations when building a FastAPI web API with PostgreSQL:
1. Choose Fast..." (score: 1.000)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision', 'goal']` "Goal: To understand the reasoning behind building a web API using FastAPI and PostgreSQL.

Decision:..." (score: 1.277)
    5. [assistant] `['decision', 'goal']` "Goal: Build a web API using FastAPI as the framework.

Decision: To achieve this goal, we can use th..." (score: 1.165)
    ... and 21 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [user] "How does this compare to other options?" (score: 1.000)
    2. [user] "Can you explain the reasoning?" (score: 1.000)
    3. [assistant] `['decision']` "Sure! When choosing PostgreSQL as the database for a FastAPI web API, the following factors played a..." (score: 1.300)
    4. [user] "Remind me of our technology choices so far." (score: 1.000)
    5. [assistant] `['decision', 'goal']` "Goal: To understand the reasoning behind building a web API using FastAPI and PostgreSQL.

Decision:..." (score: 1.149)
    ... and 31 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.331)
  - Recalled content:
    1. [user] "Can you walk me through this?" (score: 1.000)
    2. [user] "What should I watch out for?" (score: 1.000)
    3. [user] "How do I debug this?" (score: 1.000)
    4. [assistant] "To help you understand how to debug your FastAPI application, I'll walk you through some common tool..." (score: 1.000)
    5. [user] "What framework and database are we using?" (score: 1.000)
    ... and 10 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.153)
  - Recalled content:
    1. [user] "Are there any edge cases?" (score: 1.000)
    2. [assistant] "Yes, here are some potential edge cases and solutions when building a web API using FastAPI and Post..." (score: 1.000)
    3. [user] "Can you summarize our tech stack decisions?" (score: 1.000)
    4. [assistant] `['decision', 'goal']` "Goal: To understand the reasoning behind building a web API using FastAPI and PostgreSQL.

Decision:..." (score: 1.153)
    5. [assistant] `['decision', 'goal']` "Goal: Build a web API using FastAPI as the framework.

Decision: To achieve this goal, we can use th..." (score: 1.138)
    ... and 9 more items

- **Turn 40**: "What were our initial technology decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.600)
  - Recalled content:
    1. [user] "What's the expected behavior?" (score: 1.000)
    2. [assistant] `['decision', 'goal']` "Goal: Provide an example of a FastAPI application with PostgreSQL as the database and using Pytest f..." (score: 1.600)
    3. [user] "What are the main considerations here?" (score: 1.000)
    4. [user] "What's the recommended setup?" (score: 1.000)
    5. [assistant] "To set up a FastAPI web API with PostgreSQL, follow these steps:

1. Install the required packages u..." (score: 1.000)
    ... and 14 more items

---

### 50-Turn Conversations

- **Average recall hit rate**: 100.0%
- **Standard deviation**: 0.000
- **Score range**: 1.08 - 1.17

#### Iteration 1 ✅

- Session ID: `eval_50t_iter1_21806f19`
- Recall Hit Rate: 100.0%
- Average Score: 1.171
- Time: 1571.4s
- Episodes closed: 13
- Facts extracted: 60
- Tokens ingested: 17,806
- Avg ACMS overhead: 5269ms/turn
- Avg ACMS overhead (excl reflection): 249ms/turn
- Reflection turns: 13
- p95 ACMS overhead: 22609ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.228)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision', 'goal']` "Decision: To build a web API using FastAPI, we will proceed with the following steps:

1. First, mak..." (score: 1.228)
    3. [assistant] `['decision']` "Decision: When considering using PostgreSQL as a database for your web API, there are some key trade..." (score: 0.927)
    4. [assistant] `['decision']` "Decision: To include a database in our project, we will use PostgreSQL. Here are some steps to insta..." (score: 0.907)
    5. [assistant] `['decision']` "FastAPI is chosen as the framework for building a web API." (score: 1.103)
    ... and 9 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [user] "What are the main considerations here?" (score: 1.000)
    2. [assistant] `['decision']` "Decision: To summarize, the main considerations for using FastAPI and PostgreSQL in this project inc..." (score: 1.300)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision', 'goal']` "Decision: To build a web API using FastAPI, we will proceed with the following steps:

1. First, mak..." (score: 1.131)
    5. [assistant] `['decision']` "Decision: When considering using PostgreSQL as a database for your web API, there are some key trade..." (score: 0.999)
    ... and 20 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.131)
  - Recalled content:
    1. [user] "What's the performance impact?" (score: 1.000)
    2. [assistant] "The performance impact of using FastAPI and PostgreSQL for a web API can be significant due to their..." (score: 1.000)
    3. [user] "What's the expected behavior?" (score: 1.000)
    4. [assistant] "The expected behavior when using FastAPI and PostgreSQL for a web API is high performance due to the..." (score: 1.000)
    5. [user] "Remind me of our technology choices so far." (score: 1.000)
    ... and 23 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.191)
  - Recalled content:
    1. [user] "How does this compare to other options?" (score: 1.000)
    2. [user] "How do I verify this works?" (score: 1.000)
    3. [assistant] "To verify that your FastAPI application is working as expected, you can follow these steps:

1. Ensu..." (score: 1.000)
    4. [user] "What are the main considerations here?" (score: 1.000)
    5. [assistant] "To test your FastAPI application with PostgreSQL as a database, the main considerations include:

1...." (score: 1.000)
    ... and 19 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.100)
  - Recalled content:
    1. [user] "What do you think about that approach?" (score: 1.000)
    2. [assistant] "The proposed approach to building a web API using FastAPI and PostgreSQL seems very effective, as bo..." (score: 1.000)
    3. [user] "Can you summarize our tech stack decisions?" (score: 1.000)
    4. [assistant] `['decision', 'goal']` "Decision: To build a web API using FastAPI, we will proceed with the following steps:

1. First, mak..." (score: 1.100)
    5. [assistant] `['decision']` "Decision: When considering using PostgreSQL as a database for your web API, there are some key trade..." (score: 0.856)
    ... and 15 more items

- **Turn 40**: "What were our initial technology decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.104)
  - Recalled content:
    1. [user] "How do I test this?" (score: 1.000)
    2. [assistant] "To test your FastAPI application with Pytest, follow these steps:

1. Install necessary dependencies..." (score: 1.000)
    3. [user] "How do I debug this?" (score: 1.000)
    4. [assistant] "To debug your FastAPI application, you can utilize a few methods:

1. **Python Debuggers**: Use a Py..." (score: 1.000)
    5. [user] "What's the typical workflow?" (score: 1.000)
    ... and 9 more items

- **Turn 50**: "I forgot - what backend technologies did we pick?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.141)
  - Recalled content:
    1. [user] "What are the main considerations here?" (score: 1.000)
    2. [assistant] "The main considerations when using FastAPI and PostgreSQL together for a web API project include:

1..." (score: 1.000)
    3. [user] "Are there any alternatives?" (score: 1.000)
    4. [assistant] "Yes, there are other web frameworks and databases that can be used in conjunction with FastAPI and P..." (score: 1.000)
    5. [user] "I forgot - what backend technologies did we pick?" (score: 1.000)
    ... and 24 more items

---

#### Iteration 2 ✅

- Session ID: `eval_50t_iter2_0875f5a2`
- Recall Hit Rate: 100.0%
- Average Score: 1.079
- Time: 1612.1s
- Episodes closed: 15
- Facts extracted: 64
- Tokens ingested: 19,407
- Avg ACMS overhead: 5580ms/turn
- Avg ACMS overhead (excl reflection): 267ms/turn
- Reflection turns: 14
- p95 ACMS overhead: 24595ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.028)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision']` "Decision: Based on your request, we will proceed with building a web API using the FastAPI framework..." (score: 1.028)
    3. [assistant] `['decision']` "Decision: To work with the PostgreSQL database in our FastAPI web API project, we will install the n..." (score: 0.890)
    4. [assistant] `['decision']` "The user has decided to use FastAPI for building a web API." (score: 1.027)
    5. [assistant] `['decision']` "An example of how to set up a FastAPI application with a PostgreSQL database was provided." (score: 0.995)
    ... and 9 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.144)
  - Recalled content:
    1. [user] "What are common mistakes?" (score: 1.000)
    2. [assistant] "When working with FastAPI and PostgreSQL, some common mistakes users might encounter include:

1. Fo..." (score: 1.000)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision']` "Decision: To work with the PostgreSQL database in our FastAPI web API project, we will install the n..." (score: 0.911)
    5. [assistant] `['decision']` "Decision: Based on your request, we will proceed with building a web API using the FastAPI framework..." (score: 0.873)
    ... and 20 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "Are there any alternatives?" (score: 1.000)
    2. [assistant] "To answer your question, there are indeed alternatives to FastAPI when it comes to building web APIs..." (score: 1.000)
    3. [user] "Can you walk me through this?" (score: 1.000)
    4. [assistant] "I'd be happy to help walk you through building a web API using FastAPI and PostgreSQL. Here's an out..." (score: 1.000)
    5. [user] "Remind me of our technology choices so far." (score: 1.000)
    ... and 12 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.083)
  - Recalled content:
    1. [user] "What's the best practice for this?" (score: 1.000)
    2. [user] "What should I watch out for?" (score: 1.000)
    3. [assistant] "To ensure a smooth development experience when building your FastAPI web API with PostgreSQL, keep t..." (score: 1.000)
    4. [user] "How does this compare to other options?" (score: 1.000)
    5. [assistant] "For building web APIs, FastAPI is a modern and high-performance choice, but it's not the only option..." (score: 1.000)
    ... and 23 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "How would you implement that?" (score: 1.000)
    2. [assistant] "To proceed with building a web API using FastAPI and PostgreSQL, follow these steps:

1. Install the..." (score: 1.000)
    3. [user] "Can you summarize our tech stack decisions?" (score: 1.000)
    4. [assistant] `['decision']` "Decision: Based on your request, we will proceed with building a web API using the FastAPI framework..." (score: 0.873)
    5. [assistant] `['decision']` "Decision: Based on your request, we will proceed with building a web API using the FastAPI framework..." (score: 0.854)
    ... and 5 more items

- **Turn 40**: "What were our initial technology decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "How would you implement that?" (score: 1.000)
    2. [user] "What are the trade-offs?" (score: 1.000)
    3. [user] "How do I test this?" (score: 1.000)
    4. [assistant] "To test the FastAPI application using PostgreSQL, you can use various testing tools and techniques. ..." (score: 1.000)
    5. [user] "What were our initial technology decisions?" (score: 1.000)
    ... and 6 more items

- **Turn 50**: "I forgot - what backend technologies did we pick?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [user] "How do I handle errors?" (score: 1.000)
    2. [assistant] `['decision']` "Decision: When it comes to handling errors in a FastAPI application, there are several ways you can ..." (score: 1.300)
    3. [user] "Are there any alternatives?" (score: 1.000)
    4. [assistant] "Yes, there are alternative solutions for building web APIs in Python. Three popular options are Flas..." (score: 1.000)
    5. [user] "Can you explain the reasoning?" (score: 1.000)
    ... and 11 more items

---

### 60-Turn Conversations

- **Average recall hit rate**: 100.0%
- **Standard deviation**: 0.000
- **Score range**: 1.05 - 1.56

#### Iteration 1 ✅

- Session ID: `eval_60t_iter1_7a7c101a`
- Recall Hit Rate: 100.0%
- Average Score: 1.052
- Time: 1823.6s
- Episodes closed: 17
- Facts extracted: 74
- Tokens ingested: 19,396
- Avg ACMS overhead: 5192ms/turn
- Avg ACMS overhead (excl reflection): 279ms/turn
- Reflection turns: 16
- p95 ACMS overhead: 21500ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.114)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

Here's some information about FastAPI: FastAP..." (score: 1.028)
    3. [assistant] `['decision']` "Decision: To create a FastAPI web API with a PostgreSQL database, we will need to install the necess..." (score: 0.903)
    4. [assistant] `['goal']` "The goal is to build a web API using FastAPI as the framework." (score: 1.114)
    5. [assistant] `['decision']` "To get started with FastAPI, you can create a new project and run the application using specific com..." (score: 1.031)
    ... and 9 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.145)
  - Recalled content:
    1. [user] "What's the next step?" (score: 1.000)
    2. [assistant] "The next step is to create a simple database model based on the example provided earlier and test th..." (score: 1.000)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision']` "Decision: To create a FastAPI web API with a PostgreSQL database, we will need to install the necess..." (score: 0.918)
    5. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

Here's some information about FastAPI: FastAP..." (score: 0.857)
    ... and 20 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "In using FastAPI for building a web API, there are some trade-offs to consider:

1. Learning curve: ..." (score: 1.000)
    2. [user] "Are there any dependencies?" (score: 1.000)
    3. [assistant] "To create a FastAPI web API with PostgreSQL as the database, you will need to install the following ..." (score: 1.000)
    4. [user] "Remind me of our technology choices so far." (score: 1.000)
    5. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

Here's some information about FastAPI: FastAP..." (score: 0.849)
    ... and 31 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.081)
  - Recalled content:
    1. [assistant] "The expected behavior for building a web API using FastAPI with PostgreSQL as the database is to fir..." (score: 1.000)
    2. [user] "What should I watch out for?" (score: 1.000)
    3. [assistant] "When building a web API with FastAPI, here are some things you might want to consider:

1. **Edge ca..." (score: 1.000)
    4. [user] "What's the typical workflow?" (score: 1.000)
    5. [assistant] "To build a web API using FastAPI, follow these steps:

1. Install FastAPI and required dependencies:..." (score: 1.000)
    ... and 16 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "The recommended setup for building a web API using FastAPI with a PostgreSQL database includes the f..." (score: 1.000)
    2. [user] "Can you summarize our tech stack decisions?" (score: 1.000)
    3. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

Here's some information about FastAPI: FastAP..." (score: 0.835)
    4. [assistant] `['goal']` "[assistant]
Goal: Build a web API using FastAPI as the framework.

The recommended setup for buildin..." (score: 0.835)
    5. [assistant] `['decision']` "Decision: To create a FastAPI web API with a PostgreSQL database, we will need to install the necess..." (score: 0.782)
    ... and 31 more items

- **Turn 40**: "What were our initial technology decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "What are the trade-offs?" (score: 1.000)
    2. [assistant] "The trade-offs of building a web API using FastAPI include:

1. Steeper learning curve compared to o..." (score: 1.000)
    3. [user] "What's the next step?" (score: 1.000)
    4. [assistant] "The next step in building a web API using FastAPI with a PostgreSQL database is setting up the neces..." (score: 1.000)
    5. [user] "What were our initial technology decisions?" (score: 1.000)
    ... and 23 more items

- **Turn 50**: "I forgot - what backend technologies did we pick?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "Yes, there are some dependencies needed for integrating FastAPI with PostgreSQL:

1. FastAPI - The m..." (score: 1.000)
    2. [user] "What do you think about that approach?" (score: 1.000)
    3. [assistant] "This approach seems well-structured and thorough, providing a clear guide on how to build a web API ..." (score: 1.000)
    4. [user] "How does this compare to other options?" (score: 1.000)
    5. [assistant] "In terms of learning curve, FastAPI has a slightly steeper learning curve compared to traditional we..." (score: 1.000)
    ... and 14 more items

- **Turn 60**: "What was our database choice again?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.076)
  - Recalled content:
    1. [assistant] "Yes, the approach is scalable given the use of FastAPI, which is designed for high performance and s..." (score: 1.000)
    2. [user] "What was our database choice again?" (score: 1.000)
    3. [assistant] `['decision']` "Decision: To create a FastAPI web API with a PostgreSQL database, we will need to install the necess..." (score: 0.885)
    4. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

Here's some information about FastAPI: FastAP..." (score: 0.805)
    5. [assistant] `['goal']` "[assistant]
Goal: Build a web API using FastAPI as the framework.

The recommended setup for buildin..." (score: 0.796)
    ... and 20 more items

---

#### Iteration 2 ✅

- Session ID: `eval_60t_iter2_72a95dfd`
- Recall Hit Rate: 100.0%
- Average Score: 1.563
- Time: 2009.7s
- Episodes closed: 15
- Facts extracted: 70
- Tokens ingested: 23,035
- Avg ACMS overhead: 4955ms/turn
- Avg ACMS overhead (excl reflection): 275ms/turn
- Reflection turns: 15
- p95 ACMS overhead: 24105ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.135)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision']` "Decision: I will help you build a FastAPI web API. Here is an example of how to set up your project ..." (score: 0.957)
    3. [assistant] `['decision']` "Decision: To include a database in your FastAPI web API, we will use PostgreSQL. Here is how to inst..." (score: 0.877)
    4. [assistant] `['decision']` "The user chose to use FastAPI as the web API framework." (score: 1.135)
    5. [assistant] `['decision']` "A code snippet was provided for querying data from a PostgreSQL database in the FastAPI project." (score: 1.001)
    ... and 8 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.132)
  - Recalled content:
    1. [user] "Is this approach scalable?" (score: 1.000)
    2. [assistant] "Yes, using FastAPI as your web API framework in combination with a robust database system like Postg..." (score: 1.000)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision']` "Decision: To include a database in your FastAPI web API, we will use PostgreSQL. Here is how to inst..." (score: 0.922)
    5. [assistant] `['decision']` "Decision: I will help you build a FastAPI web API. Here is an example of how to set up your project ..." (score: 0.839)
    ... and 21 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 2.000)
  - Recalled content:
    1. [user] "Can you explain the reasoning?" (score: 1.000)
    2. [assistant] `['decision', 'constraint', 'goal']` "Decision: The chosen web API framework is FastAPI, and PostgreSQL was selected as the database for t..." (score: 2.000)
    3. [user] "How do I verify this works?" (score: 1.000)
    4. [assistant] "To verify that your FastAPI web API connected to PostgreSQL is working correctly, you can follow the..." (score: 1.000)
    5. [user] "Remind me of our technology choices so far." (score: 1.000)
    ... and 33 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.800)
  - Recalled content:
    1. [user] "What tools should I use?" (score: 1.000)
    2. [assistant] "You have chosen FastAPI as your web API framework and PostgreSQL as your database management system...." (score: 1.000)
    3. [user] "What's the typical workflow?" (score: 1.000)
    4. [assistant] "The typical workflow for building a FastAPI web API with PostgreSQL as the database involves the fol..." (score: 1.000)
    5. [user] "What documentation should I read?" (score: 1.000)
    ... and 16 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.598)
  - Recalled content:
    1. [user] "How do I handle errors?" (score: 1.000)
    2. [assistant] "To handle errors in FastAPI, we can use the built-in exception handling mechanisms. Here's an exampl..." (score: 1.000)
    3. [user] "Can you summarize our tech stack decisions?" (score: 1.000)
    4. [assistant] `['decision', 'constraint', 'goal']` "Decision: The chosen web API framework is FastAPI, and PostgreSQL was selected as the database for t..." (score: 1.598)
    5. [assistant] `['decision', 'constraint', 'goal']` "Decision: The FastAPI web API should be able to query and display data from a PostgreSQL database up..." (score: 1.500)
    ... and 30 more items

- **Turn 40**: "What were our initial technology decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.556)
  - Recalled content:
    1. [user] "What are the prerequisites?" (score: 1.000)
    2. [assistant] "To set up a FastAPI web API with PostgreSQL, you will need:

1. Python 3.7 or later (<https://www.py..." (score: 1.000)
    3. [user] "Are there any dependencies?" (score: 1.000)
    4. [assistant] "Yes, for setting up a FastAPI web API with PostgreSQL, you will need the following dependencies:

1...." (score: 1.000)
    5. [user] "What are the main considerations here?" (score: 1.000)
    ... and 10 more items

- **Turn 50**: "I forgot - what backend technologies did we pick?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.601)
  - Recalled content:
    1. [user] "Can you give me an example?" (score: 1.000)
    2. [assistant] `['failure']` "Of course! Let's take a look at an example of how to create FastAPI routes for creating and updating..." (score: 1.200)
    3. [user] "I forgot - what backend technologies did we pick?" (score: 1.000)
    4. [assistant] `['decision', 'constraint', 'goal']` "Decision: The chosen web API framework is FastAPI, and PostgreSQL was selected as the database for t..." (score: 1.601)
    5. [assistant] `['decision', 'constraint', 'goal']` "Decision: The FastAPI web API should be able to query and display data from a PostgreSQL database up..." (score: 1.473)
    ... and 6 more items

- **Turn 60**: "What was our database choice again?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.680)
  - Recalled content:
    1. [user] "What's the next step?" (score: 1.000)
    2. [user] "What's the typical workflow?" (score: 1.000)
    3. [user] "What are common mistakes?" (score: 1.000)
    4. [assistant] "When using FastAPI with PostgreSQL, some common mistakes developers might encounter include:

1. Inc..." (score: 1.000)
    5. [user] "What was our database choice again?" (score: 1.000)
    ... and 15 more items

---

### 70-Turn Conversations

- **Average recall hit rate**: 100.0%
- **Standard deviation**: 0.000
- **Score range**: 1.08 - 1.08

#### Iteration 1 ✅

- Session ID: `eval_70t_iter1_d16207d8`
- Recall Hit Rate: 100.0%
- Average Score: 1.081
- Time: 3220.6s
- Episodes closed: 20
- Facts extracted: 85
- Tokens ingested: 29,626
- Avg ACMS overhead: 5991ms/turn
- Avg ACMS overhead (excl reflection): 357ms/turn
- Reflection turns: 19
- p95 ACMS overhead: 27290ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

To get started, you can create a new director..." (score: 1.300)
    2. [user] "For the database, I've decided to use PostgreSQL." (score: 1.000)
    3. [assistant] `['decision']` "Decision: To integrate a database with your FastAPI project, you can use SQLAlchemy, an Object Relat..." (score: 1.300)
    4. [user] "What are the prerequisites?" (score: 1.000)
    5. [user] "What's the expected behavior?" (score: 1.000)
    ... and 3 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 0.962)
  - Recalled content:
    1. [user] "What tools should I use?" (score: 1.000)
    2. [user] "What should I watch out for?" (score: 1.000)
    3. [assistant] "To build a robust and scalable web API using FastAPI, you should consider the following best practic..." (score: 1.000)
    4. [user] "What are the main considerations here?" (score: 1.000)
    5. [assistant] "The main considerations for building a web API using FastAPI are:
1. Writing clean, modular code tha..." (score: 1.000)
    ... and 16 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "The expected behavior of your FastAPI project, after integrating a PostgreSQL database using SQLAlch..." (score: 1.000)
    2. [user] "Remind me of our technology choices so far." (score: 1.000)
    3. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

To get started, you can create a new director..." (score: 0.837)
    4. [assistant] `['decision']` "Decision: To integrate a database with your FastAPI project, you can use SQLAlchemy, an Object Relat..." (score: 0.794)
    5. [assistant] `['constraint']` "It's necessary to set up a PostgreSQL server and get the connection string before using it with Fast..." (score: 0.868)
    ... and 22 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.088)
  - Recalled content:
    1. [user] "What's the next step?" (score: 1.000)
    2. [assistant] "To build a FastAPI project with PostgreSQL integration, follow these steps:

1. Set up a PostgreSQL ..." (score: 1.000)
    3. [user] "What framework and database are we using?" (score: 1.000)
    4. [assistant] `['goal']` "Goal: Building a web API using FastAPI as the framework and integrating it with a PostgreSQL databas..." (score: 1.024)
    5. [assistant] `['decision']` "Decision: To integrate a database with your FastAPI project, you can use SQLAlchemy, an Object Relat..." (score: 0.985)
    ... and 2 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "To learn more about using SQLAlchemy with your FastAPI project, you can refer to the following resou..." (score: 1.000)
    2. [user] "Can you give me an example?" (score: 1.000)
    3. [user] "How does this compare to other options?" (score: 1.000)
    4. [user] "How would you implement that?" (score: 1.000)
    5. [assistant] "To implement the integration of a database with FastAPI using SQLAlchemy, follow these steps:

1. Fi..." (score: 1.000)
    ... and 4 more items

- **Turn 40**: "What were our initial technology decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "To verify that FastAPI, SQLAlchemy, and PostgreSQL are working together in your project, you can per..." (score: 1.000)
    2. [user] "How do I debug this?" (score: 1.000)
    3. [assistant] "To debug your FastAPI application, follow these steps:

1. Check if there are any syntax errors or m..." (score: 1.000)
    4. [user] "What were our initial technology decisions?" (score: 1.000)
    5. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

To get started, you can create a new director..." (score: 0.776)
    ... and 5 more items

- **Turn 50**: "I forgot - what backend technologies did we pick?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "What's the performance impact?" (score: 1.000)
    2. [assistant] "Using FastAPI can provide a positive impact on performance compared to Express.js due to its built-i..." (score: 1.000)
    3. [user] "What are the main considerations here?" (score: 1.000)
    4. [assistant] "In this context, the main consideration is setting up a PostgreSQL server and obtaining its connecti..." (score: 1.000)
    5. [user] "What's the recommended setup?" (score: 1.000)
    ... and 37 more items

- **Turn 60**: "What was our database choice again?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [assistant] `['decision']` "Decision: To further elaborate on the trade-offs of using SQLAlchemy to integrate a database with yo..." (score: 1.300)
    2. [user] "Are there any edge cases?" (score: 1.000)
    3. [user] "How do I debug this?" (score: 1.000)
    4. [user] "How does this compare to other options?" (score: 1.000)
    5. [user] "What was our database choice again?" (score: 1.000)
    ... and 5 more items

- **Turn 70**: "Remind me of the framework we're using."
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.084)
  - Recalled content:
    1. [assistant] "To integrate SQLAlchemy for integrating your FastAPI project with a PostgreSQL database, you'll need..." (score: 1.000)
    2. [user] "What are common mistakes?" (score: 1.000)
    3. [assistant] "To handle errors effectively in your FastAPI project, consider the following best practices:

1. Cus..." (score: 1.000)
    4. [user] "Remind me of the framework we're using." (score: 1.000)
    5. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

To get started, you can create a new director..." (score: 0.938)
    ... and 12 more items

---

#### Iteration 2 ✅

- Session ID: `eval_70t_iter2_c0d426a6`
- Recall Hit Rate: 100.0%
- Average Score: 1.077
- Time: 2650.1s
- Episodes closed: 19
- Facts extracted: 85
- Tokens ingested: 27,772
- Avg ACMS overhead: 5788ms/turn
- Avg ACMS overhead (excl reflection): 292ms/turn
- Reflection turns: 18
- p95 ACMS overhead: 27234ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.109)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

To achieve this goal, we can start by install..." (score: 1.010)
    3. [assistant] `['decision']` "Decision: To integrate a database with your FastAPI project, you can use PostgreSQL as the database ..." (score: 0.872)
    4. [assistant] `['goal']` "User chooses to build a web API using FastAPI as the framework." (score: 1.109)
    5. [assistant] `['goal']` "User chooses to integrate PostgreSQL as the database management system." (score: 0.972)
    ... and 9 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 0.994)
  - Recalled content:
    1. [assistant] "To build a web API using FastAPI, follow these steps:

1. Install FastAPI using pip:

```bash
pip in..." (score: 1.000)
    2. [user] "What database did we choose?" (score: 1.000)
    3. [assistant] `['decision']` "Decision: To integrate a database with your FastAPI project, you can use PostgreSQL as the database ..." (score: 0.894)
    4. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

To achieve this goal, we can start by install..." (score: 0.839)
    5. [assistant] `['goal']` "User decides to use PostgreSQL for the database management system." (score: 0.994)
    ... and 20 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "To achieve the goal of building a web API with FastAPI, you need to watch out for the following:

1...." (score: 1.000)
    2. [user] "Can you walk me through this?" (score: 1.000)
    3. [assistant] "To create a web API using FastAPI as the framework and integrate it with PostgreSQL, follow these st..." (score: 1.000)
    4. [user] "Remind me of our technology choices so far." (score: 1.000)
    5. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

To achieve this goal, we can start by install..." (score: 0.830)
    ... and 17 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [user] "What do you think about that approach?" (score: 1.000)
    2. [assistant] `['goal']` "Goal: You have chosen PostgreSQL as your database management system for the web API project. This ch..." (score: 1.300)
    3. [user] "Can you walk me through this?" (score: 1.000)
    4. [assistant] "To build a web API using FastAPI and integrate it with PostgreSQL as the database management system,..." (score: 1.000)
    5. [user] "Are there any dependencies?" (score: 1.000)
    ... and 14 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "Building a basic FastAPI project with PostgreSQL integration can typically be completed in less than..." (score: 1.000)
    2. [user] "How would you implement that?" (score: 1.000)
    3. [assistant] "To achieve the goal of building a web API with FastAPI and integrating it with PostgreSQL, follow th..." (score: 1.000)
    4. [user] "Can you summarize our tech stack decisions?" (score: 1.000)
    5. [assistant] `['goal']` "Goal: You have chosen PostgreSQL as your database management system for the web API project. This ch..." (score: 0.853)
    ... and 32 more items

- **Turn 40**: "What were our initial technology decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [user] "Are there any alternatives?" (score: 1.000)
    2. [assistant] "There are several alternatives for handling errors in your FastAPI project, including:

1. Built-in ..." (score: 1.000)
    3. [user] "What are the main considerations here?" (score: 1.000)
    4. [assistant] "When considering the main considerations for implementing a FastAPI project with PostgreSQL, here ar..." (score: 1.000)
    5. [user] "What are the main considerations here?" (score: 1.000)
    ... and 21 more items

- **Turn 50**: "I forgot - what backend technologies did we pick?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "Creating a web API using FastAPI and integrating it with PostgreSQL involves several steps, some of ..." (score: 1.000)
    2. [user] "How would you implement that?" (score: 1.000)
    3. [assistant] "To create a web API with FastAPI and integrate it with PostgreSQL, follow these steps:

1. Install F..." (score: 1.000)
    4. [user] "I forgot - what backend technologies did we pick?" (score: 1.000)
    5. [assistant] `['goal']` "Goal: You have chosen PostgreSQL as your database management system for the web API project. This ch..." (score: 0.857)
    ... and 6 more items

- **Turn 60**: "What was our database choice again?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.200)
  - Recalled content:
    1. [user] "Are there any edge cases?" (score: 1.000)
    2. [assistant] `['failure']` "In terms of testing your FastAPI project integrated with PostgreSQL, here are some edge cases and su..." (score: 1.200)
    3. [user] "How do I debug this?" (score: 1.000)
    4. [user] "How would you implement that?" (score: 1.000)
    5. [user] "What was our database choice again?" (score: 1.000)
    ... and 10 more items

- **Turn 70**: "Remind me of the framework we're using."
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.089)
  - Recalled content:
    1. [assistant] "Yes, the approach using FastAPI and PostgreSQL for building a web API is generally considered scalab..." (score: 1.000)
    2. [user] "Are there any alternatives?" (score: 1.000)
    3. [assistant] "Yes, there are alternatives to using FastAPI and PostgreSQL for building a web API. Some popular opt..." (score: 1.000)
    4. [user] "Remind me of the framework we're using." (score: 1.000)
    5. [assistant] `['goal']` "Goal: Build a web API using FastAPI as the framework.

To achieve this goal, we can start by install..." (score: 0.949)
    ... and 9 more items

---

### 80-Turn Conversations

- **Average recall hit rate**: 100.0%
- **Standard deviation**: 0.000
- **Score range**: 1.12 - 1.20

#### Iteration 1 ✅

- Session ID: `eval_80t_iter1_daf3fc45`
- Recall Hit Rate: 100.0%
- Average Score: 1.121
- Time: 2567.6s
- Episodes closed: 22
- Facts extracted: 99
- Tokens ingested: 28,512
- Avg ACMS overhead: 5266ms/turn
- Avg ACMS overhead (excl reflection): 256ms/turn
- Reflection turns: 22
- p95 ACMS overhead: 22320ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.145)
  - Recalled content:
    1. [user] "What framework are we using for the API?" (score: 1.000)
    2. [assistant] `['decision', 'failure']` "Decision: To incorporate a PostgreSQL database with your web API, follow these steps:

1. Install th..." (score: 1.043)
    3. [assistant] `['decision']` "Decision: I will proceed with building a web API using the FastAPI framework for you.

Here's an exa..." (score: 1.036)
    4. [assistant] `['decision']` "The user has decided to use FastAPI as the web API framework." (score: 1.145)
    5. [assistant] `['decision']` "Uvicorn was chosen as the ASGI server for running the FastAPI application." (score: 1.042)
    ... and 9 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.076)
  - Recalled content:
    1. [user] "Are there any alternatives?" (score: 1.000)
    2. [assistant] "To build a web API using Python, there are several popular options available. Some of the most commo..." (score: 1.000)
    3. [user] "What database did we choose?" (score: 1.000)
    4. [assistant] `['decision', 'failure']` "Decision: To incorporate a PostgreSQL database with your web API, follow these steps:

1. Install th..." (score: 1.076)
    5. [assistant] `['decision']` "Decision: I will proceed with building a web API using the FastAPI framework for you.

Here's an exa..." (score: 0.845)
    ... and 21 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.200)
  - Recalled content:
    1. [user] "What's the recommended setup?" (score: 1.000)
    2. [user] "Can you elaborate on that?" (score: 1.000)
    3. [assistant] `['failure']` "Certainly! Here's a detailed explanation of using FastAPI with PostgreSQL for your web API:

1. Inst..." (score: 1.200)
    4. [user] "Remind me of our technology choices so far." (score: 1.000)
    5. [assistant] `['decision', 'failure']` "Decision: To incorporate a PostgreSQL database with your web API, follow these steps:

1. Install th..." (score: 0.945)
    ... and 5 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.134)
  - Recalled content:
    1. [assistant] "Performance impacts when using a PostgreSQL database with FastAPI can depend on several factors such..." (score: 1.000)
    2. [user] "Are there any edge cases?" (score: 1.000)
    3. [assistant] "When selecting a database for your FastAPI project, there are alternatives to consider. Here are som..." (score: 1.000)
    4. [user] "What framework and database are we using?" (score: 1.000)
    5. [assistant] `['decision', 'failure']` "Decision: To incorporate a PostgreSQL database with your web API, follow these steps:

1. Install th..." (score: 1.112)
    ... and 6 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.200)
  - Recalled content:
    1. [assistant] `['failure']` "To test your web API with PostgreSQL integration, follow these steps:

1. Install the required packa..." (score: 1.200)
    2. [user] "What's the expected behavior?" (score: 1.000)
    3. [user] "What's the expected behavior?" (score: 1.000)
    4. [user] "Can you walk me through this?" (score: 1.000)
    5. [user] "Can you summarize our tech stack decisions?" (score: 1.000)
    ... and 4 more items

- **Turn 40**: "What were our initial technology decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "Yes, combining FastAPI and PostgreSQL can lead to highly scalable web APIs due to their robust featu..." (score: 1.000)
    2. [user] "What were our initial technology decisions?" (score: 1.000)
    3. [assistant] `['decision', 'failure']` "Decision: To incorporate a PostgreSQL database with your web API, follow these steps:

1. Install th..." (score: 0.860)
    4. [assistant] `['decision']` "Decision: To provide a better understanding of using FastAPI and PostgreSQL, I will offer more infor..." (score: 0.773)
    5. [assistant] `['decision']` "Decision: I will proceed with building a web API using the FastAPI framework for you.

Here's an exa..." (score: 0.752)
    ... and 6 more items

- **Turn 50**: "I forgot - what backend technologies did we pick?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.200)
  - Recalled content:
    1. [user] "How do I handle errors?" (score: 1.000)
    2. [assistant] `['failure']` "To handle errors effectively in your FastAPI and PostgreSQL application, follow these steps:

1. Imp..." (score: 1.200)
    3. [user] "How would you implement that?" (score: 1.000)
    4. [assistant] `['failure']` "To incorporate a PostgreSQL database with your FastAPI application, follow these steps:

1. Install ..." (score: 1.200)
    5. [user] "I forgot - what backend technologies did we pick?" (score: 1.000)
    ... and 17 more items

- **Turn 60**: "What was our database choice again?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.052)
  - Recalled content:
    1. [assistant] "To test your FastAPI application with a PostgreSQL database, you can follow these steps:

1. Manual ..." (score: 1.000)
    2. [user] "What was our database choice again?" (score: 1.000)
    3. [assistant] `['decision', 'failure']` "Decision: To incorporate a PostgreSQL database with your web API, follow these steps:

1. Install th..." (score: 1.050)
    4. [assistant] `['decision']` "Decision: To provide a better understanding of using FastAPI and PostgreSQL, I will offer more infor..." (score: 0.893)
    5. [assistant] `['decision']` "Decision: I will proceed with building a web API using the FastAPI framework for you.

Here's an exa..." (score: 0.805)
    ... and 10 more items

- **Turn 70**: "Remind me of the framework we're using."
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.200)
  - Recalled content:
    1. [user] "Can you give me an example?" (score: 1.000)
    2. [assistant] `['failure']` "To fetch data from a PostgreSQL database using FastAPI, follow these steps:

1. Install the psycopg2..." (score: 1.200)
    3. [user] "What are the prerequisites?" (score: 1.000)
    4. [assistant] "To incorporate a PostgreSQL database with your FastAPI web API, you will need the following prerequi..." (score: 1.000)
    5. [user] "Remind me of the framework we're using." (score: 1.000)
    ... and 6 more items

- **Turn 80**: "What tech stack decisions did we make at the start?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.000)
  - Recalled content:
    1. [assistant] "The time it takes to build a FastAPI web application with PostgreSQL can vary significantly based on..." (score: 1.000)
    2. [user] "What tech stack decisions did we make at the start?" (score: 1.000)
    3. [assistant] `['decision', 'failure']` "Decision: To incorporate a PostgreSQL database with your web API, follow these steps:

1. Install th..." (score: 0.879)
    4. [assistant] `['decision']` "Decision: To provide a better understanding of using FastAPI and PostgreSQL, I will offer more infor..." (score: 0.801)
    5. [assistant] `['decision']` "Decision: To test your FastAPI application, there are several methods available. Here's an overview ..." (score: 0.788)
    ... and 6 more items

---

#### Iteration 2 ✅

- Session ID: `eval_80t_iter2_dbd6f278`
- Recall Hit Rate: 100.0%
- Average Score: 1.198
- Time: 2715.7s
- Episodes closed: 23
- Facts extracted: 110
- Tokens ingested: 31,626
- Avg ACMS overhead: 5734ms/turn
- Avg ACMS overhead (excl reflection): 296ms/turn
- Reflection turns: 23
- p95 ACMS overhead: 22628ms

**Probe Results:**

- **Turn 5**: "What framework are we using for the API?"
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.300)
  - Recalled content:
    1. [assistant] `['decision']` "[assistant] Decision: To incorporate a PostgreSQL database into your FastAPI web API, first we will ..." (score: 1.300)
    2. [user] "What's the performance impact?" (score: 1.000)
    3. [user] "What should I watch out for?" (score: 1.000)
    4. [assistant] "When using PostgreSQL with your FastAPI web API, it is essential to keep the following in mind:

1. ..." (score: 1.000)
    5. [user] "What framework are we using for the API?" (score: 1.000)
    ... and 8 more items

- **Turn 10**: "What database did we choose?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.069)
  - Recalled content:
    1. [user] "Are there any edge cases?" (score: 1.000)
    2. [user] "How does this compare to other options?" (score: 1.000)
    3. [assistant] "There are several popular web API frameworks available, each with its own strengths and trade-offs. ..." (score: 1.000)
    4. [user] "How long should this take?" (score: 1.000)
    5. [assistant] "Assuming you have already set up your PostgreSQL server and created a new database, building a basic..." (score: 1.000)
    ... and 20 more items

- **Turn 15**: "Remind me of our technology choices so far."
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.127)
  - Recalled content:
    1. [assistant] "The next step is to create a basic FastAPI application with a simple endpoint that returns a JSON re..." (score: 1.000)
    2. [user] "Are there any edge cases?" (score: 1.000)
    3. [assistant] "Yes, it's essential to keep several edge cases in mind when building a FastAPI web API with PostgreS..." (score: 1.000)
    4. [user] "How do I debug this?" (score: 1.000)
    5. [assistant] "To debug your FastAPI web API with PostgreSQL integration, you can use several methods:

1. **Inspec..." (score: 1.000)
    ... and 21 more items

- **Turn 20**: "What framework and database are we using?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.210)
  - Recalled content:
    1. [user] "How does this compare to other options?" (score: 1.000)
    2. [user] "Can you give me an example?" (score: 1.000)
    3. [assistant] "Certainly! To test your FastAPI web API, you can use tools like Postman or Curl. Here's how to test ..." (score: 1.000)
    4. [user] "What do you think about that approach?" (score: 1.000)
    5. [assistant] "The approach for building a FastAPI web API with PostgreSQL integration is efficient and practical. ..." (score: 1.000)
    ... and 26 more items

- **Turn 30**: "Can you summarize our tech stack decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.600)
  - Recalled content:
    1. [user] "Can you explain the reasoning?" (score: 1.000)
    2. [assistant] `['decision', 'goal']` "Decision: To help demonstrate the example, I will show you how to create a simple FastAPI applicatio..." (score: 1.600)
    3. [user] "Can you summarize our tech stack decisions?" (score: 1.000)
    4. [assistant] `['decision', 'goal']` "Decision: To help you build a FastAPI web API, first, I will set up a virtual environment and instal..." (score: 1.123)
    5. [assistant] `['decision']` "[assistant] Decision: To incorporate a PostgreSQL database into your FastAPI web API, first we will ..." (score: 0.797)
    ... and 29 more items

- **Turn 40**: "What were our initial technology decisions?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.074)
  - Recalled content:
    1. [user] "What's the recommended setup?" (score: 1.000)
    2. [user] "What documentation should I read?" (score: 1.000)
    3. [assistant] "To learn more about testing your FastAPI web API, you can refer to the following resources:

1. Offi..." (score: 1.000)
    4. [user] "Is this approach scalable?" (score: 1.000)
    5. [assistant] "Yes, the FastAPI approach with PostgreSQL integration is highly scalable due to its robust features ..." (score: 1.000)
    ... and 12 more items

- **Turn 50**: "I forgot - what backend technologies did we pick?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.125)
  - Recalled content:
    1. [assistant] "Yes, there are alternatives for each component in our tech stack. Here's a list of some popular alte..." (score: 1.000)
    2. [user] "How do I test this?" (score: 1.000)
    3. [assistant] "To test your FastAPI web API, you can use tools like Postman or Curl. Here's an example of testing u..." (score: 1.000)
    4. [user] "I forgot - what backend technologies did we pick?" (score: 1.000)
    5. [assistant] `['decision', 'goal']` "Decision: To help you build a FastAPI web API, first, I will set up a virtual environment and instal..." (score: 1.125)
    ... and 3 more items

- **Turn 60**: "What was our database choice again?"
  - Expected: `['PostgreSQL']`
  - Found: ✅ YES (score: 1.127)
  - Recalled content:
    1. [user] "What's the recommended setup?" (score: 1.000)
    2. [user] "What's the recommended setup?" (score: 1.000)
    3. [assistant] "To build a FastAPI web API, follow these steps:

1. Install Python 3.7+ and set up a virtual environ..." (score: 1.000)
    4. [user] "How do I verify this works?" (score: 1.000)
    5. [assistant] "To verify that your FastAPI web API with PostgreSQL integration is working correctly, you can use to..." (score: 1.000)
    ... and 7 more items

- **Turn 70**: "Remind me of the framework we're using."
  - Expected: `['FastAPI']`
  - Found: ✅ YES (score: 1.235)
  - Recalled content:
    1. [assistant] "Yes, there are other databases you can use with FastAPI instead of PostgreSQL, such as SQLite, MySQL..." (score: 1.000)
    2. [user] "What are the main considerations here?" (score: 1.000)
    3. [assistant] "The main considerations when connecting a FastAPI application to a PostgreSQL database include:

1. ..." (score: 1.000)
    4. [user] "Remind me of the framework we're using." (score: 1.000)
    5. [assistant] `['decision', 'goal']` "Decision: To help you understand how a FastAPI application works, I will walk you through creating a..." (score: 1.235)
    ... and 10 more items

- **Turn 80**: "What tech stack decisions did we make at the start?"
  - Expected: `['FastAPI', 'PostgreSQL']`
  - Found: ✅ YES (score: 1.112)
  - Recalled content:
    1. [assistant] "To build a FastAPI web API, you will need the following main tools:

1. Python 3 - The programming l..." (score: 1.000)
    2. [user] "What's the best practice for this?" (score: 1.000)
    3. [user] "What documentation should I read?" (score: 1.000)
    4. [assistant] "For understanding and utilizing PostgreSQL effectively, I recommend checking out the following resou..." (score: 1.000)
    5. [user] "How do I verify this works?" (score: 1.000)
    ... and 8 more items

---

## Consistency Analysis

- **10 turns**: 🟢 All iterations achieved 100% recall (highly consistent)
- **20 turns**: 🟢 All iterations achieved 100% recall (highly consistent)
- **30 turns**: 🟢 All iterations achieved 100% recall (highly consistent)
- **40 turns**: 🟢 All iterations achieved 100% recall (highly consistent)
- **50 turns**: 🟢 All iterations achieved 100% recall (highly consistent)
- **60 turns**: 🟢 All iterations achieved 100% recall (highly consistent)
- **70 turns**: 🟢 All iterations achieved 100% recall (highly consistent)
- **80 turns**: 🟢 All iterations achieved 100% recall (highly consistent)

## Recommendations

- ✅ Recall remains above 85% up to 80 turns.
- 📊 Optimal conversation length: **80 turns** (>85% recall with acceptable variance)

---

*Report generated by ACMS Evaluation Harness*
```
