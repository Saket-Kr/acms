"""CLI interface for the test agent."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    from acms.models import ContextItem

    from examples.test_agent.agent import AgentResponse

console = Console()


def print_welcome(session_id: str, is_new: bool) -> None:
    """Print welcome message."""
    status = "new" if is_new else "resumed"
    console.print(
        Panel(
            f"[bold blue]ACMS Test Agent[/bold blue]\n"
            f"Session: [green]{session_id}[/green] ({status})\n"
            f"Type [yellow]/help[/yellow] for commands",
            title="Welcome",
            border_style="blue",
        )
    )


def print_help() -> None:
    """Print help message."""
    help_text = """
[bold]Available Commands:[/bold]

  [yellow]/stats[/yellow]         Show session statistics
  [yellow]/episode[/yellow]       Close current episode manually
  [yellow]/recall <query>[/yellow] Test recall with a query
  [yellow]/debug[/yellow]         Toggle debug mode (show recalled context)
  [yellow]/clear[/yellow]         Start a new session (not implemented)
  [yellow]/help[/yellow]          Show this help message
  [yellow]/quit[/yellow]          Exit the agent

[bold]Tips:[/bold]
- Start messages with "Decision:", "Constraint:", "Goal:", or "Failed:" to mark them
- Use the remember tool by asking the agent to remember something
- Check /stats to see how many turns/episodes/facts exist
"""
    console.print(Panel(help_text, title="Help", border_style="cyan"))


def print_stats(stats: dict) -> None:
    """Print session statistics."""
    table = Table(title="Session Statistics", border_style="green")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Session ID", str(stats.get("session_id", "N/A")))
    table.add_row("Total Turns", str(stats.get("turns", 0)))
    table.add_row("Total Episodes", str(stats.get("episodes", 0)))
    table.add_row("Total Facts", str(stats.get("facts", 0)))
    table.add_row("Open Episode", str(stats.get("open_episode", "None")))
    table.add_row("Open Episode Turns", str(stats.get("open_episode_turns", 0)))
    table.add_row("Tokens Ingested", str(stats.get("tokens_ingested", 0)))

    console.print(table)


def print_recall_results(items: list["ContextItem"], query: str) -> None:
    """Print recall results."""
    console.print(f"\n[bold]Recall results for:[/bold] '{query}'")
    console.print(f"[dim]Found {len(items)} items[/dim]\n")

    for i, item in enumerate(items, 1):
        markers = f" [yellow][{', '.join(item.markers)}][/yellow]" if item.markers else ""
        score = f"[dim](score: {item.score:.2f})[/dim]"

        console.print(f"[bold]{i}. [{item.role.value}]{markers}[/bold] {score}")
        console.print(f"   {item.content[:200]}{'...' if len(item.content) > 200 else ''}")
        console.print()


def print_response(response: "AgentResponse", debug: bool = False) -> None:
    """Print agent response."""
    # Print debug info if enabled
    if debug and response.recalled_items:
        console.print(
            f"\n[dim]Recalled {len(response.recalled_items)} items, "
            f"{sum(i.token_count for i in response.recalled_items)} tokens[/dim]"
        )
        for item in response.recalled_items[:3]:  # Show first 3
            markers = f"[{', '.join(item.markers)}]" if item.markers else ""
            console.print(f"[dim]  - {markers} {item.content[:50]}...[/dim]")
        if len(response.recalled_items) > 3:
            console.print(f"[dim]  ... and {len(response.recalled_items) - 3} more[/dim]")

    # Print tool calls if any
    if response.tool_calls:
        for tool_name, result in response.tool_calls:
            console.print(Panel(result, title=f"Tool: {tool_name}", border_style="yellow"))

    # Print response
    console.print()
    console.print(Markdown(response.content))
    console.print()


def print_episode_closed(episode_id: str | None) -> None:
    """Print episode closed message."""
    if episode_id:
        console.print(f"[green]Episode closed:[/green] {episode_id}")
        console.print("[dim]Starting new episode...[/dim]")
    else:
        console.print("[yellow]No open episode to close.[/yellow]")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]Error:[/red] {message}")


def print_thinking() -> None:
    """Print thinking indicator."""
    console.print("[dim]Thinking...[/dim]", end="\r")


def get_input() -> str:
    """Get user input."""
    try:
        return console.input("[bold green]You:[/bold green] ")
    except EOFError:
        return "/quit"
