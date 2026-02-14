"""Report generation for ACMS evaluation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from examples.evaluation.metrics import EvaluationReport, TurnCountGroupMetrics


def generate_json_report(report: "EvaluationReport", output_path: Path) -> None:
    """Generate the full JSON report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)


def generate_markdown_report(report: "EvaluationReport", output_path: Path) -> None:
    """Generate the human-readable markdown report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []

    # Header
    lines.append("# ACMS Evaluation Report\n")
    lines.append(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total Runtime: {_format_duration(report.total_runtime_seconds)}\n")

    # Executive Summary
    lines.append("## Executive Summary\n")
    total_sessions = sum(len(g.iterations) for g in report.turn_count_groups)
    total_turns = sum(
        g.turn_count * len(g.iterations) for g in report.turn_count_groups
    )
    lines.append(f"- **Total sessions**: {total_sessions}")
    lines.append(f"- **Total turns evaluated**: {total_turns:,}")
    lines.append(f"- **Overall recall hit rate**: {report.overall_recall_hit_rate:.1%}")
    lines.append(f"- **Consistency score**: {report.overall_consistency_score:.2f}")
    lines.append(
        f"- **Optimal conversation length**: {report.optimal_conversation_length} turns\n"
    )

    # ACMS Overhead Analysis
    lines.append("## ACMS Overhead Analysis\n")
    if report.overall_avg_acms_overhead_ms > 0:
        lines.append(
            f"**ACMS adds ~{report.overall_avg_acms_overhead_ms:.0f}ms per turn on average.**\n"
        )
        lines.append(
            "| Turn Count | Avg ACMS Overhead | Avg (excl. Reflection) "
            "| Avg Recall | Avg Ingest (User) | Avg Ingest (Asst) |"
        )
        lines.append(
            "|------------|-------------------|------------------------"
            "|------------|-------------------|-------------------|"
        )
        for group in sorted(report.turn_count_groups, key=lambda g: g.turn_count):
            summaries = [i.latency_summary for i in group.iterations if i.latency_summary]
            if not summaries:
                continue
            n = len(summaries)
            avg_recall = sum(s.avg_recall_ms for s in summaries) / n
            avg_ingest_u = sum(s.avg_ingest_user_ms for s in summaries) / n
            avg_ingest_a = sum(s.avg_ingest_assistant_ms for s in summaries) / n
            lines.append(
                f"| {group.turn_count} | {group.avg_acms_overhead_ms:.0f}ms "
                f"| {group.avg_acms_overhead_ms_excl_reflection:.0f}ms "
                f"| {avg_recall:.0f}ms | {avg_ingest_u:.0f}ms | {avg_ingest_a:.0f}ms |"
            )
        lines.append("")
    else:
        lines.append("*No latency data available.*\n")

    # Consolidation Analysis (only if consolidation data is present)
    has_consolidation = any(
        i.consolidation_stats
        for g in report.turn_count_groups
        for i in g.iterations
    )
    if has_consolidation:
        lines.append("## Consolidation Analysis\n")
        lines.append(
            f"**Overall staleness rate: {report.overall_staleness_rate:.1%}** "
            f"(fraction of probes with stale/superseded keywords in recall)\n"
        )
        lines.append(
            f"**Overall consolidation ratio: {report.overall_consolidation_ratio:.2f}** "
            f"(superseded / total facts)\n"
        )
        lines.append(
            "| Turn Count | Avg Staleness | Avg Consolidation Ratio "
            "| Avg Active Facts | Avg Superseded Facts |"
        )
        lines.append(
            "|------------|---------------|-------------------------"
            "|------------------|----------------------|"
        )
        for group in sorted(report.turn_count_groups, key=lambda g: g.turn_count):
            stats_list = [
                i.consolidation_stats for i in group.iterations if i.consolidation_stats
            ]
            if not stats_list:
                continue
            n = len(stats_list)
            avg_active = sum(s.active_facts_count for s in stats_list) / n
            avg_superseded = sum(s.superseded_facts_count for s in stats_list) / n
            lines.append(
                f"| {group.turn_count} | {group.avg_staleness_rate:.0%} "
                f"| {group.avg_consolidation_ratio:.2f} "
                f"| {avg_active:.1f} | {avg_superseded:.1f} |"
            )
        lines.append("")

        # Interpretation guide
        if report.overall_staleness_rate == 0:
            lines.append(
                "> ✅ **Consolidation is working correctly** — "
                "no stale facts appear in recall.\n"
            )
        elif report.overall_staleness_rate <= 0.20:
            lines.append(
                "> ⚠️ **Minor staleness detected** — "
                "occasional stale keywords in recall, possibly before reflection has run.\n"
            )
        else:
            lines.append(
                "> ❌ **Consolidation needs attention** — "
                "superseded facts are regularly polluting recall. "
                "Check reflection prompts, episode boundaries, and dedup thresholds.\n"
            )

    # Configuration
    lines.append("## Configuration\n")
    lines.append(f"- Scenario: `{report.config.get('scenario', 'N/A')}`")
    lines.append(f"- Turn counts: {report.config.get('turn_counts', [])}")
    lines.append(
        f"- Iterations per turn count: {report.config.get('iterations_per_turn_count', 0)}"
    )
    lines.append(f"- Max concurrent: {report.config.get('max_concurrent', 0)}\n")

    # Summary Table
    lines.append("## Decision Persistence by Turn Count\n")
    lines.append(
        "| Turns | Iterations | Avg Recall Rate | Std Dev | Avg Score | Min | Max |"
    )
    lines.append("|-------|------------|-----------------|---------|-----------|-----|-----|")

    for group in sorted(report.turn_count_groups, key=lambda g: g.turn_count):
        lines.append(
            f"| {group.turn_count} | {len(group.iterations)} | "
            f"{group.avg_recall_hit_rate:.1%} | {group.std_recall_hit_rate:.2f} | "
            f"{group.avg_score:.2f} | {group.min_score:.2f} | {group.max_score:.2f} |"
        )

    lines.append("")

    # Detailed Results for each turn count
    lines.append("## Detailed Results\n")

    for group in sorted(report.turn_count_groups, key=lambda g: g.turn_count):
        lines.append(f"### {group.turn_count}-Turn Conversations\n")
        lines.append(f"- **Average recall hit rate**: {group.avg_recall_hit_rate:.1%}")
        lines.append(f"- **Standard deviation**: {group.std_recall_hit_rate:.3f}")
        lines.append(f"- **Score range**: {group.min_score:.2f} - {group.max_score:.2f}\n")

        # Show each iteration
        for iteration in group.iterations:
            status = "✅" if iteration.recall_hit_rate >= 0.9 else (
                "⚠️" if iteration.recall_hit_rate >= 0.7 else "❌"
            )
            lines.append(f"#### Iteration {iteration.iteration_id} {status}\n")
            lines.append(f"- Session ID: `{iteration.session_id}`")
            lines.append(f"- Recall Hit Rate: {iteration.recall_hit_rate:.1%}")
            lines.append(f"- Average Score: {iteration.avg_recall_score:.3f}")
            lines.append(f"- Time: {iteration.total_time_seconds:.1f}s")
            lines.append(f"- Episodes closed: {iteration.episodes_closed}")
            lines.append(f"- Facts extracted: {iteration.facts_extracted}")
            lines.append(f"- Tokens ingested: {iteration.tokens_ingested:,}")

            if iteration.latency_summary:
                ls = iteration.latency_summary
                lines.append(f"- Avg ACMS overhead: {ls.avg_total_acms_ms:.0f}ms/turn")
                lines.append(
                    f"- Avg ACMS overhead (excl reflection): "
                    f"{ls.avg_acms_ms_excluding_reflection:.0f}ms/turn"
                )
                lines.append(f"- Reflection turns: {ls.reflection_turn_count}")
                lines.append(f"- p95 ACMS overhead: {ls.p95_total_acms_ms:.0f}ms")

            if iteration.consolidation_stats:
                cs = iteration.consolidation_stats
                lines.append(
                    f"- Active facts: {cs.active_facts_count}, "
                    f"Superseded: {cs.superseded_facts_count}, "
                    f"Consolidation ratio: {cs.consolidation_ratio:.2f}"
                )
                lines.append(f"- Staleness rate: {cs.staleness_rate:.0%}")

            lines.append("")

            # Probe results
            if iteration.probe_results:
                lines.append("**Probe Results:**\n")
                for probe in iteration.probe_results:
                    found_str = "✅ YES" if probe.found else "❌ NO"
                    lines.append(f"- **Turn {probe.turn_number}**: \"{probe.query}\"")
                    lines.append(f"  - Expected: `{probe.expected_keywords}`")
                    lines.append(f"  - Found: {found_str} (score: {probe.best_score:.3f})")
                    if probe.excluded_keywords:
                        if probe.stale_found:
                            lines.append(
                                f"  - ❌ Stale keywords present: `{probe.stale_keywords_present}`"
                            )
                        else:
                            lines.append(
                                f"  - ✅ No stale keywords (excluded: `{probe.excluded_keywords}`)"
                            )

                    if probe.recalled_items:
                        lines.append("  - Recalled content:")
                        for i, item in enumerate(probe.recalled_items[:5], 1):
                            # Truncate long text
                            text = item.text[:100] + "..." if len(item.text) > 100 else item.text
                            markers = f" `{item.markers}`" if item.markers else ""
                            lines.append(
                                f"    {i}. [{item.role}]{markers} \"{text}\" "
                                f"(score: {item.score:.3f})"
                            )
                        if len(probe.recalled_items) > 5:
                            lines.append(
                                f"    ... and {len(probe.recalled_items) - 5} more items"
                            )
                    lines.append("")

            lines.append("---\n")

    # Consistency Analysis
    lines.append("## Consistency Analysis\n")

    for group in sorted(report.turn_count_groups, key=lambda g: g.turn_count):
        hit_rates = [i.recall_hit_rate for i in group.iterations]
        perfect_count = sum(1 for r in hit_rates if r == 1.0)
        high_count = sum(1 for r in hit_rates if r >= 0.9)

        if perfect_count == len(group.iterations):
            status = "🟢 All iterations achieved 100% recall (highly consistent)"
        elif high_count == len(group.iterations):
            status = f"🟡 All iterations achieved >90% recall ({high_count}/{len(group.iterations)})"
        elif group.std_recall_hit_rate < 0.1:
            status = f"🟡 Low variance (std={group.std_recall_hit_rate:.3f})"
        else:
            status = f"🔴 High variance (std={group.std_recall_hit_rate:.3f})"

        lines.append(f"- **{group.turn_count} turns**: {status}")

    lines.append("")

    # Recommendations
    lines.append("## Recommendations\n")

    # Find where recall starts degrading
    for group in sorted(report.turn_count_groups, key=lambda g: g.turn_count):
        if group.avg_recall_hit_rate < 0.85:
            lines.append(
                f"- ⚠️ Recall degrades below 85% at {group.turn_count} turns. "
                f"Consider shorter episodes or larger token budgets."
            )
            break
    else:
        lines.append(
            f"- ✅ Recall remains above 85% up to {max(g.turn_count for g in report.turn_count_groups)} turns."
        )

    # Consistency recommendation
    high_variance_groups = [
        g for g in report.turn_count_groups if g.std_recall_hit_rate > 0.15
    ]
    if high_variance_groups:
        turns = [g.turn_count for g in high_variance_groups]
        lines.append(
            f"- ⚠️ High variance detected at {turns} turns. "
            f"Results may be inconsistent."
        )

    # Optimal length
    lines.append(
        f"- 📊 Optimal conversation length: **{report.optimal_conversation_length} turns** "
        f"(>85% recall with acceptable variance)"
    )

    # Consolidation recommendations
    if has_consolidation:
        if report.overall_staleness_rate > 0.20:
            lines.append(
                "- ❌ **Staleness rate is high (>20%)** — consolidation is not effectively "
                "removing superseded facts from recall. Consider: shorter episodes "
                "(max_turns_per_episode), stronger consolidation prompts, or lower "
                "dedup thresholds."
            )
        elif report.overall_staleness_rate > 0:
            lines.append(
                f"- ⚠️ Staleness rate is {report.overall_staleness_rate:.0%} — "
                "some superseded facts appear in early probes before consolidation fires."
            )
        else:
            lines.append(
                "- ✅ Consolidation is working perfectly — zero stale facts in recall."
            )
        if report.overall_consolidation_ratio == 0:
            lines.append(
                "- ⚠️ Consolidation ratio is 0 — no facts were superseded. "
                "This may mean episodes are too long for consolidation to trigger, "
                "or the scenario does not require fact updates."
            )

    lines.append("")

    # Footer
    lines.append("---\n")
    lines.append("*Report generated by ACMS Evaluation Harness*")

    # Write to file
    with open(output_path, "w") as f:
        f.write("\n".join(lines))


def _format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def save_reports(report: "EvaluationReport", output_dir: str) -> tuple[Path, Path]:
    """Save both JSON and Markdown reports.

    Returns:
        Tuple of (json_path, markdown_path)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate timestamp and scenario slug for filenames
    timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
    scenario = report.config.get("scenario", "unknown")

    json_path = output_path / f"evaluation_report_{scenario}_{timestamp}.json"
    markdown_path = output_path / f"evaluation_summary_{scenario}_{timestamp}.md"

    generate_json_report(report, json_path)
    generate_markdown_report(report, markdown_path)

    # Also save as "latest" (scenario-scoped)
    latest_json = output_path / f"evaluation_report_{scenario}_latest.json"
    latest_md = output_path / f"evaluation_summary_{scenario}_latest.md"

    generate_json_report(report, latest_json)
    generate_markdown_report(report, latest_md)

    return json_path, markdown_path
