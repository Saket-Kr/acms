"""Configuration for the test agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


@dataclass
class OllamaConfig:
    """Ollama API configuration."""

    host: str = field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    chat_model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_CHAT_MODEL", "mistral:7b-instruct")
    )
    embed_model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    )
    embed_dimension: int = 384  # nomic-embed-text dimension


@dataclass
class AgentConfig:
    """Test agent configuration."""

    # Session settings
    session_id: str = "default"
    data_dir: Path = field(default_factory=lambda: Path.home() / ".acms_test_agent")

    # ACMS settings
    token_budget: int = 2000
    max_turns_per_episode: int = 8

    # Debug settings
    debug: bool = field(default_factory=lambda: os.getenv("ACMS_DEBUG", "0") == "1")

    # Ollama settings
    ollama: OllamaConfig = field(default_factory=OllamaConfig)

    def __post_init__(self) -> None:
        """Ensure data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> Path:
        """Get SQLite database path for this session."""
        return self.data_dir / f"{self.session_id}.db"


# Agent system prompt
SYSTEM_PROMPT = """You are a helpful AI assistant. You have access to tools and memory of our conversation.

When you make decisions, start your response with "Decision:" to help remember them.
When you encounter constraints or limitations, note them with "Constraint:".
When something fails or doesn't work, note it with "Failed:" to avoid repeating mistakes.
When the user sets a goal, acknowledge it with "Goal:".

Be concise and helpful. If you're unsure, ask clarifying questions."""

# Default configuration
DEFAULT_CONFIG = AgentConfig()
