# Chatbrief — current handover

> Snapshot from GitHub branch inspection and verified writes. Re-check the branch before continuing. Local worktree state is not visible through the GitHub connection.

## Repository state

- Repository: https://github.com/hosmaznazfar/Chatbrief
- Intended branch: `refactor/chatbrief-package-layout`
- Latest verified branch commit before this handover update: `9b52feaab1fc4766021f660b59ab50018970c22b` (marks the root `pj` launcher executable).
- Local branch, HEAD, and uncommitted changes: unknown; the developer must provide local `git status` when relevant.
- Workflow source: https://github.com/hosmaznazfar/AIWorkFlow

## Objective

Finish the package-layout and platform-abstraction refactor, then validate it. Integrate a project-local AI-assisted workflow without replacing Chatbrief's architecture, dependency management, existing docs, or CI.

## AIWorkFlow integration completed on this branch

- Added `AI_README.md` with Chatbrief-specific startup, architecture, safety, and validation instructions.
- Added `CHATGPT_CONTEXT.md` with persistent product, stack, architecture, and refactor context.
- Added `docs/CHATGPT_NEW_CHAT_STARTER.md`.
- Added `FEATURE_IMPLEMENTATION_CHECKLIST.md`.
- Added `docs/handover/current.md` and updated it with this integration state.
- Added `.pj/workflow.toml` with ordered Ruff, formatting, Pyright, pytest, and optional Astro website build steps. The Python test step is explicitly deferred until the developer declares the refactor ready.
- Added the AIWorkFlow Rust CLI source under `pj-core/` and root `pj` launcher. The launcher is stored with executable mode `100755`.
- Added `.github/workflows/pj-core.yml` for launcher/bootstrap checks, rustfmt, Rust unit tests, and Clippy.
- Added a workflow documentation section to the existing README.
- Preserved existing architecture docs, plans, manifests, lockfiles, Makefile, application source, and CI workflow.

## Verified repository/tooling observations

- Python package metadata declares `chatbrief`, Python `>=3.14`, setuptools src-layout discovery from `src`, and package data under `chatbrief/prompts/*.txt`.
- `uv.lock` is committed; use `uv sync --locked` for reproducible environment setup.
- Python tooling is declared in `pyproject.toml`: Ruff, Pyright, Pylint, Bandit, Vulture, pytest, pytest-cov, pytest-asyncio, and pre-commit.
- The root Makefile provides `lint`, `test`, `check`, `format`, and run/install targets.
- The Astro website is under `website/` and has a committed `package-lock.json`; CI runs `npm ci` and `npm run build`.
- Existing architecture docs are in `docs/adr/` and `docs/plans/`; preserve them.
- Existing CI workflow is `.github/workflows/ci.yml`; its push/PR branch filters currently target `main`.
- The `pj` CLI is built from source with Cargo if no release binary is present. No prebuilt release binary is bundled.

## Project decisions to preserve

- Keep digest/domain logic independent of Telegram and future platform SDKs.
- Keep platform behavior in adapters and use injected `MessageSource` / `MessageSender`.
- `Message` remains platform-neutral; do not reintroduce channel-level platform metadata into it.
- `Message.link` is the individual message URL; channel URL generation belongs to the platform source abstraction.
- Keep root `main.py` as composition root and the Python package under `src/chatbrief/`.
- Bale is a future adapter; do not add credentials/config behavior that implies it is implemented.
- Do not remove old factories or tests until all real references/coverage have been migrated.

## Refactor work represented in the branch

The current branch includes the `src/chatbrief/` package layout and imports rooted at `chatbrief.*`. The platform-abstraction work has introduced platform interfaces/building and moved digest collection, building/service, cache, scheduler, command service, and MCP composition toward dependency injection.

## Remaining refactor work to investigate

1. Reconcile this handover with the current GitHub branch and developer's local `git status`.
2. Finish migrating tests from the former `src.*` imports and legacy `src.core` assumptions.
3. Preserve the behavior coverage formerly supplied by `tests/test_core.py`; migrate its behavior coverage before deleting or replacing it.
4. Inspect the standalone `summarizer.py` entry point and remaining old factory usage.
5. Remove obsolete factory/constants only after searching all production and test references.
6. Review Telegram-specific prompts, URL/length assumptions, and constants for correct adapter/domain ownership.
7. Refresh README development instructions and examples to match the final package paths and actual commands.
8. Verify the Rust CLI through the new GitHub Actions workflow before relying on it locally.

## Validation status

- GitHub read-back confirmed all newly added workflow files and README updates are present on the target branch.
- The Git tree confirms the root `pj` launcher has executable mode `100755`.
- No local Chatbrief tests, lint, type checks, website build, Rust build, or Rust tests were run in this session.
- A workflow-run result for the new Rust CI was not available through the connected GitHub read endpoint at handover time; do not mark the Rust CLI as CI-verified.
- Historical pre-refactor baseline: 471 passed, 7 skipped, 80.28% coverage. This is not a current-branch result.
- Per the developer's instruction, defer the full Chatbrief test suite until the refactor is complete and the developer explicitly authorizes validation.

## Exact next steps

1. Reconcile the handover with local `git status` and pull the updated feature branch.
2. Continue the approved package/platform refactor without running the full Chatbrief test suite prematurely.
3. Check the `pj-core` GitHub Actions run; resolve any compile, formatting, test, or Clippy failures before relying on the CLI.
4. Once the developer declares the refactor complete, run the configured Python checks and record their actual output.
