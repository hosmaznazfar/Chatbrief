# Chatbrief — current handover

> Snapshot created from inspection of the GitHub branch. Re-verify all facts before continuing. Local worktree state is not visible through the GitHub connection.

## Repository state

- Repository: https://github.com/hosmaznazfar/Chatbrief
- Intended branch: `refactor/chatbrief-package-layout`
- Latest inspected branch: package layout is rooted at `src/chatbrief/`; root `main.py` remains the application entry point/composition root.
- Local branch, HEAD, and uncommitted changes: unknown; the developer must provide local `git status` when relevant.
- Related workflow source: https://github.com/hosmaznazfar/AIWorkFlow

## Objective

Finish the package-layout and platform-abstraction refactor, then validate it. Integrate a project-local AI-assisted workflow without replacing Chatbrief's architecture, dependency management, existing docs, or CI.

## Verified repository/tooling observations

- Python package metadata declares `chatbrief`, Python `>=3.14`, setuptools src-layout discovery from `src`, and package data under `chatbrief/prompts/*.txt`.
- `uv.lock` is committed; use `uv sync --locked` for reproducible environment setup.
- Python tooling is declared in `pyproject.toml`: Ruff, Pyright, Pylint, Bandit, Vulture, pytest, pytest-cov, pytest-asyncio, and pre-commit.
- The root Makefile provides `lint`, `test`, `check`, `format`, and run/install targets.
- The Astro website is under `website/` and has a committed `package-lock.json`; CI runs `npm ci` and `npm run build`.
- Existing architecture docs are in `docs/adr/` and `docs/plans/`; preserve them.
- Existing CI workflow is `.github/workflows/ci.yml`. Its push/PR branch filters currently target `main`; do not assume it runs on this feature branch without a PR to main.

## Project decisions to preserve

- Keep digest/domain logic independent of Telegram and future platform SDKs.
- Keep platform behavior in adapters and use injected `MessageSource` / `MessageSender`.
- `Message` remains platform-neutral; do not reintroduce channel-level platform metadata into it.
- `Message.link` is the individual message URL; channel URL generation belongs to the platform source abstraction.
- Keep root `main.py` as composition root and the Python package under `src/chatbrief/`.
- Bale is a future adapter; do not add credentials/config behavior that implies it is implemented.
- Do not remove old factories or tests until all real references/coverage have been migrated.

## Refactor work already represented in the branch

The current branch includes the `src/chatbrief/` package tree and imports rooted at `chatbrief.*`. The refactor has introduced platform abstractions/building and moved digest collection, building/service, cache, scheduler, command service, and MCP composition toward dependency injection.

## Remaining refactor work to investigate

1. Inspect the full current diff and local worktree state before further edits.
2. Finish migrating tests from the former `src.*` imports and legacy `src.core` assumptions.
3. Preserve the behavior coverage formerly supplied by `tests/test_core.py`; split/migrate tests before deleting legacy tests.
4. Inspect the standalone `summarizer.py` entry point and remaining old factory usage.
5. Remove obsolete factory/constants only after searching all production and test references.
6. Review Telegram-specific prompts, URL/length assumptions, and constants for correct adapter/domain ownership.
7. Refresh README development instructions and examples to match the final package paths and actual commands.

## Validation status

- No tests, lint, type checks, or builds were run as part of this handover.
- Historical pre-refactor baseline: 471 passed, 7 skipped, 80.28% coverage. This is not a current-branch result.
- Per the developer's instruction, defer the full test suite until the refactor is complete and the developer explicitly authorizes validation.
- Rust `pj` CLI integration must be treated as unverified until its GitHub Actions workflow succeeds.

## Exact next steps

1. Reconcile this handover with the current GitHub branch and developer's local `git status`.
2. Continue the approved package/platform refactor without running the full test suite prematurely.
3. Once the developer declares the refactor complete, run the configured Python checks and record their real output.
4. Check the `pj-core` GitHub Actions run before relying on the Rust CLI.
