# Chatbrief — current handover

> Snapshot from verified GitHub branch reads/writes. Re-check GitHub and the developer's local worktree before continuing.

## Repository state

- Repository: https://github.com/hosmaznazfar/Chatbrief
- Active branch: refactor/chatbrief-package-layout
- Latest verified remote commit before this handover update: 88de580c90af48ce31fd3a482669979863f95b35 (removed obsolete Graphify/Codex instructions from the handover).
- This integration was made directly on the remote branch through GitHub. The developer's local branch/HEAD/worktree remains unknown; inspect local status before pulling.
- Workflow source: https://github.com/hosmaznazfar/AIWorkFlow (the project workflow was adapted to Chatbrief's Python/Astro stack; the Rust implementation was not copied).

## Objective

Finish the package-layout and platform-abstraction refactor, then validate it. Keep the project-local AI workflow lightweight, Python-specific, and separate from application runtime dependencies. Use Graphify as an optional, Git-shared architecture map for AI-assisted development.

## Project-local workflow integration

- Created docs/AI_WORKFLOW.md, adapting AIWorkFlow's workflow lifecycle, graph-assisted exploration, project command contract, safety rules, chat conventions, and handover contract to Chatbrief.
- Rewrote docs/GRAPHIFY.md around the standalone local Graphify CLI and pj automation. No Codex/editor skill, MCP server, or assistant-specific Graphify installation is required.
- Added the separate pj graph command group: install, status, build, update, sync, query, path, explain, watch, and hooks install/status/uninstall.
- Default pj graph build/update/sync operations set GRAPHIFY_BACKEND=none and use code-only extraction. Semantic document extraction is opt-in through --semantic.
- Added known local-only Graphify output exclusions to .gitignore: graphify-out/cost.json, graphify-out/.graphify_python, graphify-out/.cloud-cta-shown, and graphify-out/cache/.
- Updated AI_README.md, CHATGPT_CONTEXT.md, docs/CHATGPT_NEW_CHAT_STARTER.md, FEATURE_IMPLEMENTATION_CHECKLIST.md, and README.md to use the local CLI/pj workflow and to tell ChatGPT to inspect committed graph artifacts through GitHub.
- The primary shareable graph artifacts are graphify-out/graph.json, graphify-out/GRAPH_REPORT.md, graphify-out/graph.html, plus portable manifest.json if Graphify generates it.
- Graphify's local hook integration is exposed through pj graph hooks. It installs post-commit, post-checkout, post-merge, and post-rewrite hooks plus a graph.json merge driver. After git pull/merge, run pj graph sync. Review .gitattributes changes created by hook installation.
- Graphify artifacts are intended to be committed with the source revision they describe. Never stage/commit/push automatically.
- No graphify-out/ artifacts have been generated or verified on this branch yet. No local Graphify CLI was installed or executed in this work segment.
- ChatGPT using GitHub can inspect committed artifacts but cannot run the developer's local Graphify CLI or inspect uncommitted local changes. If the graph is absent/stale, report that and trace source directly.
- Graph relationships are navigation/impact-analysis evidence. Verify important paths against current source, tests, and ADRs; inferred/ambiguous edges are leads, not facts.

## pj helper

- .pj/workflow.toml still contains exactly four Python checks, in order: Ruff lint, Ruff format check, Pyright, and pytest. All commands execute through uv run.
- Root pj remains an executable Python 3.14+ script using only the Python standard library.
- Added a separate optional Graphify command group without adding Graphify to the Python check pipeline or application dependencies.
- pj graph install uses uv tool install graphifyy and is idempotent when graphify is already on PATH.
- pj graph build uses graphify extract . --code-only by default.
- pj graph update runs graphify update . with GRAPHIFY_BACKEND=none by default.
- pj graph sync builds when graphify-out/graph.json is missing and otherwise incrementally updates.
- pj graph query/path/explain delegate to the corresponding Graphify CLI query commands.
- pj graph hooks install/status/uninstall delegate to Graphify's Git hook management. pj graph watch delegates to the optional Graphify watch feature.
- pj graph status reports CLI availability, primary artifact presence, graphify-out Git changes, and Graphify hook status.
- pj doctor reports Graphify as optional and does not fail if it is not installed.
- Graphify is not a .pj/workflow.toml check, pyproject.toml dependency, uv.lock dependency, Docker dependency, or runtime dependency.
- The Python check pipeline remains unchanged; tests are still deferred until the developer declares the refactor ready.

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

- Read-back verification succeeded for pj, docs/GRAPHIFY.md, docs/AI_WORKFLOW.md, AI_README.md, CHATGPT_CONTEXT.md, docs/CHATGPT_NEW_CHAT_STARTER.md, FEATURE_IMPLEMENTATION_CHECKLIST.md, README.md, docs/handover/current.md, .gitignore, and .pj/workflow.toml.
- No local Graphify installation, graph generation, query, or Git hook installation was performed.
- No Chatbrief tests, Ruff, Pyright, Pylint, Bandit, Vulture, or website build were run. Do not infer runtime correctness from GitHub file writes.
- Per the developer's instruction, defer the full Chatbrief test suite until the refactor is complete and the developer explicitly authorizes validation.
- Historical pre-refactor baseline: 471 passed, 7 skipped, 80.28% coverage. This is not a current-branch result.

## Exact next steps

1. Inspect local git status, then pull refactor/chatbrief-package-layout with --ff-only; preserve any local work.
2. Inspect pj --help and ./pj graph --help; run ./pj doctor and ./pj graph status.
3. Install the standalone Graphify CLI with ./pj graph install if it is not already available.
4. Run ./pj graph build to generate the initial local code-only graph. Inspect the report, JSON, HTML, and any additional generated files.
5. Run ./pj graph hooks install if automatic post-commit/branch-switch refresh is desired. Review local Git hook status, Git config, and any .gitattributes change.
6. Review graphify-out artifacts and commit the portable graph files with the source revision they describe. Keep local-only output excluded.
7. After every git pull/merge, run ./pj graph sync; before source commits, run ./pj graph sync and review graph changes.
8. Continue the approved package/platform refactor without running the full Chatbrief test suite prematurely.
9. Once the developer declares the refactor complete, run the configured Python checks and record their actual output.


## Local Graphify bootstrap — developer-reported state (2026-10-30)

The developer supplied terminal output confirming the following local operations on `refactor/chatbrief-package-layout`:

- Installed Graphify CLI is available at `/home/hmnf/.local/bin/graphify`; reported version: `0.9.95`.
- `./pj doctor` succeeded and reported Python 3.14.8, uv available, and a valid workflow config with four checks. Graphify is correctly treated as optional.
- `./pj graph hooks install` installed the post-commit, post-checkout, post-merge, and post-rewrite hooks and registered the `graphify` merge driver. A second install/status confirmed these were already installed.
- `./pj graph sync` created the code-only graph. The subsequent `./pj graph build` incrementally scanned 85 unchanged code files and wrote a graph with 1,911 nodes and 4,260 edges.
- `./pj graph status` reports `graph.json` present, but `GRAPH_REPORT.md` and `graph.html` missing; the graph is therefore incomplete. Graphify's output explicitly recommends `graphify cluster-only <project-root>`. Run `graphify cluster-only .` from the repository root, then verify `./pj graph status` again.
- The post-commit hook launched a background rebuild with log at `/home/hmnf/.cache/graphify-rebuild.log`. Its completion/result has not been supplied; inspect the log and Git status before the next push.
- The developer committed and pushed commit `7047c4a` (`apply latest changes`) to this branch. This is developer-reported terminal evidence; re-check GitHub HEAD before relying on it.
- The `git add .` commit also included `.codex/hooks.json`, `AGENTS.md`, `graphify-out/.graphify_analysis.json`, and `graphify-out/.graphify_root`. These were not part of the intended shareable artifact list. The inspected `.codex/hooks.json` invokes Graphify from a Codex Bash hook; `AGENTS.md` contains assistant/skill-specific instructions; `.graphify_root` contains an absolute local path. Review whether these should be removed from the shared branch and add appropriate ignore rules for machine-local/internal Graphify files. Do not silently add further assistant-specific integrations; the intended design remains local Graphify CLI + pj + Git hooks.
- No Chatbrief tests or quality checks were run in the supplied output. Continue deferring the full test suite until the developer declares the package/platform refactor ready for validation.

### Immediate Graphify follow-up

~~~bash
graphify cluster-only .
./pj graph status
tail -n 100 ~/.cache/graphify-rebuild.log
git status --short
~~~

Review the generated report, visualization, and any hook-produced changes. Commit only reviewed, portable graph artifacts with the source revision they describe. Do not use `git add .` for this cleanup; stage explicit paths after deciding how to handle the unexpected assistant-specific and machine-local files.
