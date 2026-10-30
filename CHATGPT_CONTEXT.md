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
5. `docs/GRAPHIFY.md`
6. Relevant ADRs in `docs/adr/`, plans in `docs/plans/`, and the current source/tests.

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

## Graphify — shared code knowledge graph

Graphify is the selected optional code-graph tool for Chatbrief's GitHub-based AI workflow. The purpose is to commit the generated graph alongside source so ChatGPT and other agents inspecting GitHub can read the same architectural map.

- Operational instructions: `docs/GRAPHIFY.md`.
- Commit the primary outputs `graphify-out/graph.json`, `graphify-out/GRAPH_REPORT.md`, and `graphify-out/graph.html` with the source revision they describe.
- Do not ignore `graphify-out/`; the generated graph is intentionally shared through Git.
- Local optional install: `uv tool install graphifyy`; Codex skill registration: `graphify codex install`.
- In Codex, first build with `$graphify .`, then refresh changed files with `$graphify . --update`.
- Graphify is not an application dependency, must not enter `pyproject.toml`/ `uv.lock`, Docker, or `.pj/workflow.toml`, and is not required for normal development.
- For ChatGPT using GitHub, read the committed report and relevant graph JSON from the selected branch. ChatGPT does not automatically have access to a developer's local Graphify process or MCP server.
- Treat graph relationships as navigation/impact-analysis evidence. Verify important paths against current source, tests, and ADRs; inferred/ambiguous edges are not facts.
- If artifacts are absent or stale, state that clearly and trace source directly. Do not claim graph refresh/query unless it actually occurred.

Graph generation is not yet verified on this branch. Do not claim that `graphify-out/` exists or is current until the artifacts are present on GitHub and read back.

## Tooling and commands

Use `uv` and the committed lockfile. Configured tools include Ruff, Pyright, Pylint, Bandit, Vulture, pytest, pytest-cov, pytest-asyncio, and pre-commit. Website dependencies are managed independently with npm and `website/package-lock.json`.

Do not add Graphify to `pj`: the project-local check workflow remains Python-only and Graphify is an optional AI navigation integration.

## Project-local workflow

- `./pj` is a Python standard-library helper; it does not need a compiler or third-party Python package.
- The only workflow runtime/tool prerequisites are Python 3.14+ and `uv`.
- `./pj doctor` checks the Python version, `uv` availability, and workflow configuration validity; it returns non-zero when a required prerequisite or configuration is missing/invalid.
- `.pj/workflow.toml` defines Ruff lint, Ruff format check, Pyright, and pytest, all executed through `uv run`.
- The separate Astro website is not part of the Python `pj` workflow.
- Do not add Node/npm, Rust/Cargo, Graphify, or other language toolchains to `pj` unless the developer explicitly changes the project requirements.

## Safety

No automatic staging, committing, pushing, merging, deployment, publishing, or migrations. Ask before application-code changes when the task is exploratory or feature-oriented. For approved implementation, work in small reviewable phases and keep docs/checklist/handover aligned. Do not run tests before the current refactor is complete unless the developer changes that instruction.
