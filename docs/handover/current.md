# Chatbrief — current handover

> Snapshot from verified GitHub branch reads/writes. Re-check GitHub and the developer's local worktree before continuing.

## Repository state

- Repository: https://github.com/hosmaznazfar/Chatbrief
- Active branch: refactor/chatbrief-package-layout
- Latest verified remote commit from this documentation update: b5f2357e1dbb70408a6d11c4900c4c328d4e0862 (adds Graphify guidance to the implementation checklist).
- The preceding commits in this update added docs/GRAPHIFY.md, integrated Graphify into AI_README.md and CHATGPT_CONTEXT.md, and updated the new-chat starter.
- The developer's local branch/HEAD/worktree after these remote writes is unknown. Do not assume the local checkout contains these commits.
- Workflow source: https://github.com/hosmaznazfar/AIWorkFlow (adapted to Chatbrief; do not copy its generic/Rust implementation blindly).

## Objective

Finish the package-layout and platform-abstraction refactor, then validate it. Keep the project-local AI workflow lightweight, Python-specific, and separate from application runtime dependencies. Use Graphify as an optional, Git-shared architecture map for AI-assisted development.

## Project-local workflow integration

- Existing AI workflow files are adapted from AIWorkFlow: AI_README.md, CHATGPT_CONTEXT.md, docs/CHATGPT_NEW_CHAT_STARTER.md, docs/handover/current.md, and FEATURE_IMPLEMENTATION_CHECKLIST.md.
- Added docs/GRAPHIFY.md as the project-specific operational contract for installation, graph generation/refresh, Git tracking, and assistant use.
- Updated AI_README.md, CHATGPT_CONTEXT.md, docs/CHATGPT_NEW_CHAT_STARTER.md, and FEATURE_IMPLEMENTATION_CHECKLIST.md to tell agents to inspect committed Graphify artifacts and verify graph relationships against source/tests.
- Graphify is selected as optional development/AI navigation tooling. Its graph artifacts are intended to be committed to GitHub so ChatGPT using GitHub can inspect the same architecture map.
- Expected primary artifacts: graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, and graphify-out/graph.html. The current branch had no graphify-out/ artifacts when this integration was inspected; graph generation has not yet been performed or verified.
- The existing .gitignore did not ignore graphify-out/; do not add it. Review generated files and commit the graph with the source revision it describes.
- Local installation is optional: uv tool install graphifyy; Codex skill registration: graphify codex install; Codex invocation: $graphify . and refresh: $graphify . --update.
- Graphify is not an application dependency. Do not add it to pyproject.toml, uv.lock, Docker, or .pj/workflow.toml.
- ChatGPT working through GitHub can read committed graph artifacts, but does not automatically access the developer's local Graphify MCP server or filesystem. If artifacts are absent/stale, report that and trace source directly.
- Graph output is a snapshot. Refresh before committing source changes, review the generated diff, and commit graph and source together. Do not rely solely on a post-commit hook that may leave graph updates uncommitted.
- Do not treat graph edges as infallible: verify relevant relationships against current source, tests, and ADRs, especially inferred or ambiguous edges.

## pj helper

- Added .pj/workflow.toml with exactly four Python checks, in order: Ruff lint, Ruff format check, Pyright, and pytest. All commands are executed through uv run.
- Root pj is an executable Python 3.14+ script using only the Python standard library. It does not require Cargo, Rust, Node.js, npm, Graphify, or third-party Python packages.
- The CLI supports init, doctor, check, and workflow validate; check --list and check --dry-run are read-only inspection modes.
- Recent hardening added strict TOML type checks, symlink-safe cwd validation, boolean/timeout/required/requires validation, cumulative required-failure handling, subprocess startup/timeout reporting, and a doctor status/exit code for Python >=3.14, uv, and workflow configuration.
- Graphify remains separate from pj; the helper stays Python-only.

## Verified project facts

- Python package: chatbrief, located under src/chatbrief/.
- Python requirement: >=3.14; use uv and the committed uv.lock.
- Root main.py remains the composition root.
- The application is an asynchronous Telegram digest bot with AI provider integrations, scheduling, storage, extension hooks, and an optional MCP server. Bale remains a future platform target, not an implemented adapter.
- Python development tools include Ruff, Pyright, Pylint, Bandit, Vulture, pytest, pytest-cov, pytest-asyncio, and pre-commit.
- The Astro website is under website/; inspect its own package manifest/lockfile before website changes.
- Existing CI is .github/workflows/ci.yml; inspect its current contents before changing validation assumptions.
- Architecture decisions and plans live under docs/adr/ and docs/plans/; preserve and update them when material decisions change.

## Architecture decisions to preserve

- Keep digest/domain logic independent of Telegram and future platform SDKs.
- Keep platform-specific behavior in adapters and inject MessageSource / MessageSender.
- Message remains platform-neutral; do not reintroduce channel-level platform metadata into it.
- Message.link is the individual message URL; channel URL generation belongs to the platform source abstraction.
- Keep root main.py as composition root and the package under src/chatbrief/.
- Bale is a future adapter; do not add credentials/config behavior that implies it is implemented.
- Do not remove old factories or tests until all real references and behavior coverage have been migrated.
- Do not make code-graph tooling a runtime dependency or a mandatory part of pj; Graphify is optional development tooling.

## Refactor work represented in the branch

The branch contains the src/chatbrief/ package layout and imports rooted at chatbrief.*. Platform-abstraction work has moved digest collection/building/service, cache access, scheduler, command service, and MCP composition toward injected platform interfaces.

## Remaining refactor work to investigate

1. Finish migrating tests from former src.* imports and legacy src.core assumptions.
2. Preserve behavior coverage formerly supplied by tests/test_core.py; migrate that coverage before deleting/replacing tests.
3. Inspect the standalone summarizer.py entry point and remaining old factory usage.
4. Remove obsolete factories/constants only after searching all production and test references.
5. Review Telegram-specific prompts, URL/length assumptions, and constants for correct adapter/domain ownership.
6. Refresh stale README development instructions/examples after source migration is complete.
7. Install/register Graphify locally if needed, generate the initial graph from the current Chatbrief source, inspect the outputs, and commit the reviewed graphify-out/ artifacts with the matching source revision.
8. Pull and verify the latest documentation updates in the developer's local checkout; local state is unknown.

## Validation status

- The Graphify integration documentation was written and read-back verification is still pending.
- No Graphify CLI installation, skill registration, graph generation, or graph query was performed in this work segment.
- No Chatbrief tests, Ruff, Pyright, Pylint, Bandit, Vulture, website build, or other project validation checks have been run in this work segment.
- Per the developer's instruction, defer the full Chatbrief test suite until the refactor is complete and the developer explicitly authorizes validation.
- Historical pre-refactor baseline: 471 passed, 7 skipped, 80.28% coverage. This is not a current-branch result.

## Exact next steps

1. Pull the latest refactor/chatbrief-package-layout commits with fast-forward only; inspect local status first and preserve any local work.
2. Install Graphify locally if not already available: uv tool install graphifyy; register Codex with graphify codex install if needed.
3. From a Codex session in the Chatbrief root, run $graphify . to create the initial graph; inspect all generated outputs.
4. Verify graphify-out/graph.json, GRAPH_REPORT.md, and graph.html are present, relevant, and safe to commit; then commit them with the source revision they describe after explicit review.
5. Continue the approved package/platform refactor without running the full Chatbrief test suite prematurely.
6. Once the developer declares the refactor complete, run the configured Python checks and record their actual output.
