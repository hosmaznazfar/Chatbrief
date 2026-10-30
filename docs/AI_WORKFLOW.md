# Chatbrief — AI-assisted development workflow

This document adapts the reusable workflow defined in [AIWorkFlow](https://github.com/hosmaznazfar/AIWorkFlow) to Chatbrief's actual Python/Astro stack and its local Graphify CLI integration.

It describes the expected collaboration between the developer, local tools, GitHub, and ChatGPT. The slash commands below are conversation conventions, not native ChatGPT commands.

## Goals

- Keep project context, architecture decisions, plans, checklists, and handovers in Git.
- Use Graphify locally to maintain a code relationship graph and commit its portable artifacts to GitHub.
- Let ChatGPT inspect the same committed graph and source when answering questions or proposing modifications through GitHub.
- Use pj as the single project-local command interface for Python checks and Graphify automation.
- Preserve safe, reviewable Git operations: no implicit staging, commits, pushes, merges, deployments, or migrations.

## Project workflow files

| File | Responsibility |
|---|---|
| AI_README.md | Operational instructions for AI-assisted development |
| CHATGPT_CONTEXT.md | Persistent project architecture and decisions |
| docs/AI_WORKFLOW.md | This end-to-end workflow contract |
| docs/GRAPHIFY.md | Graphify installation, local commands, Git hooks, and graph-sharing rules |
| docs/CHATGPT_NEW_CHAT_STARTER.md | Prompt for starting a new ChatGPT session |
| docs/handover/current.md | Current verified project state and next actions |
| FEATURE_IMPLEMENTATION_CHECKLIST.md | Non-trivial change checklist |
| docs/adr/ | Accepted architecture decisions |
| docs/plans/ | Approved implementation plans |
| .pj/workflow.toml | Ordered project quality checks |

Read these files before significant work. Treat handovers as snapshots and verify current GitHub state and source before relying on them.

## Lifecycle

### Starting a session

1. Verify repository, branch, latest GitHub commit, and current local worktree state when local work is relevant.
2. Read AI_README.md, CHATGPT_CONTEXT.md, this document, docs/handover/current.md, FEATURE_IMPLEMENTATION_CHECKLIST.md, README.md, relevant ADRs/plans, and the source/tests.
3. Check whether graphify-out/GRAPH_REPORT.md and graphify-out/graph.json exist on the exact GitHub branch/commit.
4. Use the committed report and graph to locate relevant modules, symbols, callers, dependencies, and likely impact areas.
5. Verify task-critical relationships against current source, tests, configuration, and ADRs. The graph is a navigation aid, not an authority.
6. Reconcile any mismatch between the handover, graph, and current source before making claims.

### Feature work

1. Explore relevant source, tests, documentation, and graph relationships.
2. Define the problem, scope, acceptance criteria, non-goals, risks, and implementation phases.
3. Update the relevant plan and checklist.
4. Ask for approval before modifying application code when the request is exploratory or the implementation scope is not yet approved.
5. Implement in small phases, preserving existing conventions and architecture boundaries.
6. Add or migrate tests for changed behavior; do not remove coverage merely to make a refactor pass.
7. Refresh the local graph after relevant changes and review its diff.
8. Run only the checks authorized and appropriate for the current refactor phase.
9. Update the handover with actual changes, validation, graph state, blockers, and next actions.

### Bug fixing

1. Reproduce or precisely characterize the reported behavior.
2. Query the graph to locate the relevant flow, callers, dependencies, and likely blast radius.
3. Trace the actual implementation and tests to establish the root cause.
4. Propose the smallest appropriate fix and regression coverage.
5. Implement only the agreed scope, update the graph, and validate with the authorized checks.
6. Record evidence and remaining risks in the handover.

### Review

Review the complete diff for:
- correctness and preservation of existing behavior;
- architecture boundaries and dependency direction;
- security, privacy, credentials, and data integrity;
- configuration compatibility and error handling;
- localization and Persian/English behavior where relevant;
- tests and actual validation evidence;
- graph artifact freshness and accidental local-only files;
- documentation, checklist, ADR, and handover consistency.

Do not accept a graph edge as proof. Check the actual source and test behavior.

## Local Graphify workflow

Graphify runs on the developer's machine as a standalone CLI. Do not install assistant-specific Graphify skills or configure Codex, MCP, or editor integrations as part of this project workflow.

Install the standalone CLI:

~~~bash
./pj graph install
~~~

Build the initial code-only graph:

~~~bash
./pj graph build
~~~

After source changes:

~~~bash
./pj graph update
~~~

After git pull or merge:

~~~bash
./pj graph sync
~~~

Query locally:

~~~bash
./pj graph query "how does a collected message reach the digest sender?"
./pj graph path "MessageSource" "MessageSender"
./pj graph explain "PlatformBuilder"
~~~

Install Graphify's local Git hooks once per clone:

~~~bash
./pj graph hooks install
./pj graph hooks status
~~~

The default pj build/update commands set GRAPHIFY_BACKEND=none. Code extraction is local and does not require an API key. Semantic extraction of documents is opt-in via --semantic and uses the configured Graphify backend; do not enable it without deciding where document content may be processed.

Graphify hooks refresh code relationships after commits and branch changes. Run pj graph sync after pulling or merging. Review .gitattributes changes and all generated artifacts.

See docs/GRAPHIFY.md for command details, output tracking policy, hook behavior, and troubleshooting.

## Source-to-GitHub handoff

The graph and source should describe the same project revision.

Recommended local cycle:

~~~bash
./pj graph sync
git status --short
git add src tests docs graphify-out
git diff --cached
git commit
./pj graph status
~~~

Graphify's post-commit refresh may finish asynchronously. If the graph becomes modified after the commit, review and commit that graph update before pushing. Then push the reviewed commits when explicitly intended.

After a pull or merge:

~~~bash
git pull --ff-only
./pj graph sync
git status --short
~~~

Never stage, commit, or push automatically. Do not use git add . without reviewing ignored and generated files.

## How ChatGPT should use GitHub

ChatGPT working from GitHub can inspect only the committed repository state; it cannot run the developer's local CLI or access uncommitted files.

For a project question or modification:

1. Verify the target branch and latest commit.
2. Read the committed graph report and inspect relevant graph JSON nodes/edges.
3. Use the graph to identify likely source files and relationships.
4. Read the actual source, tests, configuration, and relevant ADRs.
5. Verify all important graph claims against source.
6. If graph artifacts are missing or may be stale, say so and perform source-based tracing instead.
7. After proposing or implementing source changes, state that the local graph must be refreshed before the source+graph update is committed and pushed.

Do not claim to have run local Graphify queries or refreshed the local graph unless command output from that environment was actually provided.

## pj command contract

The root pj script remains Python standard-library-only. Its existing check pipeline remains separate from Graphify:

~~~bash
./pj doctor
./pj workflow validate
./pj check --list
./pj check --dry-run
./pj check
~~~

Graphify commands are optional workflow operations:

~~~bash
./pj graph install
./pj graph status
./pj graph build
./pj graph update
./pj graph sync
./pj graph query "question"
./pj graph path "A" "B"
./pj graph explain "symbol"
./pj graph watch
./pj graph hooks install
./pj graph hooks status
./pj graph hooks uninstall
~~~

Graphify must not be added to pyproject.toml, uv.lock, Docker, or .pj/workflow.toml. Missing Graphify must not make pj doctor or Python quality checks fail.

## Chat workflow conventions

- /help — explain the available workflow and safety rules.
- /status — inspect branch, GitHub HEAD, known local state, graph artifact availability, and validation evidence.
- /feature <goal> — inspect graph/source/docs/tests, define scope and acceptance criteria, update the plan, and wait for approval before implementation.
- /fix <problem> — trace the graph and source to establish root cause, then propose a minimal fix and regression coverage.
- /trace <area> — query graph paths and verify them against source; cite concrete files and symbols.
- /review — inspect the complete diff, architecture, tests, security, and graph freshness.
- /test — run only authorized checks; otherwise provide exact commands and request output.
- /sync — refresh Graphify, inspect the generated diff, and report local Git state; never stage/commit/push.
- /branch <name> — verify target and preserve uncommitted work before switching.
- /merge <source> -> <target> — compare branches, inspect conflicts and validation, and require explicit approval before merging.
- /handover — update docs/handover/current.md with verified state, actual checks, graph status, blockers, and next steps.
- /create — use the plan-first process for a new feature or component.

## Chatbrief-specific guardrails

- The application package is under src/chatbrief/; root main.py remains the composition root.
- Keep digest/domain logic platform-neutral. Platform-specific behavior belongs in adapters.
- Use the existing MessageSource and MessageSender abstractions for platform interactions.
- Keep Message limited to intrinsic, platform-neutral message data.
- Do not implement Bale credentials/configuration as if a Bale adapter already exists.
- Preserve architecture decisions in docs/adr/ and update an ADR when a material decision changes.
- Python requirement is >=3.14; use uv and the committed uv.lock.
- The Astro website under website/ has its own package.json and package-lock.json.
- Do not run the full test suite until the developer explicitly declares the current package/platform refactor ready for validation. The historical pre-refactor test baseline is not evidence about the current branch.

## Handover contract

At meaningful milestones, update docs/handover/current.md with:
- repository, branch, and verified commit;
- objective and decisions;
- completed and in-progress work;
- changed files and commit links when available;
- checks actually executed and their evidence;
- graph artifact availability and whether freshness is verified;
- local-only or uncommitted state explicitly marked unknown unless supplied;
- blockers and exact next steps.

Never invent local state, graph freshness, command output, or test results.


## Graphify artifact completion check

A successful code extraction does not necessarily mean all shareable graph artifacts have been generated. If Graphify reports that `cluster-only` is the next step, run it explicitly from the repository root:

~~~bash
graphify cluster-only .
./pj graph status
~~~

After source changes or a pull/merge, run `./pj graph sync`, then regenerate the report/visualization with `graphify cluster-only .` when needed. Confirm that `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.html` exist before calling the graph complete or relying on the report for broad architecture review.

Graphify hooks may start a background rebuild after a commit. Check the log/status and Git diff after the hook finishes; review and commit any subsequent graph changes before pushing. Never stage or commit hook output automatically.

The project's Graphify integration is deliberately local CLI + pj + Git hooks. Do not add Codex, editor, MCP, or other assistant-specific integrations unless the developer separately requests them. Review unexpected generated files before staging; internal analysis files and absolute-path markers are not automatically shareable graph artifacts.
