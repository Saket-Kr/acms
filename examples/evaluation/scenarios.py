"""Test scenario definitions for ACMS evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ScenarioTurn:
    """Definition of a turn in a scenario."""

    turn_type: Literal["setup", "filler", "probe"]
    message: str
    expected_keywords: list[str] = field(default_factory=list)


@dataclass
class Scenario:
    """A test scenario with defined turns."""

    name: str
    description: str
    turns: dict[int, ScenarioTurn] = field(default_factory=dict)

    def get_turn(self, turn_number: int) -> ScenarioTurn | None:
        """Get the turn definition for a specific turn number."""
        return self.turns.get(turn_number)

    def get_probes(self) -> list[tuple[int, ScenarioTurn]]:
        """Get all probe turns with their turn numbers."""
        return [
            (num, turn)
            for num, turn in sorted(self.turns.items())
            if turn.turn_type == "probe"
        ]


# Pool of filler messages for turns without specific scenarios
FILLER_MESSAGES = [
    "What do you think about that approach?",
    "Can you elaborate on that?",
    "What are the main considerations here?",
    "How would you implement that?",
    "What are the trade-offs?",
    "Can you give me an example?",
    "What's the best practice for this?",
    "Are there any alternatives?",
    "What should I watch out for?",
    "How does this compare to other options?",
    "What's the next step?",
    "Can you explain the reasoning?",
    "What are the prerequisites?",
    "How do I test this?",
    "What's the expected behavior?",
    "Are there any edge cases?",
    "How do I handle errors?",
    "What's the performance impact?",
    "Is this approach scalable?",
    "What documentation should I read?",
    "How do I debug this?",
    "What tools should I use?",
    "Can you walk me through this?",
    "What's the typical workflow?",
    "How long should this take?",
    "What are common mistakes?",
    "How do I verify this works?",
    "What's the recommended setup?",
    "Are there any dependencies?",
    "How do I integrate this?",
]


# Define test scenarios
DECISION_TRACKING = Scenario(
    name="decision_tracking",
    description="Test if decisions are recalled over time",
    turns={
        1: ScenarioTurn(
            "setup",
            "I need to build a web API. Let's use FastAPI as the framework.",
            [],
        ),
        2: ScenarioTurn(
            "setup",
            "For the database, I've decided to use PostgreSQL.",
            [],
        ),
        5: ScenarioTurn(
            "probe",
            "What framework are we using for the API?",
            ["FastAPI"],
        ),
        10: ScenarioTurn(
            "probe",
            "What database did we choose?",
            ["PostgreSQL"],
        ),
        15: ScenarioTurn(
            "probe",
            "Remind me of our technology choices so far.",
            ["FastAPI", "PostgreSQL"],
        ),
        20: ScenarioTurn(
            "probe",
            "What framework and database are we using?",
            ["FastAPI", "PostgreSQL"],
        ),
        30: ScenarioTurn(
            "probe",
            "Can you summarize our tech stack decisions?",
            ["FastAPI", "PostgreSQL"],
        ),
        40: ScenarioTurn(
            "probe",
            "What were our initial technology decisions?",
            ["FastAPI", "PostgreSQL"],
        ),
        50: ScenarioTurn(
            "probe",
            "I forgot - what backend technologies did we pick?",
            ["FastAPI", "PostgreSQL"],
        ),
        60: ScenarioTurn(
            "probe",
            "What was our database choice again?",
            ["PostgreSQL"],
        ),
        70: ScenarioTurn(
            "probe",
            "Remind me of the framework we're using.",
            ["FastAPI"],
        ),
        80: ScenarioTurn(
            "probe",
            "What tech stack decisions did we make at the start?",
            ["FastAPI", "PostgreSQL"],
        ),
    },
)


CONSTRAINT_AWARENESS = Scenario(
    name="constraint_awareness",
    description="Test if constraints are recalled when relevant",
    turns={
        1: ScenarioTurn(
            "setup",
            "Important constraint: We must never use raw SQL queries. Always use an ORM.",
            [],
        ),
        3: ScenarioTurn(
            "setup",
            "Another constraint: All API endpoints must require authentication.",
            [],
        ),
        8: ScenarioTurn(
            "probe",
            "How should I write database queries?",
            ["ORM", "raw SQL"],
        ),
        15: ScenarioTurn(
            "probe",
            "Can I create a public endpoint without auth?",
            ["authentication", "auth"],
        ),
        25: ScenarioTurn(
            "probe",
            "What are our coding constraints?",
            ["ORM", "authentication"],
        ),
        40: ScenarioTurn(
            "probe",
            "I want to write a quick SQL query directly. Is that okay?",
            ["ORM", "raw SQL"],
        ),
        60: ScenarioTurn(
            "probe",
            "Remind me of the rules we set for this project.",
            ["ORM", "authentication"],
        ),
        80: ScenarioTurn(
            "probe",
            "What constraints should I keep in mind?",
            ["ORM", "authentication"],
        ),
    },
)


FAILURE_MEMORY = Scenario(
    name="failure_memory",
    description="Test if failures are remembered to avoid repetition",
    turns={
        1: ScenarioTurn(
            "setup",
            "I tried using Redis for session storage but it failed because our hosting doesn't support it.",
            [],
        ),
        4: ScenarioTurn(
            "setup",
            "Error: The JWT library we tried had a security vulnerability. We switched to PyJWT.",
            [],
        ),
        10: ScenarioTurn(
            "probe",
            "Should we use Redis for caching?",
            ["Redis", "failed", "hosting"],
        ),
        20: ScenarioTurn(
            "probe",
            "What JWT library should we use?",
            ["PyJWT", "security", "vulnerability"],
        ),
        35: ScenarioTurn(
            "probe",
            "What issues did we encounter so far?",
            ["Redis", "JWT"],
        ),
        50: ScenarioTurn(
            "probe",
            "Have we had any problems with session storage?",
            ["Redis", "hosting"],
        ),
        70: ScenarioTurn(
            "probe",
            "Any security issues we should remember?",
            ["JWT", "security", "vulnerability"],
        ),
        80: ScenarioTurn(
            "probe",
            "What failures should we avoid repeating?",
            ["Redis", "JWT"],
        ),
    },
)


MULTI_FACT_TRACKING = Scenario(
    name="multi_fact_tracking",
    description="Test tracking multiple distinct facts",
    turns={
        1: ScenarioTurn(
            "setup",
            "My name is Alex and I'm building a project management tool.",
            [],
        ),
        3: ScenarioTurn(
            "setup",
            "The target users are small teams of 5-20 people.",
            [],
        ),
        5: ScenarioTurn(
            "setup",
            "We need to support real-time collaboration features.",
            [],
        ),
        7: ScenarioTurn(
            "setup",
            "The deadline for the MVP is March 15th.",
            [],
        ),
        9: ScenarioTurn(
            "setup",
            "Budget constraint: We can only use free or open-source tools.",
            [],
        ),
        20: ScenarioTurn(
            "probe",
            "What's my name and what am I building?",
            ["Alex", "project management"],
        ),
        30: ScenarioTurn(
            "probe",
            "Who are our target users?",
            ["small teams", "5-20"],
        ),
        40: ScenarioTurn(
            "probe",
            "What key features do we need?",
            ["real-time", "collaboration"],
        ),
        50: ScenarioTurn(
            "probe",
            "When is the MVP deadline?",
            ["March 15"],
        ),
        60: ScenarioTurn(
            "probe",
            "What's our budget situation?",
            ["free", "open-source"],
        ),
        70: ScenarioTurn(
            "probe",
            "Give me a summary of the project requirements.",
            ["Alex", "project management", "teams", "real-time"],
        ),
        80: ScenarioTurn(
            "probe",
            "What do you remember about my project?",
            ["Alex", "project management", "March 15", "open-source"],
        ),
    },
)


GOAL_TRACKING = Scenario(
    name="goal_tracking",
    description="Test if goals and objectives are tracked",
    turns={
        1: ScenarioTurn(
            "setup",
            "Goal: Build a REST API that can handle 1000 requests per second.",
            [],
        ),
        4: ScenarioTurn(
            "setup",
            "Goal: Achieve 99.9% uptime for the service.",
            [],
        ),
        7: ScenarioTurn(
            "setup",
            "Goal: Keep response times under 100ms for 95% of requests.",
            [],
        ),
        15: ScenarioTurn(
            "probe",
            "What are our performance goals?",
            ["1000 requests", "100ms"],
        ),
        25: ScenarioTurn(
            "probe",
            "What's our uptime target?",
            ["99.9%", "uptime"],
        ),
        40: ScenarioTurn(
            "probe",
            "What are we trying to achieve with this API?",
            ["1000 requests", "99.9%", "100ms"],
        ),
        60: ScenarioTurn(
            "probe",
            "Remind me of our performance requirements.",
            ["1000 requests", "uptime", "response time"],
        ),
        80: ScenarioTurn(
            "probe",
            "What goals did we set at the beginning?",
            ["1000 requests", "99.9%", "100ms"],
        ),
    },
)


# All scenarios
SCENARIOS: dict[str, Scenario] = {
    "decision_tracking": DECISION_TRACKING,
    "constraint_awareness": CONSTRAINT_AWARENESS,
    "failure_memory": FAILURE_MEMORY,
    "multi_fact_tracking": MULTI_FACT_TRACKING,
    "goal_tracking": GOAL_TRACKING,
}


def get_filler_message(turn_number: int) -> str:
    """Get a filler message for a turn that has no scenario definition."""
    return FILLER_MESSAGES[turn_number % len(FILLER_MESSAGES)]


def get_scenario(name: str) -> Scenario:
    """Get a scenario by name."""
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {name}. Available: {list(SCENARIOS.keys())}")
    return SCENARIOS[name]


def get_all_scenarios() -> list[Scenario]:
    """Get all available scenarios."""
    return list(SCENARIOS.values())
