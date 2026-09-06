# Pull Request

## What

<!-- What does this PR change? Link related issues: Fixes #123 -->

## Why

<!-- Why is this change needed? -->

## Checklist

- [ ] Tests pass: `uv run pytest tests/ -v`
- [ ] Types check: `uv run pyright`
- [ ] Lint clean: `uv run ruff check src/ tests/` and `uv run pylint src/ tests/`
- [ ] Formatted with Ruff: `uv run ruff format src/ tests/`
- [ ] New code has tests / bug fix has a regression test
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] No secrets, session files, or personal data included
