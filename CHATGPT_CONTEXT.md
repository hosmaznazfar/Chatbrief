# Chatbrief — persistent project context

Repository: https://github.com/hosmaznazfar/Chatbrief  
Active refactor branch: `refactor/chatbrief-package-layout`  
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
- Astro website: `website/`
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

## Refactor status at the last verified handover

The remote branch contains the `src/chatbrief/` package layout and the application imports are being migrated to `chatbrief.*`. The platform-abstraction work has moved collection, digest construction/service, scheduler, command service, cache access, and MCP wiring toward injected platform interfaces.

Known remaining work from the last project review:
- Complete migration of tests and test imports to the package layout.
- Review/remove legacy test coverage that still assumes the old `src.core` structure; do not delete tests without migrating their behavior coverage.
- Inspect the remaining standalone entry point in `summarizer.py` and its old factory usage.
- Remove the old platform factory only after no production/test references remain.
- Review Telegram-specific constants/prompts/limits for the intended platform-neutral boundaries.
- Update stale README examples and development instructions after the source migration is complete.
- Run the full validation suite only after the developer declares the refactor ready.

Treat these as investigation targets, not assertions that no newer changes exist. Verify current source before acting.

## Graphify — local CLI, pj automation, and Git-shared graph

Graphify is the selected optional code-graph tool. It runs locally as a standalone CLI; no Codex/editor skill, MCP server, or assistant-specific integration is part of this workflow.

- Operational guide: docs/GRAPHIFY.md.
- Full AI workflow adapted from AIWorkFlow: docs/AI_WORKFLOW.md.
- Install the standalone CLI with ./pj graph install.
- Build the initial code-only graph with ./pj graph build.
- Refresh after source changes with ./pj graph update; after pull/merge use ./pj graph sync.
- Query locally with ./pj graph query "question", ./pj graph path "A" "B", and ./pj graph explain "symbol".
- Install/status/uninstall Graphify's local Git automation through ./pj graph hooks install|status|uninstall.
- Commit graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, and graphify-out/graph.html with the source revision they describe. Keep local interpreter metadata, cache, and cost files ignored.
- The default pj graph build/update operations use GRAPHIFY_BACKEND=none for local code-only extraction. Semantic document extraction is optional and requires an explicitly configured backend via --semantic.
- Graphify is not an application dependency and is not part of .pj/workflow.toml. It must not enter pyproject.toml, uv.lock, Docker, or application startup.
- ChatGPT using GitHub reads the committed report/graph artifacts on the selected branch and verifies relationships against source, tests, and ADRs. It cannot run the developer's local CLI or see uncommitted changes.
- Graph generation has not been verified until artifacts exist on GitHub and have been read back. Do not claim local refresh/query unless actual command output is supplied.


## Development workflow contract

Follow `docs/AI_WORKFLOW.md` for the developer's required sequence: inspect the code and graph; request `./pj graph refresh` and `./pj graph diff` at the start of each non-trivial feature/fix/review; review and commit the graph artifacts; research material design options and ask for the developer's decision; implement approved changes in small reviewed commits; update related documentation per step; and finalize migration/planning Markdown files after implementation. Do not skip decision gates or claim local Graphify execution from a GitHub-only session.

## Tooling and commands

Use `uv` and the committed lockfile. Configured tools include Ruff, Pyright, Pylint, Bandit, Vulture, pytest, pytest-cov, pytest-asyncio, and pre-commit. Website dependencies are managed independently with npm and `website/package-lock.json`.

Do not add Graphify to the Python check pipeline: .pj/workflow.toml remains Python-only. Graphify is available through its separate optional pj graph command group.

## Project-local workflow

- `./pj` is a Python standard-library helper; it does not need a compiler or third-party Python package.
- The Python workflow prerequisites are Python 3.14+ and `uv`. Graphify is an optional separately installed CLI.
- `./pj doctor` checks the Python version, `uv` availability, and workflow configuration validity; it returns non-zero when a required prerequisite or configuration is missing/invalid.
- `.pj/workflow.toml` defines Ruff lint, Ruff format check, Pyright, and pytest, all executed through `uv run`.
- The separate Astro website is not part of the Python `pj` workflow.
- Do not add Node/npm, Rust/Cargo, or Graphify to the Python check pipeline. The optional Graphify CLI is managed separately through pj graph commands.

## Safety

No automatic staging, committing, pushing, merging, deployment, publishing, or migrations. Ask before application-code changes when the task is exploratory or feature-oriented. For approved implementation, work in small reviewable phases and keep docs/checklist/handover aligned. Do not run tests before the current refactor is complete unless the developer changes that instruction.
