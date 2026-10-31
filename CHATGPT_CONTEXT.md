# Chatbrief — persistent project context

Repository: https://github.com/hosmaznazfar/Chatbrief  
Active modernization branch: `upgrade/full-project-modernization`  
Primary package: `src/chatbrief/`  
Python: `>=3.14`; package/dependency manager: `uv`

## Read first

At the start of a new session, verify the repository and branch, then read:

1. `AI_README.md`
2. `docs/handover/current.md`
3. `FEATURE_IMPLEMENTATION_CHECKLIST.md`
4. `README.md`
5. `docs/AI_WORKFLOW.md`
6. `docs/GRAPHIFY.md`
7. Relevant ADRs in `docs/adr/`, plans in `docs/plans/`, and the current source/tests.

The handover is a snapshot, not proof of current state. GitHub does not expose the developer's local uncommitted work.

## Product and stack

Chatbrief is an asynchronous, AI-powered digest application. The current implementation collects Telegram messages, summarizes/groups them using configurable AI providers, and delivers digests. It also has scheduling, storage, extension hooks, and an optional MCP server. Bale is a future platform target, not an implemented adapter.

The repository includes:
- Python application/package under `src/chatbrief/`
- Root entry point/composition root: `main.py`
- Python dependencies and tool configuration: `pyproject.toml`, `uv.lock`
- Tests: `tests/`
- CI: `.github/workflows/ci.yml`
- Architecture decisions and plans: `docs/adr/`, `docs/plans/`

## Architectural decisions to preserve

- Domain/digest logic must not import or know Telegram/Bale SDK details.
- Platform adapters own authentication, fetching, sending, URL construction, and platform-specific behavior.
- `Message` contains intrinsic generic message data only; do not add platform-specific channel metadata to it.
- `Message.link` is the individual message link. Channel/source attribution is handled at the grouped digest/platform boundary.
- `MessageSource.get_channel_url(ChannelConfig)` owns channel URL generation; formatters must not parse Telegram URL syntax.
- Services receive `MessageSource` / `MessageSender` dependencies rather than constructing platform clients.
- `PlatformBuilder` and root `main.py` compose concrete platform services.
- `src/core.py` was removed after its responsibilities were migrated to focused modules.
- Keep the standard `src/chatbrief` package layout. Root `main.py` remains the executable composition root.
- Do not implement Bale configuration/credentials as if the adapter already exists.
- Keep existing ADRs authoritative; record material architecture changes explicitly.

## Current refactor status (2026-10-30)

The package/platform implementation migration is the starting point for the Python-only modernization on `upgrade/full-project-modernization`. The full test suite and quality checks have deliberately not been run.

Completed:
- Migrated test imports to `chatbrief.*` and moved legacy `tests/test_core.py` behavior coverage into `tests/test_digest.py`.
- Added platform-builder tests and updated the shared test configuration to include `Platform.TELEGRAM`.
- Removed the obsolete platform factory; the standalone summarizer now obtains platform services through `PlatformBuilder`.
- Made `TelegramBot` require an injected `CommandService`; root `main.py` remains the application composition root.
- Updated `CommandService` to use injected `MessageSource` and `MessageSender` dependencies.
- Fixed the remaining type-checking-only legacy package import.
- Aligned coverage targets with the `chatbrief` package.
- Updated current README/config/Docker instructions, moved the default prompt template to the package path while preserving the legacy config sentinel, and archived the completed extensibility/storage plans.

Remaining:
- Review the committed changes in the developer's local checkout without overwriting local work.
- Wait for explicit authorization to run Ruff, Pyright, Pylint, Bandit, Vulture, and the full pytest suite.
- Fix any validation findings and record actual results before declaring the refactor complete.

Do not treat the historical pre-refactor test baseline as evidence that the current branch passes.

## Graphify — local CLI, pj automation, and Git-shared graph

Graphify is the selected optional code-graph tool. It runs locally as a standalone CLI; no Codex/editor skill, MCP server, or assistant-specific integration is part of this workflow.

- Operational guide: `docs/GRAPHIFY.md`.
- Full AI workflow: `docs/AI_WORKFLOW.md`.
- Use `./pj graph refresh` and `./pj graph diff` when a new non-trivial task needs a fresh graph; the developer has already handled the graph step for the current refactor and no additional refresh is being requested here.
- The latest verified GitHub tree contains `graphify-out/graph.json` and `graphify-out/manifest.json`; `GRAPH_REPORT.md` and `graph.html` are absent from that remote snapshot. The developer's local state may differ.
- `.graphify_analysis.json` and `.graphify_root` are currently tracked. Review their portability separately; they are not blockers for the package/platform implementation.
- Graphify is not an application dependency and is not part of `.pj/workflow.toml`. It must not enter `pyproject.toml`, `uv.lock`, Docker, or application startup.
- ChatGPT using GitHub reads committed artifacts on the selected branch and verifies relationships against source, tests, and ADRs. It cannot run the developer's local CLI or see uncommitted changes.
- Treat graph relationships as navigation aids; verify important relationships against current source and tests.

## Development workflow contract

Follow `docs/AI_WORKFLOW.md` for the developer's required sequence: inspect the code and graph; request `./pj graph refresh` and `./pj graph diff` at the start of each non-trivial feature/fix/review; review and commit the graph artifacts; research material design options and ask for the developer's decision; implement approved changes in small reviewed commits; update related documentation per step; and finalize migration/planning Markdown files after implementation. Do not skip decision gates or claim local Graphify execution from a GitHub-only session.

## Tooling and commands

Use `uv` and the committed lockfile. Configured tools include Ruff, Pyright, Pylint, Bandit, Vulture, pytest, pytest-cov, pytest-asyncio, and pre-commit. The project is Python-only; Python dependencies and tooling are managed with `uv`.

Do not add Graphify to the Python check pipeline: .pj/workflow.toml remains Python-only. Graphify is available through its separate optional pj graph command group.

## Project-local workflow

- `./pj` is a Python standard-library helper; it does not need a compiler or third-party Python package.
- The Python workflow prerequisites are Python 3.14+ and `uv`. Graphify is an optional separately installed CLI.
- `./pj doctor` checks the Python version, `uv` availability, and workflow configuration validity; it returns non-zero when a required prerequisite or configuration is missing/invalid.
- `.pj/workflow.toml` defines Ruff lint, Ruff format check, Pyright, and pytest, all executed through `uv run`.
- Do not add Rust/Cargo or Graphify to the Python check pipeline. The optional Graphify CLI is managed separately through pj graph commands.

## Safety

No automatic staging, committing, pushing, merging, deployment, publishing, or migrations. Ask before application-code changes when the task is exploratory or feature-oriented. For approved implementation, work in small reviewable phases and keep docs/checklist/handover aligned. Do not run tests before the current refactor is complete unless the developer changes that instruction.
