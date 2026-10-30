# Chatbrief — current handover

> Snapshot from verified GitHub branch reads/writes and the developer's latest local terminal output. Re-check both remote and local state before continuing.

## Repository state

- Repository: https://github.com/hosmaznazfar/Chatbrief
- Active branch: `refactor/chatbrief-package-layout`
- Latest verified remote commit at this handover update: `0af90bc222a24751864505bf8b6f4cb178ebe8c7` (polishes the hardened Python `pj` diagnostics).
- The developer last reported a clean local worktree after pulling commit `a4bd506`; subsequent `pj` hardening commits were written to GitHub afterward and have not yet been pulled locally.
- Local filesystem state after those remote writes is therefore not currently verified.
- Workflow source: https://github.com/hosmaznazfar/AIWorkFlow (adapted to Chatbrief; do not copy its generic/Rust implementation blindly).

## Objective

Finish the package-layout and platform-abstraction refactor, then validate it. Keep the project-local AI workflow lightweight, Python-specific, and separate from application runtime dependencies.

## Project-local workflow integration

- Added `AI_README.md`, `CHATGPT_CONTEXT.md`, `docs/CHATGPT_NEW_CHAT_STARTER.md`, and `FEATURE_IMPLEMENTATION_CHECKLIST.md`.
- Added `.pj/workflow.toml` with exactly four Python checks, in order: Ruff lint, Ruff format check, Pyright, and pytest. All commands are executed through `uv run`.
- The Astro website is intentionally excluded from `pj`; it is a separate project area with its own npm lockfile and workflow.
- Root `pj` is an executable Python 3.14+ script using only the Python standard library. It does not require Cargo, Rust, Node.js, npm, Graphify, or third-party Python packages.
- Removed the Rust CLI implementation, Rust manifest, and Rust-specific GitHub Actions workflow from the branch. There should be no tracked `pj-core/` or `.github/workflows/pj-core.yml`.
- The CLI supports `init`, `doctor`, `check`, and `workflow validate`; `check --list` and `check --dry-run` are read-only inspection modes.
- Recent hardening added strict TOML type checks, symlink-safe `cwd` validation, boolean/timeout/required/requires validation, cumulative required-failure handling, subprocess startup/timeout reporting, and a `doctor` status/exit code for Python >=3.14, uv, and workflow configuration.
- `AI_README.md` and `CHATGPT_CONTEXT.md` now document the `doctor` contract.

## Verified project facts

- Python package: `chatbrief`, located under `src/chatbrief/`.
- Python requirement: `>=3.14`; use `uv` and the committed `uv.lock`.
- Root `main.py` remains the composition root.
- The application is an asynchronous Telegram digest bot with AI provider integrations, scheduling, storage, extension hooks, and an optional MCP server. Bale remains a future platform target, not an implemented adapter.
- Python development tools include Ruff, Pyright, Pylint, Bandit, Vulture, pytest, pytest-cov, pytest-asyncio, and pre-commit.
- The Astro website is under `website/`; inspect its own package manifest/lockfile before website changes.
- Existing CI is `.github/workflows/ci.yml`; inspect its current contents before changing validation assumptions.
- Architecture decisions and plans live under `docs/adr/` and `docs/plans/`; preserve and update them when material decisions change.

## Architecture decisions to preserve

- Keep digest/domain logic independent of Telegram and future platform SDKs.
- Keep platform-specific behavior in adapters and inject `MessageSource` / `MessageSender`.
- `Message` remains platform-neutral; do not reintroduce channel-level platform metadata into it.
- `Message.link` is the individual message URL; channel URL generation belongs to the platform source abstraction.
- Keep root `main.py` as composition root and the package under `src/chatbrief/`.
- Bale is a future adapter; do not add credentials/config behavior that implies it is implemented.
- Do not remove old factories or tests until all real references and behavior coverage have been migrated.
- Do not make code-graph tooling a runtime dependency or a mandatory part of `pj`; it should be an optional development/AI navigation integration.

## Refactor work represented in the branch

The branch contains the `src/chatbrief/` package layout and imports rooted at `chatbrief.*`. Platform-abstraction work has moved digest collection/building/service, cache access, scheduler, command service, and MCP composition toward injected platform interfaces.

## Remaining refactor work to investigate

1. Finish migrating tests from former `src.*` imports and legacy `src.core` assumptions.
2. Preserve behavior coverage formerly supplied by `tests/test_core.py`; migrate that coverage before deleting/replacing tests.
3. Inspect the standalone `summarizer.py` entry point and remaining old factory usage.
4. Remove obsolete factories/constants only after searching all production and test references.
5. Review Telegram-specific prompts, URL/length assumptions, and constants for correct adapter/domain ownership.
6. Refresh stale README development instructions/examples after source migration is complete.
7. Review and select an optional code-graph tool to replace Graphify as an AI navigation aid. No code-graph product has been selected or integrated yet.

## Validation status

- Before the latest hardening, the developer ran `./pj --help`, `./pj doctor`, `./pj workflow validate`, `./pj check --list`, and `./pj check --dry-run`; those succeeded on the earlier Python CLI implementation.
- The hardened `pj` version has been written and read back from GitHub, but has not yet been pulled or executed locally.
- No Chatbrief tests, Ruff, Pyright, Pylint, Bandit, Vulture, website build, or other project validation checks have been run in this work segment.
- Per the developer's instruction, defer the full Chatbrief test suite until the refactor is complete and the developer explicitly authorizes validation.
- Historical pre-refactor baseline: 471 passed, 7 skipped, 80.28% coverage. This is not a current-branch result.

## Exact next steps

1. Pull the latest `refactor/chatbrief-package-layout` changes with fast-forward only.
2. Run only the read-only CLI verification commands: `./pj --help`, `./pj doctor`, `./pj workflow validate`, `./pj check --list`, and `./pj check --dry-run`. Do not run `./pj check` yet.
3. Select the intended code-graph project and define its local install, MCP integration, generated-data location, ignore rules, and agent instructions. Keep it optional and out of `pj` prerequisites.
4. Continue the approved package/platform refactor without running the full Chatbrief test suite prematurely.
5. Once the developer declares the refactor complete, run the configured Python checks and record their actual output.
