"""Entry point for the test agent."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from examples.test_agent import cli
from examples.test_agent.agent import TestAgent
from examples.test_agent.config import AgentConfig


async def main(config: AgentConfig) -> None:
    """Run the test agent."""
    agent = TestAgent(config)

    try:
        # Initialize agent
        await agent.initialize()

        # Check if this is a new session
        stats = await agent.get_stats()
        is_new = stats.get("turns", 0) == 0

        cli.print_welcome(config.session_id, is_new)

        # Main loop
        debug_mode = config.debug

        while True:
            try:
                user_input = cli.get_input()
            except KeyboardInterrupt:
                cli.console.print("\n[dim]Use /quit to exit[/dim]")
                continue

            if not user_input.strip():
                continue

            # Handle commands
            if user_input.startswith("/"):
                cmd_parts = user_input[1:].split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                cmd_arg = cmd_parts[1] if len(cmd_parts) > 1 else ""

                if cmd == "quit" or cmd == "exit" or cmd == "q":
                    cli.console.print("[dim]Goodbye![/dim]")
                    break

                elif cmd == "help" or cmd == "h":
                    cli.print_help()

                elif cmd == "stats":
                    stats = await agent.get_stats()
                    cli.print_stats(stats)

                elif cmd == "episode":
                    episode_id = await agent.close_episode()
                    cli.print_episode_closed(episode_id)

                elif cmd == "recall":
                    if not cmd_arg:
                        cli.print_error("Usage: /recall <query>")
                    else:
                        items = await agent.recall(cmd_arg)
                        cli.print_recall_results(items, cmd_arg)

                elif cmd == "debug":
                    debug_mode = not debug_mode
                    cli.console.print(
                        f"[dim]Debug mode: {'enabled' if debug_mode else 'disabled'}[/dim]"
                    )

                elif cmd == "clear":
                    cli.print_error("Not implemented. Start a new session with --session <name>")

                else:
                    cli.print_error(f"Unknown command: /{cmd}. Type /help for available commands.")

                continue

            # Process message
            cli.print_thinking()
            try:
                response = await agent.chat(user_input)
                cli.print_response(response, debug=debug_mode)
            except Exception as e:
                cli.print_error(str(e))

    finally:
        await agent.close()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Gleanr Test Agent - A conversational agent for testing Gleanr",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m examples.test_agent.run                    # Use default session
  python -m examples.test_agent.run --session my_test  # Use named session
  python -m examples.test_agent.run --debug            # Enable debug mode

Environment variables:
  OLLAMA_HOST         Ollama API host (default: http://localhost:11434)
  OLLAMA_CHAT_MODEL   Chat model (default: mistral:7b-instruct)
  OLLAMA_EMBED_MODEL  Embedding model (default: nomic-embed-text)
  Gleanr_DEBUG          Enable debug mode (1 = enabled)
""",
    )

    parser.add_argument(
        "--session",
        "-s",
        type=str,
        default="default",
        help="Session name (default: default)",
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enable debug mode (show recalled context)",
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Data directory for session storage",
    )

    parser.add_argument(
        "--token-budget",
        type=int,
        default=2000,
        help="Token budget for recall (default: 2000)",
    )

    return parser.parse_args()


def run() -> None:
    """Entry point."""
    args = parse_args()

    config = AgentConfig(
        session_id=args.session,
        debug=args.debug,
        token_budget=args.token_budget,
    )

    if args.data_dir:
        config.data_dir = args.data_dir

    try:
        asyncio.run(main(config))
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)


if __name__ == "__main__":
    run()
