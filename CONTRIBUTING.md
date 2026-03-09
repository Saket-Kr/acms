# Contributing to Gleanr

Thank you for your interest in contributing to Gleanr! This guide will help you
get started.

## Development Setup

```bash
git clone https://github.com/Saket-Kr/gleanr.git
cd gleanr
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=gleanr

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/
```

## Code Quality

This project enforces strict code quality standards:

```bash
# Linting
ruff check gleanr/

# Formatting
ruff format gleanr/

# Type checking
mypy gleanr/
```

All checks must pass before a PR will be reviewed.

## Project Structure

```
gleanr/
  core/       # Gleanr entry point and configuration
  memory/     # Recall pipeline, reflection, episode management
  models/     # Data models (Turn, Episode, Fact, etc.)
  providers/  # Embedder, Reflector, TokenCounter implementations
  storage/    # Storage backends (in-memory, SQLite)
  cache/      # LRU caching layer
  utils/      # Shared utilities
  errors.py   # Exception hierarchy
tests/
  unit/         # Fast, isolated tests
  integration/  # Tests that exercise multiple components together
```

## Making Changes

1. **Read `PLAN.md`** to understand the architecture before making changes.
2. **Create a branch** from `main` for your work.
3. **Write tests** for new functionality or bug fixes.
4. **Keep changes focused** — one logical change per PR.
5. **Follow existing patterns** — match the style of surrounding code.

## Commit Messages

Use clear, concise commit messages that explain *why*, not just *what*:

- `Fix consolidation applying actions against scoped subset instead of all facts`
- `Add exponential backoff retry to OpenAI and Anthropic providers`

## Pull Requests

- Keep the title short (under 70 characters).
- Include a summary of what changed and why.
- Reference any related issues.
- Ensure all tests pass and code quality checks are clean.

## Reporting Issues

Use the [issue tracker](https://github.com/Saket-Kr/gleanr/issues) and include:

- What you expected to happen
- What actually happened
- Steps to reproduce
- Python version and OS

## License

By contributing, you agree that your contributions will be licensed under the
MIT License.
