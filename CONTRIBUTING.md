# Contributing to Telebrief

First off, thank you for considering contributing to Telebrief! Whether it's a bug report, a new feature, a documentation fix, or a question — all contributions are welcome.

## Ways to Contribute

- **Report bugs** — open a [bug report](https://github.com/belaytzev/Telebrief/issues/new?template=bug_report.yml)
- **Suggest features** — open a [feature request](https://github.com/belaytzev/Telebrief/issues/new?template=feature_request.yml)
- **Improve documentation** — typo fixes and clarifications are great first contributions
- **Submit code** — bug fixes, new filters, new AI providers, new storage backends (see [Extensibility](README.md#-extensibility))
- **Add translations** — UI strings live in `src/ui_strings.py`; adding a language is a self-contained change

## Development Setup

Telebrief requires **Python 3.14+** and uses [uv](https://docs.astral.sh/uv/) for environment management.

```bash
# Clone your fork
git clone https://github.com/<your-username>/Telebrief.git
cd Telebrief

# Create a virtual environment and install dependencies
uv venv
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Copy and fill in configuration
cp config.yaml.example config.yaml
cp .env.example .env
```


## Running Tests and Checks

Run the full verification suite before pushing:

```bash
# Tests (coverage threshold must stay above the configured minimum)
uv run pytest tests/ -v

# Type checking
uv run pyright

# Linting
uv run ruff check src/ tests/
uv run pylint src/ tests/

# Formatting
uv run ruff format src/ tests/

# Security checks
uv run bandit -c pyproject.toml -r src/

# Run all pre-commit hooks
pre-commit run --all-files
```

Or use the Makefile shortcuts: `make test`, `make lint`, `make format`, `make check`.

### Testing conventions

* Fixtures live in `tests/conftest.py` (`sample_config`, `mock_logger`)
* All async tests use `@pytest.mark.asyncio`
* New code should come with tests; bug fixes should include a regression test

## Code Style

* **Ruff** for formatting, linting, and import ordering
* **Pyright** for type checking — new code should be fully typed
* **Pylint** for additional static analysis
* **Bandit** for security checks
* **pre-commit** runs repository-wide formatting, linting, and security checks

## Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat(grouper): deterministic QUALITY GATE filter
fix(collector): handle empty channel history
docs: clarify per-channel lookback configuration
```

Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

## Pull Request Process

1. **Fork** the repository and create a branch from `main`
2. **Make your changes** — keep PRs focused on a single concern
3. **Run the full check suite** (tests + Pyright + Ruff + Pylint + Bandit) locally
4. **Run `pre-commit run --all-files`** and make sure all hooks pass
5. **Open a PR** against `main` with a clear description of what and why
6. CI must pass before review; a maintainer will review and merge

For larger changes (new modules, architectural shifts), please open an issue first to discuss the approach — it saves everyone time.

## Reporting Bugs

A good bug report includes:

- Telebrief version / commit hash
- Python version and OS
- AI provider in use (OpenAI / Ollama / Anthropic)
- Relevant `config.yaml` settings (**redact API keys, phone numbers, and session data**)
- Steps to reproduce, expected behavior, actual behavior
- Log output if available (`logs/` directory)

**Never include your Telegram session files, API credentials, or `.env` contents in issues.**

## Questions

Open a [discussion or issue](https://github.com/belaytzev/Telebrief/issues) — happy to help.

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).
