"""Main evaluation engine for ACMS."""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from examples.evaluation.metrics import (
    EvaluationReport,
    IterationResult,
    ProbeResult,
    RecalledItem,
    TurnCountGroupMetrics,
    TurnMetrics,
    calculate_avg_recall_score,
    calculate_recall_hit_rate,
    check_keywords_in_recall,
)
from examples.evaluation.scenarios import (
    Scenario,
    ScenarioTurn,
    get_all_scenarios,
    get_filler_message,
    get_scenario,
)
from examples.test_agent.agent import TestAgent
from examples.test_agent.config import AgentConfig


@dataclass
class EvaluatorConfig:
    """Configuration for the evaluator."""

    turn_counts: list[int] = field(default_factory=lambda: [10, 20, 30, 40, 50, 60, 70, 80])
    iterations_per_turn_count: int = 10
    max_concurrent: int = 5
    scenario_name: str | None = None  # None = use default scenario
    verbose: bool = False
    output_dir: str = "./evaluation_output"


class ConcurrencyLimiter:
    """Limits concurrent async operations using a semaphore."""

    def __init__(self, max_concurrent: int = 5):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_count = 0

    async def run(self, coro: Any) -> Any:
        """Run a coroutine with concurrency limiting."""
        async with self._semaphore:
            self._active_count += 1
            try:
                return await coro
            finally:
                self._active_count -= 1

    @property
    def active_count(self) -> int:
        """Number of currently active operations."""
        return self._active_count


class Evaluator:
    """Main evaluation engine."""

    def __init__(self, config: EvaluatorConfig):
        self.config = config
        self._limiter = ConcurrencyLimiter(config.max_concurrent)
        self._console = Console()
        self._scenario = self._get_scenario()

    def _get_scenario(self) -> Scenario:
        """Get the scenario to use for evaluation."""
        if self.config.scenario_name:
            return get_scenario(self.config.scenario_name)
        # Default to decision_tracking as the main scenario
        return get_scenario("decision_tracking")

    async def run_evaluation(self) -> EvaluationReport:
        """Run the full evaluation suite."""
        from datetime import datetime

        start_time = time.time()
        turn_count_groups: list[TurnCountGroupMetrics] = []

        self._console.print(f"\n[bold blue]ACMS Evaluation Starting[/bold blue]")
        self._console.print(f"Scenario: [green]{self._scenario.name}[/green]")
        self._console.print(f"Turn counts: {self.config.turn_counts}")
        self._console.print(f"Iterations per turn count: {self.config.iterations_per_turn_count}")
        self._console.print(f"Max concurrent: {self.config.max_concurrent}")
        self._console.print()

        total_sessions = len(self.config.turn_counts) * self.config.iterations_per_turn_count

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self._console,
        ) as progress:
            overall_task = progress.add_task(
                "[cyan]Overall progress", total=total_sessions
            )

            # Process each turn count group sequentially
            for turn_count in self.config.turn_counts:
                group_task = progress.add_task(
                    f"[yellow]{turn_count}-turn sessions",
                    total=self.config.iterations_per_turn_count,
                )

                # Run iterations for this turn count in parallel (with limiting)
                iteration_tasks = []
                for iteration_id in range(1, self.config.iterations_per_turn_count + 1):
                    task = self._limiter.run(
                        self._run_single_iteration(
                            turn_count=turn_count,
                            iteration_id=iteration_id,
                            scenario=self._scenario,
                        )
                    )
                    iteration_tasks.append(task)

                # Collect results as they complete
                iterations: list[IterationResult] = []
                for coro in asyncio.as_completed(iteration_tasks):
                    result = await coro
                    iterations.append(result)
                    progress.advance(group_task)
                    progress.advance(overall_task)

                    if self.config.verbose:
                        self._console.print(
                            f"  [dim]Iteration {result.iteration_id}: "
                            f"hit_rate={result.recall_hit_rate:.2%}, "
                            f"avg_score={result.avg_recall_score:.3f}[/dim]"
                        )

                # Sort iterations by ID for consistent ordering
                iterations.sort(key=lambda x: x.iteration_id)

                # Create group metrics
                group = TurnCountGroupMetrics(
                    turn_count=turn_count,
                    iterations=iterations,
                )
                turn_count_groups.append(group)

                progress.remove_task(group_task)

                # Print group summary
                self._console.print(
                    f"[green]✓[/green] {turn_count}-turn: "
                    f"avg_hit_rate={group.avg_recall_hit_rate:.2%}, "
                    f"avg_score={group.avg_score:.3f}, "
                    f"std={group.std_score:.3f}"
                )

        elapsed = time.time() - start_time

        report = EvaluationReport(
            generated_at=datetime.now(),
            total_runtime_seconds=elapsed,
            config={
                "turn_counts": self.config.turn_counts,
                "iterations_per_turn_count": self.config.iterations_per_turn_count,
                "max_concurrent": self.config.max_concurrent,
                "scenario": self._scenario.name,
            },
            turn_count_groups=turn_count_groups,
        )

        self._console.print()
        self._console.print(f"[bold green]Evaluation complete![/bold green]")
        self._console.print(f"Total time: {elapsed:.1f}s")
        self._console.print(f"Overall hit rate: {report.overall_recall_hit_rate:.2%}")
        self._console.print(f"Optimal conversation length: {report.optimal_conversation_length} turns")

        return report

    async def _run_single_iteration(
        self,
        turn_count: int,
        iteration_id: int,
        scenario: Scenario,
    ) -> IterationResult:
        """Run a single iteration (one conversation session)."""
        session_id = f"eval_{turn_count}t_iter{iteration_id}_{uuid.uuid4().hex[:8]}"

        # Create agent config with unique session
        agent_config = AgentConfig(
            session_id=session_id,
            debug=False,
            token_budget=2000,
        )

        agent = TestAgent(agent_config)
        await agent.initialize()

        turn_metrics: list[TurnMetrics] = []
        probe_results: list[ProbeResult] = []

        start_time = time.time()

        try:
            for turn_number in range(1, turn_count + 1):
                # Get message for this turn
                scenario_turn = scenario.get_turn(turn_number)
                if scenario_turn:
                    message = scenario_turn.message
                    turn_type = scenario_turn.turn_type
                    expected_keywords = scenario_turn.expected_keywords
                else:
                    message = get_filler_message(turn_number)
                    turn_type = "filler"
                    expected_keywords = []

                # Execute turn
                turn_start = time.time()
                response = await agent.chat(message)
                turn_elapsed_ms = int((time.time() - turn_start) * 1000)

                # Build recalled items list
                recalled_items = [
                    RecalledItem(
                        text=item.content,
                        score=item.score,
                        role=item.role.value,
                        markers=list(item.markers) if item.markers else [],
                    )
                    for item in response.recalled_items
                ]

                # Collect markers
                markers_in_recall = []
                for item in response.recalled_items:
                    if item.markers:
                        markers_in_recall.extend(item.markers)
                markers_in_recall = list(set(markers_in_recall))

                # Calculate recall tokens
                recall_tokens = sum(item.token_count for item in response.recalled_items)

                # Create turn metrics
                turn_metric = TurnMetrics(
                    turn_number=turn_number,
                    turn_type=turn_type,
                    message=message,
                    response_time_ms=turn_elapsed_ms,
                    recall_count=len(response.recalled_items),
                    recall_tokens=recall_tokens,
                    markers_in_recall=markers_in_recall,
                    recalled_items=recalled_items,
                )

                # If this is a probe, evaluate recall
                if turn_type == "probe" and expected_keywords:
                    found, best_score = check_keywords_in_recall(
                        recalled_items, expected_keywords
                    )
                    probe_result = ProbeResult(
                        turn_number=turn_number,
                        query=message,
                        expected_keywords=expected_keywords,
                        found=found,
                        best_score=best_score,
                        recalled_items=recalled_items,
                    )
                    turn_metric.probe_result = probe_result
                    probe_results.append(probe_result)

                turn_metrics.append(turn_metric)

            # Get final stats
            stats = await agent.get_stats()

        finally:
            await agent.close()

        total_time = time.time() - start_time

        return IterationResult(
            iteration_id=iteration_id,
            turn_count=turn_count,
            session_id=session_id,
            scenario_name=scenario.name,
            recall_hit_rate=calculate_recall_hit_rate(probe_results),
            avg_recall_score=calculate_avg_recall_score(probe_results),
            total_time_seconds=total_time,
            episodes_closed=stats.get("episodes", 0),
            facts_extracted=stats.get("facts", 0),
            tokens_ingested=stats.get("tokens_ingested", 0),
            probe_results=probe_results,
            turn_metrics=turn_metrics,
        )

    async def run_quick_test(self, turn_count: int = 10) -> IterationResult:
        """Run a quick single-iteration test for sanity checking."""
        self._console.print(f"\n[bold]Quick test: {turn_count} turns[/bold]")

        result = await self._run_single_iteration(
            turn_count=turn_count,
            iteration_id=1,
            scenario=self._scenario,
        )

        self._console.print(f"[green]✓[/green] Recall hit rate: {result.recall_hit_rate:.2%}")
        self._console.print(f"[green]✓[/green] Avg recall score: {result.avg_recall_score:.3f}")
        self._console.print(f"[green]✓[/green] Time: {result.total_time_seconds:.1f}s")
        self._console.print(f"[green]✓[/green] Episodes closed: {result.episodes_closed}")
        self._console.print(f"[green]✓[/green] Facts extracted: {result.facts_extracted}")

        if result.probe_results:
            self._console.print("\n[bold]Probe results:[/bold]")
            for probe in result.probe_results:
                status = "[green]✓[/green]" if probe.found else "[red]✗[/red]"
                self._console.print(
                    f"  {status} Turn {probe.turn_number}: '{probe.query[:50]}...' "
                    f"(score: {probe.best_score:.3f})"
                )
                if self.config.verbose and probe.recalled_items:
                    for item in probe.recalled_items[:3]:
                        self._console.print(
                            f"      [dim][{item.role}] {item.text[:60]}... "
                            f"(score: {item.score:.3f})[/dim]"
                        )

        return result
