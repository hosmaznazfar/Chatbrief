# Chatbrief — AI development guide

This is the operational guide for AI-assisted work in Chatbrief. Project facts below are based on the repository manifests, source layout, existing documentation, and CI configuration. Re-check GitHub before relying on a prior handover.

## Start every session with repository verification

1. Confirm repository `hosmaznazfar/Chatbrief`, intended branch, and current GitHub HEAD.
2. Read `CHATGPT_CONTEXT.md`, `docs/AI_WORKFLOW.md`, `docs/handover/current.md`, `FEATURE_IMPLEMENTATION_CHECKLIST.md`, the root `README.md`, relevant ADRs/plans, and the source/tests related to the task.
3. Read [`docs/GRAPHIFY.md`](docs/GRAPHIFY.md) for the shared code-graph workflow. Check the graph artifacts on the exact branch/commit being inspected.
4. Reconcile the handover with current source. GitHub state does not reveal the developer's local uncommitted work; ask for local `git status` when it matters.
5. Inspect the current implementation and existing conventions before proposing changes. Do not infer that a planned feature or architecture is already implemented.
6. Use `docs/CHATGPT_NEW_CHAT_STARTER.md` when starting a new chat.

## Project facts and stack

- Python package: `chatbrief`, located under `src/chatbrief/`.
- Python requirement: `>=3.14`.
- Python environment and dependency management: `uv`; `uv.lock` is committed.
- Backend/application: asynchronous Python Telegram digest application, with AI provider integrations, scheduling, storage, extensibility hooks, and an optional MCP server.
- Packaging: setuptools with src-layout package discovery.
- Development tools declared in `pyproject.toml`: Ruff, Pyright, Pylint, Bandit, Vulture, pytest, pytest-cov, pytest-asyncio, and pre-commit.
- CI: `.github/workflows/ci.yml`; inspect it before changing validation assumptions.

Do not add dependencies or change package managers just to fit the workflow. Graphify is optional development tooling, not an application/runtime dependency and not a required `pj` check.

## Required feature/fix workflow

For every feature request, bug fix, or codebase investigation, follow [docs/AI_WORKFLOW.md](docs/AI_WORKFLOW.md): inspect the current branch and code relationships; request/review a local graph refresh when useful; then implement already-approved work in small reviewed steps. Research and ask for a decision only when a genuinely unresolved material choice or implementation contradiction appears. Do not repeat approval rounds for decisions already approved. Update related documentation alongside each step. After implementation is complete, finalize the migration and planning Markdown files and update the handover.

For non-trivial changes, request these commands when the graph needs refreshing; do not block implementation on an unchanged or machine-local graph rebuild. The developer reviews any generated changes before staging:

```bash
./pj graph refresh
./pj graph diff
```

Do not treat an uncommitted local graph as visible on GitHub. Verify the new graph commit and source revision before relying on it.

## Graph-assisted development (Graphify)

Chatbrief uses the standalone Graphify CLI locally. Its generated graph artifacts are committed to GitHub so ChatGPT can inspect the same architecture map alongside source code.

- Follow [docs/GRAPHIFY.md](docs/GRAPHIFY.md) for the local CLI, pj automation, Git hooks, privacy, and commit workflow.
- Follow [docs/AI_WORKFLOW.md](docs/AI_WORKFLOW.md) for the complete project AI workflow adapted from AIWorkFlow.
- No Codex integration, editor skill, MCP server, or assistant-specific Graphify installation is required.
- Install the standalone CLI with **./pj graph install**.
- Use **./pj graph refresh** to update/build the graph, generate the report and HTML, and print status; use **./pj graph diff** to inspect Git changes to graph artifacts. The developer reviews and commits portable graph outputs before implementation decisions.
- Lower-level operations remain available as **./pj graph build**, **./pj graph update**, and **./pj graph sync**.
- Query locally with **./pj graph query "question"**, **./pj graph path "A" "B"**, and **./pj graph explain "symbol"**.
- Install Graphify's local Git automation with **./pj graph hooks install**; inspect it with **./pj graph hooks status**.
- Commit **graphify-out/graph.json**, **graphify-out/GRAPH_REPORT.md**, and **graphify-out/graph.html** with the source revision they describe. Keep known machine-local state ignored.
- The default pj graph build/update operations are code-only and set **GRAPHIFY_BACKEND=none**; semantic document extraction is opt-in with **--semantic**.
- For ChatGPT sessions using GitHub, read the committed report and relevant graph JSON on the selected branch. The assistant cannot run the developer's local CLI or inspect uncommitted files.
- Use graph relationships to guide exploration and impact analysis, then verify them against current source, tests, and ADRs. Inferred/ambiguous edges are leads, not facts.
- If the graph is missing or may be stale, state that explicitly and trace the source directly.

## Chat workflow conventions

These are assistant workflow conventions, not native ChatGPT slash-command registrations.

- `/help`: explain the available workflows and safety rules.
- `/status`: inspect branch, GitHub HEAD, local worktree (only when local output is available), graph artifact availability/freshness, and validation state.
- `/feature <goal>`: inspect graph/source/docs/tests; request a graph refresh and review graph changes (commit only if artifacts changed); research material options and ask the developer to decide; then implement approved steps as focused commits, update related docs, and finalize migration/planning files after implementation.
- `/fix <problem>`: trace graph and source to establish root cause; research material fix options and ask the developer to decide; then implement approved changes in reviewed, focused commits.
- `/trace <area>`: use committed Graphify artifacts when available to follow imports/calls/dependencies, then verify every relevant relationship against actual source and tests.
- `/review`: inspect the complete diff for architecture, correctness, security, data integrity, localization, tests, and whether graph artifacts need updating.
- `/test`: run only relevant checks when execution access is available; otherwise provide exact commands and request their output.
- `/branch <name>`: verify the target and preserve work; never discard or switch away from uncommitted changes silently.
- `/merge <source> -> <target>`: compare branches, inspect conflicts and validation, and require explicit final approval.
- `/handover`: update `docs/handover/current.md` with verified GitHub state, completed work, actual validation, graph availability/freshness, blockers, and next steps.
- `/sync`: request `./pj graph refresh` and `./pj graph diff` when local execution is unavailable; inspect the graph commit on GitHub before relying on it.
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

## Current implementation status

The current branch has migrated tests to `chatbrief.*`, moved legacy core behavior tests into `tests/test_digest.py`, removed the obsolete platform factory, and made `PlatformBuilder`/root `main.py` the platform composition path. `TelegramBot` requires an injected `CommandService`; the service receives `MessageSource` and `MessageSender` dependencies. Coverage configuration targets the `chatbrief` package. The default prompt template resolves from the packaged resource while older `src/prompts/base_summary.txt` configuration remains compatible. The completed extensibility and storage plans are archived under `docs/plans/completed/`.

The required application-state SQLite database, migration runner, export persistence, lease-fenced worker foundation, migration-4 shared archive schema, typed archive repositories, and authorization-aware `ExportSnapshotRepository` are implemented. Step 4b-2 developer validation: focused tests **62 passed**; full suite **658 passed, 7 skipped**, coverage **93.52%**; Pyright passed. Ruff and Ruff format each identified one small issue; fixes have been pushed and require a local rerun. Step 4b-3 implements fixed-cutoff snapshots for active subscriptions, private-source grants, central Bot API access, rolling-retention boundaries, deleted-message exclusion, and explicit Bot API coverage gaps. Local validation of the snapshot is pending. Telethon is not accepted as an ongoing-subscription access path. The legacy message-history store remains separate and is never automatically backfilled.

Bale remains unimplemented. The current platform adapter supports Telegram only.

## Validation commands

Install/synchronize the locked Python environment:

```bash
uv sync --locked
```

Relevant Python checks (use focused subsets during implementation and the full set at integration milestones):

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

Do not claim any command ran unless its output is available. The existing CI workflow is authoritative for CI commands; check it before changing this list.

**Current project state (2026-11-02):** the package-layout/platform refactor and dependency upgrades are complete on `refactor/chatbrief-package-layout`. The required application-state SQLite database, migration runner, export schema, and startup integration are implemented and developer-validated; the optional legacy message-history database remains independent and unchanged. Export persistence Steps 3a–3e are implemented and developer-validated. Step 3e validation: focused delivery/storage tests **19 passed**; full suite **631 passed, 7 skipped**, coverage **93.40%**; Ruff lint/format passed; Pyright **0 errors, 0 warnings, 0 informations**. Step 4a adds an un-wired `ExportWorker` service with state-based async phase dispatch, bounded concurrency, lease renewal and stale-handler cancellation, retry scheduling, and bounded shutdown grace. Developer validation on 2026-11-02: Ruff lint passed, Ruff format reported **102 files already formatted**, Pyright reported **0 errors, 0 warnings, 0 informations**, and pytest collected **652 tests** with **7 skipped** and **93.19% coverage**; the pasted terminal output did not include pytest's final passed count. Step 4a is validated. Do not implement a production collection handler by reading the legacy message-history store: its rows have no trustworthy owner/source/message identity and the approved plan prohibits automatic backfill. Migration 4 now establishes the identity-only user table and shared source/access/authorization/subscription/message/coverage schema; local validation is pending. Repository APIs and the authorization-aware snapshot query are the immediate next dependencies. Never read or automatically backfill the legacy message-history store. Packaging, Telegram delivery, cleanup handlers, application startup wiring, and user-facing commands remain future work. Continue in small dependency-ordered implementation/test/documentation slices; do not block coding on Graphify output or reopen approved decisions without a concrete implementation-level contradiction.

## Project workflow helper

The root `./pj` is a Python 3.14+ script implemented with the Python standard library only. It does not require Cargo, Rust, or third-party Python packages. Graphify is an optional external CLI used by the separate pj graph command group.

Runtime/tool requirements:
- Python 3.14+ to execute `pj`.
- `uv` to synchronize the environment and run the configured Python checks.

Read-only commands:

```bash
./pj --help
./pj doctor
./pj workflow validate
./pj check --list
./pj check --dry-run
```

`./pj doctor` verifies that the current interpreter is Python 3.14+, that `uv` is available, and that the workflow configuration exists and validates. `./pj workflow validate` only validates `.pj/workflow.toml`; it does not orchestrate feature/fix stages. `./pj check` runs the configured Python quality checks, while `./pj graph refresh` and `./pj graph diff` support the graph-first development process. It exits non-zero when a required prerequisite or the configuration is missing/invalid. `./pj check` runs the configured checks in order. Run focused tests for each implementation slice and the full suite at appropriate integration milestones; the earlier refactor validation gate has been cleared. The project and quality-check workflow are Python-only. Graphify is not a check prerequisite: its independent pj graph commands are optional local graph operations.

## Git and change safety

- Inspect before editing. Preserve user changes and unrelated project conventions.
- Keep changes scoped to the requested task and branch.
- For an authorized feature/fix task, commit each reviewed implementation step and its related documentation directly to the intended branch. Ask before pushing, merging, deploying, publishing, or running migrations. When the local Graphify CLI is unavailable to the assistant, ask the developer to refresh, review, and commit graph artifacts locally.
- Do not overwrite existing docs/config wholesale; make focused updates and preserve project-specific content.
- Never put credentials, tokens, private session files, or real local config in tracked files.
- Distinguish verified GitHub state from unknown local worktree state.
- Report validation as passed, failed, skipped, or not run; never blur those categories.

## End-of-session handover

Update `docs/handover/current.md` when meaningful work is completed. Record the exact repository/branch/commit if verified, decisions, files changed, checks actually run, checks deliberately deferred, graph artifact availability/freshness, blockers, and the next concrete action. Do not invent local state or test results.


## Graphify artifact completion and hook verification

The current `pj graph build` and `pj graph sync` commands perform code extraction. Graphify may finish that step with only `graphify-out/graph.json` and its internal analysis state, and print a recommendation to run `cluster-only`. That means the graph can exist while `pj graph status` still reports it as incomplete because the human-readable report and visualization have not been generated.

From the repository root, complete the graph artifacts explicitly:

```bash
./pj graph build
graphify cluster-only .
./pj graph status
```

After source changes or a pull/merge, use:

```bash
./pj graph sync
graphify cluster-only .
./pj graph status
```

Confirm that `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.html` exist before treating the shared graph as complete. Review all generated files before staging; the portable graph/report/visualization and manifest are candidates for Git, while internal analysis files, absolute-path markers, caches, and machine-local state must not be committed unless their portability has been verified.

Graphify's post-commit hook can launch a background rebuild. Check its completion and `git status --short` afterward. If tracked graph artifacts changed, inspect the diff, commit the reviewed graph update with the matching source revision, and only then push. Hooks never replace explicit review.

Do not add assistant-specific integrations as part of this project's Graphify workflow. In particular, review any newly generated `.codex/` configuration or agent-instruction files rather than assuming they are required; the intended integration is the local Graphify CLI, `pj`, and Git hooks only.
