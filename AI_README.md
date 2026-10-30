# Chatbrief — AI development guide

This is the operational guide for AI-assisted work in Chatbrief. Project facts below are based on the repository manifests, source layout, existing documentation, and CI configuration. Re-check GitHub before relying on a prior handover.

## Start every session with repository verification

1. Confirm repository `hosmaznazfar/Chatbrief`, intended branch, and current GitHub HEAD.
2. Read `CHATGPT_CONTEXT.md`, `docs/handover/current.md`, `FEATURE_IMPLEMENTATION_CHECKLIST.md`, the root `README.md`, relevant ADRs/plans, and the source/tests related to the task.
3. Reconcile the handover with current source. GitHub state does not reveal the developer's local uncommitted work; ask for local `git status` when it matters.
4. Inspect the current implementation and existing conventions before proposing changes. Do not infer that a planned feature or architecture is already implemented.
5. Use `docs/CHATGPT_NEW_CHAT_STARTER.md` when starting a new chat.

## Project facts and stack

- Python package: `chatbrief`, located under `src/chatbrief/`.
- Python requirement: `>=3.14`.
- Python environment and dependency management: `uv`; `uv.lock` is committed.
- Backend/application: asynchronous Python Telegram digest application, with AI provider integrations, scheduling, storage, extensibility hooks, and an optional MCP server.
- Website: Astro project under `website/`, with its own `package-lock.json`.
- Packaging: setuptools with src-layout package discovery.
- Development tools declared in `pyproject.toml`: Ruff, Pyright, Pylint, Bandit, Vulture, pytest, pytest-cov, pytest-asyncio, and pre-commit.
- CI: `.github/workflows/ci.yml`; inspect it before changing validation assumptions.

Do not add dependencies or change package managers just to fit the workflow. Graphify is optional and is not required for normal development.

## Chat workflow conventions

These are assistant workflow conventions, not native ChatGPT slash-command registrations.

- `/help`: explain the available workflows and safety rules.
- `/status`: inspect branch, GitHub HEAD, local worktree (only when local output is available), docs, and validation state.
- `/feature <goal>`: inspect source/tests/docs; define scope, acceptance criteria, risks, and phases; update the plan/checklist; wait for approval before implementing application-code changes.
- `/fix <problem>`: trace the behavior to the responsible source and tests, identify root cause, propose a minimal fix and regression coverage, then implement the agreed scope.
- `/trace <area>`: follow real imports, calls, and data flow. If Graphify is installed, use it as an aid, never as the authority.
- `/review`: inspect the complete diff for architecture, correctness, security, data integrity, localization, tests, and accidental generated/secrets files.
- `/test`: run only relevant checks when execution access is available; otherwise provide exact commands and request their output.
- `/branch <name>`: verify the target and preserve work; never discard or switch away from uncommitted changes silently.
- `/merge <source> -> <target>`: compare branches, inspect conflicts and validation, and require explicit final approval.
- `/handover`: update `docs/handover/current.md` with verified GitHub state, completed work, actual validation, blockers, and next steps.
- `/sync`: refresh any configured graph, inspect repository status and diffs, and report what actually succeeded.
- `/create`: use the plan-first process for new features or components.

## Architecture guardrails

- Keep platform-specific behavior inside platform adapters. Digest/domain logic should not depend on Telegram or a future platform SDK.
- Keep composition and dependency wiring in the root `main.py` and platform builder; avoid recreating service construction in domain modules.
- Use the existing `MessageSource` / `MessageSender` abstractions for platform interactions.
- Keep `Message` limited to intrinsic, platform-neutral message data. Platform-specific channel metadata belongs to the adapter/configuration boundary.
- Preserve the current source layout and imports rooted at `chatbrief`; do not reintroduce imports from a top-level `src` package.
- Preserve the existing configuration validation and backwards-compatibility decisions. Do not change credentials or introduce a new platform's config requirements before its adapter is implemented.
- Respect the existing ADRs and plans. If a new decision conflicts with them, explain the trade-off and update/add an ADR rather than silently changing direction.
- Avoid speculative abstractions. Add a protocol/model only when it expresses a real domain contract or removes a concrete coupling.

## Validation commands

Install/synchronize the locked Python environment:

```bash
uv sync --locked
```

Relevant Python checks (run only when the current refactor phase is ready for validation):

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pyright
uv run pylint src tests --fail-under=8.0
uv run bandit -c pyproject.toml -r src
uv run vulture src vulture_whitelist.py --min-confidence 80
uv run pytest tests/ -v
```

The aggregate Makefile targets are also available:

```bash
make lint
make test
make check
```

Website checks, after installing its locked dependencies:

```bash
npm ci --prefix website
npm run build --prefix website
```

Do not claim any command ran unless its output is available. The existing CI workflow is authoritative for CI commands; check it before changing this list.

**Current refactor constraint:** the package-layout and platform-abstraction refactor is still in progress. Do not run the full test suite or declare the refactor complete until the developer explicitly says implementation is ready for validation. The historical baseline of 471 passed / 7 skipped and 80.28% coverage belongs to the pre-refactor state; it is not evidence that this branch currently passes.

## Git and change safety

- Inspect before editing. Preserve user changes and unrelated project conventions.
- Keep changes scoped to the requested task and branch.
- Do not stage, commit, push, merge, deploy, publish, or run migrations unless explicitly approved.
- Do not overwrite existing docs/config wholesale; make focused updates and preserve project-specific content.
- Never put credentials, tokens, private session files, or real local config in tracked files.
- Distinguish verified GitHub state from unknown local worktree state.
- Report validation as passed, failed, skipped, or not run; never blur those categories.

## End-of-session handover

Update `docs/handover/current.md` when meaningful work is completed. Record the exact repository/branch/commit if verified, decisions, files changed, checks actually run, checks deliberately deferred, blockers, and the next concrete action. Do not invent local state or test results.
