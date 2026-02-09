"""Metric types and calculation for ACMS evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RecalledItem:
    """A single recalled item with its details."""

    text: str
    score: float
    role: str
    markers: list[str] = field(default_factory=list)


@dataclass
class ProbeResult:
    """Result of a single probe query."""

    turn_number: int
    query: str
    expected_keywords: list[str]
    found: bool
    best_score: float
    recalled_items: list[RecalledItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "turn_number": self.turn_number,
            "query": self.query,
            "expected_keywords": self.expected_keywords,
            "found": self.found,
            "best_score": self.best_score,
            "recalled_content": [
                {"text": item.text, "score": item.score, "role": item.role, "markers": item.markers}
                for item in self.recalled_items
            ],
        }


@dataclass
class TurnMetrics:
    """Metrics collected for a single turn."""

    turn_number: int
    turn_type: str  # "setup", "filler", "probe"
    message: str
    response_time_ms: int
    recall_count: int
    recall_tokens: int
    markers_in_recall: list[str] = field(default_factory=list)
    recalled_items: list[RecalledItem] = field(default_factory=list)
    # For probes only
    probe_result: ProbeResult | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "turn_number": self.turn_number,
            "turn_type": self.turn_type,
            "message": self.message,
            "response_time_ms": self.response_time_ms,
            "recall_count": self.recall_count,
            "recall_tokens": self.recall_tokens,
            "markers_in_recall": self.markers_in_recall,
        }
        if self.probe_result:
            result["probe_result"] = self.probe_result.to_dict()
        return result


@dataclass
class IterationResult:
    """Result of a single iteration (one conversation session)."""

    iteration_id: int
    turn_count: int
    session_id: str
    scenario_name: str
    recall_hit_rate: float
    avg_recall_score: float
    total_time_seconds: float
    episodes_closed: int
    facts_extracted: int
    tokens_ingested: int
    probe_results: list[ProbeResult] = field(default_factory=list)
    turn_metrics: list[TurnMetrics] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "iteration_id": self.iteration_id,
            "turn_count": self.turn_count,
            "session_id": self.session_id,
            "scenario_name": self.scenario_name,
            "recall_hit_rate": self.recall_hit_rate,
            "avg_recall_score": self.avg_recall_score,
            "total_time_seconds": self.total_time_seconds,
            "episodes_closed": self.episodes_closed,
            "facts_extracted": self.facts_extracted,
            "tokens_ingested": self.tokens_ingested,
            "probe_results": [p.to_dict() for p in self.probe_results],
            "turn_metrics": [t.to_dict() for t in self.turn_metrics],
        }


@dataclass
class TurnCountGroupMetrics:
    """Aggregated metrics for all iterations at a specific turn count."""

    turn_count: int
    iterations: list[IterationResult] = field(default_factory=list)

    @property
    def avg_recall_hit_rate(self) -> float:
        """Average recall hit rate across iterations."""
        if not self.iterations:
            return 0.0
        return sum(i.recall_hit_rate for i in self.iterations) / len(self.iterations)

    @property
    def std_recall_hit_rate(self) -> float:
        """Standard deviation of recall hit rate."""
        if len(self.iterations) < 2:
            return 0.0
        avg = self.avg_recall_hit_rate
        variance = sum((i.recall_hit_rate - avg) ** 2 for i in self.iterations) / len(
            self.iterations
        )
        return variance**0.5

    @property
    def avg_score(self) -> float:
        """Average recall score across iterations."""
        if not self.iterations:
            return 0.0
        return sum(i.avg_recall_score for i in self.iterations) / len(self.iterations)

    @property
    def std_score(self) -> float:
        """Standard deviation of recall scores."""
        if len(self.iterations) < 2:
            return 0.0
        avg = self.avg_score
        variance = sum((i.avg_recall_score - avg) ** 2 for i in self.iterations) / len(
            self.iterations
        )
        return variance**0.5

    @property
    def min_score(self) -> float:
        """Minimum recall score across iterations."""
        if not self.iterations:
            return 0.0
        return min(i.avg_recall_score for i in self.iterations)

    @property
    def max_score(self) -> float:
        """Maximum recall score across iterations."""
        if not self.iterations:
            return 0.0
        return max(i.avg_recall_score for i in self.iterations)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "turn_count": self.turn_count,
            "iteration_count": len(self.iterations),
            "avg_recall_hit_rate": round(self.avg_recall_hit_rate, 4),
            "std_recall_hit_rate": round(self.std_recall_hit_rate, 4),
            "avg_score": round(self.avg_score, 4),
            "std_score": round(self.std_score, 4),
            "min_score": round(self.min_score, 4),
            "max_score": round(self.max_score, 4),
            "iterations": [i.to_dict() for i in self.iterations],
        }


@dataclass
class EvaluationReport:
    """Complete evaluation report."""

    generated_at: datetime
    total_runtime_seconds: float
    config: dict[str, Any]
    turn_count_groups: list[TurnCountGroupMetrics] = field(default_factory=list)

    @property
    def overall_recall_hit_rate(self) -> float:
        """Overall average recall hit rate across all turn counts."""
        if not self.turn_count_groups:
            return 0.0
        return sum(g.avg_recall_hit_rate for g in self.turn_count_groups) / len(
            self.turn_count_groups
        )

    @property
    def overall_consistency_score(self) -> float:
        """Overall consistency (1 - average std dev)."""
        if not self.turn_count_groups:
            return 1.0
        avg_std = sum(g.std_recall_hit_rate for g in self.turn_count_groups) / len(
            self.turn_count_groups
        )
        return max(0.0, 1.0 - avg_std)

    @property
    def optimal_conversation_length(self) -> int:
        """Find the highest turn count with >85% recall rate."""
        for group in sorted(self.turn_count_groups, key=lambda g: -g.turn_count):
            if group.avg_recall_hit_rate >= 0.85:
                return group.turn_count
        # Default to lowest if none meet threshold
        if self.turn_count_groups:
            return min(g.turn_count for g in self.turn_count_groups)
        return 10

    @property
    def decision_persistence_curve(self) -> dict[int, float]:
        """Map of turn_count -> recall_hit_rate."""
        return {g.turn_count: g.avg_recall_hit_rate for g in self.turn_count_groups}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "metadata": {
                "generated_at": self.generated_at.isoformat(),
                "total_runtime_seconds": round(self.total_runtime_seconds, 2),
                "config": self.config,
            },
            "summary": {
                "overall_recall_hit_rate": round(self.overall_recall_hit_rate, 4),
                "overall_consistency_score": round(self.overall_consistency_score, 4),
                "optimal_conversation_length": self.optimal_conversation_length,
                "decision_persistence_curve": {
                    str(k): round(v, 4) for k, v in self.decision_persistence_curve.items()
                },
            },
            "turn_count_groups": [g.to_dict() for g in self.turn_count_groups],
        }


def calculate_recall_hit_rate(probe_results: list[ProbeResult]) -> float:
    """Calculate the percentage of probes that found expected content."""
    if not probe_results:
        return 1.0  # No probes = perfect (vacuously true)
    hits = sum(1 for p in probe_results if p.found)
    return hits / len(probe_results)


def calculate_avg_recall_score(probe_results: list[ProbeResult]) -> float:
    """Calculate average best score across probes."""
    if not probe_results:
        return 0.0
    return sum(p.best_score for p in probe_results) / len(probe_results)


def check_keywords_in_recall(
    recalled_items: list[RecalledItem], keywords: list[str]
) -> tuple[bool, float]:
    """Check if any recalled item contains the expected keywords.

    Returns:
        Tuple of (found, best_score)
    """
    if not keywords:
        return True, 1.0  # No keywords to check = success

    best_score = 0.0
    found = False

    for item in recalled_items:
        text_lower = item.text.lower()
        if any(kw.lower() in text_lower for kw in keywords):
            found = True
            best_score = max(best_score, item.score)

    return found, best_score
