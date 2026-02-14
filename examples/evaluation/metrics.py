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
    excluded_keywords: list[str] = field(default_factory=list)
    """Keywords that SHOULD NOT appear in recall (stale/superseded values)."""
    stale_found: bool = False
    """True if any excluded keyword was found in recall."""
    stale_keywords_present: list[str] = field(default_factory=list)
    """Which excluded keywords were actually found in recall."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
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
        if self.excluded_keywords:
            result["excluded_keywords"] = self.excluded_keywords
            result["stale_found"] = self.stale_found
            result["stale_keywords_present"] = self.stale_keywords_present
        return result


@dataclass
class TurnLatency:
    """ACMS latency breakdown for a single turn.

    All values are in milliseconds. Measured at the agent level by wrapping
    individual ACMS calls with ``time.perf_counter()``.
    """

    ingest_user_ms: int
    recall_ms: int
    ingest_assistant_ms: int
    ingest_facts_ms: int
    total_acms_ms: int
    llm_ms: int
    had_reflection: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "ingest_user_ms": self.ingest_user_ms,
            "recall_ms": self.recall_ms,
            "ingest_assistant_ms": self.ingest_assistant_ms,
            "ingest_facts_ms": self.ingest_facts_ms,
            "total_acms_ms": self.total_acms_ms,
            "llm_ms": self.llm_ms,
            "had_reflection": self.had_reflection,
        }


@dataclass
class LatencySummary:
    """Aggregated latency statistics for an iteration.

    Provides averages, percentiles, and a breakdown that separates reflection
    turns (which include an LLM call for fact extraction and are therefore
    significantly slower) from normal turns.
    """

    avg_total_acms_ms: float
    avg_ingest_user_ms: float
    avg_recall_ms: float
    avg_ingest_assistant_ms: float
    avg_ingest_facts_ms: float
    avg_llm_ms: float
    p50_total_acms_ms: float
    p95_total_acms_ms: float
    max_total_acms_ms: int
    reflection_turn_count: int
    avg_acms_ms_excluding_reflection: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "avg_total_acms_ms": round(self.avg_total_acms_ms, 1),
            "avg_ingest_user_ms": round(self.avg_ingest_user_ms, 1),
            "avg_recall_ms": round(self.avg_recall_ms, 1),
            "avg_ingest_assistant_ms": round(self.avg_ingest_assistant_ms, 1),
            "avg_ingest_facts_ms": round(self.avg_ingest_facts_ms, 1),
            "avg_llm_ms": round(self.avg_llm_ms, 1),
            "p50_total_acms_ms": round(self.p50_total_acms_ms, 1),
            "p95_total_acms_ms": round(self.p95_total_acms_ms, 1),
            "max_total_acms_ms": self.max_total_acms_ms,
            "reflection_turn_count": self.reflection_turn_count,
            "avg_acms_ms_excluding_reflection": round(self.avg_acms_ms_excluding_reflection, 1),
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
    latency: TurnLatency | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
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
        if self.latency:
            result["latency"] = self.latency.to_dict()
        return result


@dataclass
class ConsolidationStats:
    """Consolidation statistics for a single iteration."""

    active_facts_count: int
    superseded_facts_count: int
    total_facts_count: int
    consolidation_ratio: float
    """superseded / total facts (0 = no supersession, >0.5 = high churn)."""
    staleness_rate: float
    """Fraction of probes (with exclusions) where stale keywords were found."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "active_facts_count": self.active_facts_count,
            "superseded_facts_count": self.superseded_facts_count,
            "total_facts_count": self.total_facts_count,
            "consolidation_ratio": round(self.consolidation_ratio, 4),
            "staleness_rate": round(self.staleness_rate, 4),
        }


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
    latency_summary: LatencySummary | None = None
    consolidation_stats: ConsolidationStats | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
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
        if self.latency_summary:
            result["latency_summary"] = self.latency_summary.to_dict()
        if self.consolidation_stats:
            result["consolidation_stats"] = self.consolidation_stats.to_dict()
        return result


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

    @property
    def avg_acms_overhead_ms(self) -> float:
        """Average ACMS overhead per turn across all iterations."""
        summaries = [i.latency_summary for i in self.iterations if i.latency_summary]
        if not summaries:
            return 0.0
        return sum(s.avg_total_acms_ms for s in summaries) / len(summaries)

    @property
    def avg_acms_overhead_ms_excl_reflection(self) -> float:
        """Average ACMS overhead excluding reflection turns."""
        summaries = [i.latency_summary for i in self.iterations if i.latency_summary]
        if not summaries:
            return 0.0
        return sum(s.avg_acms_ms_excluding_reflection for s in summaries) / len(summaries)

    @property
    def avg_staleness_rate(self) -> float:
        """Average staleness rate across iterations (0 = perfect, 1 = all stale)."""
        stats = [i.consolidation_stats for i in self.iterations if i.consolidation_stats]
        if not stats:
            return 0.0
        return sum(s.staleness_rate for s in stats) / len(stats)

    @property
    def avg_consolidation_ratio(self) -> float:
        """Average consolidation ratio (superseded / total) across iterations."""
        stats = [i.consolidation_stats for i in self.iterations if i.consolidation_stats]
        if not stats:
            return 0.0
        return sum(s.consolidation_ratio for s in stats) / len(stats)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "turn_count": self.turn_count,
            "iteration_count": len(self.iterations),
            "avg_recall_hit_rate": round(self.avg_recall_hit_rate, 4),
            "std_recall_hit_rate": round(self.std_recall_hit_rate, 4),
            "avg_score": round(self.avg_score, 4),
            "std_score": round(self.std_score, 4),
            "min_score": round(self.min_score, 4),
            "max_score": round(self.max_score, 4),
            "avg_acms_overhead_ms": round(self.avg_acms_overhead_ms, 1),
            "avg_acms_overhead_ms_excl_reflection": round(self.avg_acms_overhead_ms_excl_reflection, 1),
            "iterations": [i.to_dict() for i in self.iterations],
        }
        if any(i.consolidation_stats for i in self.iterations):
            result["avg_staleness_rate"] = round(self.avg_staleness_rate, 4)
            result["avg_consolidation_ratio"] = round(self.avg_consolidation_ratio, 4)
        return result


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

    @property
    def overall_avg_acms_overhead_ms(self) -> float:
        """Overall average ACMS overhead per turn."""
        if not self.turn_count_groups:
            return 0.0
        values = [g.avg_acms_overhead_ms for g in self.turn_count_groups if g.avg_acms_overhead_ms > 0]
        if not values:
            return 0.0
        return sum(values) / len(values)

    @property
    def overall_staleness_rate(self) -> float:
        """Overall staleness rate across all turn count groups."""
        if not self.turn_count_groups:
            return 0.0
        rates = [g.avg_staleness_rate for g in self.turn_count_groups if any(
            i.consolidation_stats for i in g.iterations
        )]
        if not rates:
            return 0.0
        return sum(rates) / len(rates)

    @property
    def overall_consolidation_ratio(self) -> float:
        """Overall consolidation ratio across all turn count groups."""
        if not self.turn_count_groups:
            return 0.0
        ratios = [g.avg_consolidation_ratio for g in self.turn_count_groups if any(
            i.consolidation_stats for i in g.iterations
        )]
        if not ratios:
            return 0.0
        return sum(ratios) / len(ratios)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        summary: dict[str, Any] = {
            "overall_recall_hit_rate": round(self.overall_recall_hit_rate, 4),
            "overall_consistency_score": round(self.overall_consistency_score, 4),
            "optimal_conversation_length": self.optimal_conversation_length,
            "decision_persistence_curve": {
                str(k): round(v, 4) for k, v in self.decision_persistence_curve.items()
            },
            "overall_avg_acms_overhead_ms": round(self.overall_avg_acms_overhead_ms, 1),
        }
        has_consolidation = any(
            i.consolidation_stats
            for g in self.turn_count_groups
            for i in g.iterations
        )
        if has_consolidation:
            summary["overall_staleness_rate"] = round(self.overall_staleness_rate, 4)
            summary["overall_consolidation_ratio"] = round(self.overall_consolidation_ratio, 4)
        return {
            "metadata": {
                "generated_at": self.generated_at.isoformat(),
                "total_runtime_seconds": round(self.total_runtime_seconds, 2),
                "config": self.config,
            },
            "summary": summary,
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


def check_excluded_keywords_in_recall(
    recalled_items: list[RecalledItem], excluded_keywords: list[str]
) -> tuple[bool, list[str]]:
    """Check if any recalled item contains stale/excluded keywords.

    Returns:
        Tuple of (stale_found, stale_keywords_present)
    """
    if not excluded_keywords:
        return False, []

    stale_keywords_present: list[str] = []
    for kw in excluded_keywords:
        kw_lower = kw.lower()
        for item in recalled_items:
            if kw_lower in item.text.lower():
                stale_keywords_present.append(kw)
                break

    return bool(stale_keywords_present), stale_keywords_present


def calculate_staleness_rate(probe_results: list[ProbeResult]) -> float:
    """Calculate the fraction of probes with exclusions that had stale keywords.

    Only considers probes that have excluded_keywords defined.
    Returns 0.0 if no probes have exclusions.
    """
    probes_with_exclusions = [p for p in probe_results if p.excluded_keywords]
    if not probes_with_exclusions:
        return 0.0
    stale_count = sum(1 for p in probes_with_exclusions if p.stale_found)
    return stale_count / len(probes_with_exclusions)


def _percentile(sorted_values: list[int], pct: float) -> float:
    """Compute a percentile from a pre-sorted list of values.

    Uses nearest-rank method. ``pct`` should be between 0 and 1.
    """
    if not sorted_values:
        return 0.0
    idx = int(len(sorted_values) * pct)
    # Clamp to valid index range
    idx = min(idx, len(sorted_values) - 1)
    return float(sorted_values[idx])


def calculate_latency_summary(turn_metrics: list[TurnMetrics]) -> LatencySummary | None:
    """Calculate aggregated latency statistics from turn metrics.

    Turns without latency data are excluded. Returns None if no latency
    data is available.
    """
    latencies = [t.latency for t in turn_metrics if t.latency is not None]
    if not latencies:
        return None

    n = len(latencies)
    sorted_acms = sorted(lat.total_acms_ms for lat in latencies)

    non_reflection = [lat for lat in latencies if not lat.had_reflection]
    avg_excl_reflection = (
        sum(lat.total_acms_ms for lat in non_reflection) / len(non_reflection)
        if non_reflection
        else 0.0
    )

    return LatencySummary(
        avg_total_acms_ms=sum(lat.total_acms_ms for lat in latencies) / n,
        avg_ingest_user_ms=sum(lat.ingest_user_ms for lat in latencies) / n,
        avg_recall_ms=sum(lat.recall_ms for lat in latencies) / n,
        avg_ingest_assistant_ms=sum(lat.ingest_assistant_ms for lat in latencies) / n,
        avg_ingest_facts_ms=sum(lat.ingest_facts_ms for lat in latencies) / n,
        avg_llm_ms=sum(lat.llm_ms for lat in latencies) / n,
        p50_total_acms_ms=_percentile(sorted_acms, 0.50),
        p95_total_acms_ms=_percentile(sorted_acms, 0.95),
        max_total_acms_ms=sorted_acms[-1],
        reflection_turn_count=sum(1 for lat in latencies if lat.had_reflection),
        avg_acms_ms_excluding_reflection=avg_excl_reflection,
    )
