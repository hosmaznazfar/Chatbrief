# Chatbrief — AI-assisted development workflow

This is the **shared workflow contract for every AI assistant and development tool** used on Chatbrief: ChatGPT, IDE assistants, terminal agents, code-review tools, and human-led sessions. It is not tied to one assistant, editor, model, or vendor. Tool-specific conveniences may differ, but the project rules, Graphify usage, Git discipline, validation requirements, and handover expectations apply equally to all of them.

This document adapts the reusable workflow defined in [AIWorkFlow](https://github.com/hosmaznazfar/AIWorkFlow) to Chatbrief's actual Python/Astro stack and its local Graphify CLI integration. Slash commands below are conversation conventions, not native commands required from any particular assistant.

## Goals

- Keep project context, architecture decisions, plans, checklists, and handovers in Git.
- Give every AI assistant the same architecture and code-relationship context through the committed Graphify artifacts.
- Use Graphify locally to maintain a code relationship graph and commit reviewed, portable artifacts to GitHub before implementation decisions when the graph needs refreshing.
- Follow the developer's graph-first, research-before-decision, stepwise-implementation, and commit-each-step workflow for every feature or bug fix.
- Use `pj` as the single project-local command interface for Python checks and Graphify automation.
- Preserve safe, reviewable Git operations: no implicit staging, commits, pushes, merges, deployments, or migrations.
- Avoid dependencies on any one AI vendor, editor, plugin, MCP server, or proprietary agent integration.

## Project workflow files

| File | Responsibility |
|---|---|
| AI_README.md | Operational instructions for AI-assisted development |
| CHATGPT_CONTEXT.md | Persistent project architecture and decisions |
| docs/AI_WORKFLOW.md | Shared workflow contract for all AI assistants and tools |
| docs/GRAPHIFY.md | Graphify installation, local commands, Git hooks, and graph-sharing rules |
| docs/CHATGPT_NEW_CHAT_STARTER.md | Prompt for starting a new ChatGPT session |
| docs/handover/current.md | Current verified project state and next actions |
| FEATURE_IMPLEMENTATION_CHECKLIST.md | Non-trivial change checklist |
| docs/adr/ | Accepted architecture decisions |
| docs/plans/ | Approved implementation plans |
| .pj/workflow.toml | Ordered project quality checks |

All assistants should read the relevant project instructions before significant work. Treat handovers as snapshots and verify current GitHub state and source before relying on them.

## Mandatory rules for every AI assistant

These rules apply regardless of whether the work is performed through ChatGPT, an IDE, a terminal agent, a code-review assistant, or a human-operated workflow.

1. **Check the repository state first.** Establish the repository, target branch, latest commit, and whether the available source/graph is current. Never assume that a local worktree and GitHub have the same state.
2. **Use Graphify before broad source exploration when the graph is available.** For a codebase question, first run a focused `graphify query "<question>"`; use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<symbol>"` for a focused concept. If the CLI is unavailable but committed graph artifacts are accessible, inspect those artifacts instead. If neither is accessible, explain the limitation and trace the source directly.
3. **Use the graph to navigate, not to prove.** Verify task-critical relationships, callers, dependencies, and behavior in actual source, tests, configuration, and ADRs. Treat inferred edges as leads, not facts.
4. **Read only relevant source after graph navigation.** Use graph results to locate relevant files and symbols; avoid indiscriminate repository-wide grep or reading unrelated files. Read broader architecture reports when the task requires broad context.
5. **Respect project architecture and existing decisions.** Do not invent abstractions, platform support, configuration, or dependencies. Check ADRs and update them when a material architecture decision changes.
6. **Keep changes scoped and reviewable.** Do not overwrite unrelated user changes, silently broaden scope, or make destructive changes without explicit approval.
7. **Do not claim unperformed validation.** Report exactly which commands ran and their results. Do not run the full test suite until the developer declares the current package/platform refactor ready for validation.
8. **Refresh the graph before implementation decisions when needed, and after source changes.** Use the local `pj` graph commands; review generated changes and keep graph artifacts aligned with the source revision.
9. **Follow the task's Git authorization.** For this developer's requested workflow, commit each reviewed implementation step and its related documentation directly to the intended branch when direct Git changes/commits are authorized. Never push, merge, deploy, or run migrations without explicit authorization. If direct Git access or commit authorization is absent, prepare the exact changes and ask for the required action.
10. **Update the handover at meaningful milestones.** Record verified facts, checks, graph freshness, blockers, and next steps; distinguish supplied local evidence from independently verified remote state.

No assistant-specific Graphify plugin, skill, MCP server, editor extension, or Codex hook is required by this workflow. An assistant may use its own ordinary capabilities to read repository files, but it must follow the same Graphify-first navigation and verification rules above. The supported shared integration is the standalone local Graphify CLI, `pj`, generated graph artifacts in Git, and local Git hooks.

## Lifecycle

### Starting a session

1. Verify repository, branch, latest GitHub commit, and current local worktree state when local work is relevant.
2. Read AI_README.md, CHATGPT_CONTEXT.md, this document, docs/handover/current.md, FEATURE_IMPLEMENTATION_CHECKLIST.md, README.md, and relevant ADRs/plans.
3. Check whether `graphify-out/graph.json` and `graphify-out/GRAPH_REPORT.md` exist on the exact GitHub branch/commit or in the local worktree being used.
4. For a codebase question, query Graphify first when available. Use the graph to locate relevant modules, symbols, callers, dependencies, and likely impact areas.
5. Read the relevant source/tests/configuration and verify task-critical graph relationships. The graph is a navigation aid, not an authority.
6. Reconcile any mismatch between the handover, graph, and current source before making claims.

### Feature work — required developer workflow

Follow this order. Do not skip the graph review or decision gates.

1. **Inspect the current state.** Verify repository, branch, latest commit, worktree state when available, and the current graph revision. Query the graph to locate relevant modules, symbols, callers, dependencies, and likely impact.
2. **Request a fresh graph for each non-trivial feature, bug fix, or code review.** After the initial source/relationship inspection, ask the developer to run the local refresh so the graph is regenerated against the current checkout:
   ```bash
   ./pj graph refresh
   ./pj graph diff
   ```
   The developer reviews the Git changes and commits any changed, portable graph artifacts. If the refresh produces no graph diff, no graph-only commit is needed. Then inspect the refreshed graph and matching source revision from Git before presenting decisions.
3. **Verify the implementation context.** Trace the graph findings against actual source, tests, configuration, ADRs, and relevant documentation. Identify the real behavior and boundaries before proposing a design.
4. **Present decisions before implementation.** List every material decision that affects architecture, APIs, data models, dependencies, platform behavior, migration, compatibility, or user-visible behavior. Research current options online when external facts, project/library capabilities, or changing best practices matter. Cite sources, compare viable options and trade-offs, recommend one with reasons, and ask the developer to choose. Do not silently decide or start application-code changes while material choices remain unanswered.
5. **Agree on scope and sequence.** Once decisions are answered, state the approved design, acceptance criteria, non-goals, risks, and small implementation steps. Keep existing planning/migration documents accurate during work, but complete their final migration/planning updates after implementation is finished.
6. **Implement one step at a time.** Apply the approved changes directly to the intended Git branch when repository write access is available. After each step, inspect the complete diff, update the related code documentation/tests/ADR as needed, and commit that step before starting the next. Keep commits focused and explain their contents. Do not bundle unrelated steps.
7. **Keep the graph aligned.** After code relationships change, ask the developer to refresh the local graph with `./pj graph refresh`, inspect `./pj graph diff`, and commit reviewed graph artifacts with the source revision they describe. Do not claim the remote graph is current until the refreshed artifacts are committed and visible on the branch.
8. **Finish the documentation and validation.** After all implementation steps, update the relevant migration and planning Markdown files to reflect what actually changed, completed/deferred work, and remaining migration tasks. Run only the checks authorized and appropriate for the current refactor phase.
9. **Close the task.** Review the branch diff and commit sequence, update `docs/handover/current.md`, and report exact commits, checks, graph state, remaining risks, and next actions.

If direct Git write access or commit authorization is not available, do not pretend to have applied or committed changes. Provide the exact patch/commands and ask the developer to perform the local Git actions.

### Bug fixing

1. Characterize or reproduce the behavior and verify the branch/revision.
2. Query the graph and inspect the relevant relationships. Ask the developer to run `./pj graph refresh` and `./pj graph diff`; the developer commits any reviewed graph changes, then inspect the refreshed graph from Git.
3. Trace the actual implementation, tests, configuration, and ADRs to establish the root cause.
4. Present material fix options. Research current external/library facts online where relevant, explain trade-offs, and ask the developer to choose before changing code.
5. Implement the approved fix in small steps; review each diff, update related docs/tests, and commit each completed step.
6. Refresh and commit graph artifacts when code relationships change. After the fix is complete, update relevant migration/planning documents, validate as authorized, and record evidence in the handover.

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

Graphify runs on the developer's machine as a standalone CLI. The CLI is the shared mechanism; individual AI assistants do not need their own Graphify integration.

Install the standalone CLI:

~~~bash
./pj graph install
~~~

Build the initial code-only graph:

~~~bash
./pj graph build
~~~

At the start of each non-trivial feature/fix/review, and whenever the graph needs another complete refresh:

~~~bash
./pj graph refresh
./pj graph diff
~~~

`refresh` updates/builds the code graph, runs Graphify's `cluster-only` step to generate the report and HTML, and prints artifact status. `diff` shows Git status and tracked graph changes against HEAD. Review and commit only portable graph artifacts before continuing.

For a graph-only incremental update without report generation:

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

The default `pj` build/update commands set `GRAPHIFY_BACKEND=none`. Code extraction is local and does not require an API key. Semantic extraction of documents is opt-in via `--semantic` and uses the configured Graphify backend; do not enable it without deciding where document content may be processed.

Graphify hooks refresh code relationships after commits and branch changes. Run `./pj graph sync` after pulling or merging. Review `.gitattributes` changes and all generated artifacts.

### Complete the graph artifacts

A successful code extraction does not necessarily mean all shareable graph artifacts have been generated. If Graphify reports that `cluster-only` is the next step, run it explicitly from the repository root:

~~~bash
graphify cluster-only .
./pj graph status
~~~

Before calling the graph complete, confirm that the expected artifacts exist:

- `graphify-out/graph.json` — machine-readable code graph.
- `graphify-out/GRAPH_REPORT.md` — human-readable architecture/community report.
- `graphify-out/graph.html` — graph visualization.
- `graphify-out/manifest.json` — include when generated and confirmed portable.

After `./pj graph sync` or `./pj graph update`, regenerate the report/visualization with `graphify cluster-only .` when they are missing or stale. A missing report does not mean code extraction failed; it means the artifact-generation process is incomplete.

Review generated files before staging. Internal analysis data, cache files, root markers containing absolute machine paths, credentials, and other machine-local state are not automatically shareable artifacts. Do not commit them merely because Graphify generated them. Do not assume assistant-specific files such as `.codex/hooks.json` or agent instruction files are required for this project workflow.

See docs/GRAPHIFY.md for command details, output tracking policy, hook behavior, and troubleshooting.

## Source-to-GitHub handoff

The graph and source should describe the same project revision.

Recommended local graph-review cycle:

~~~bash
./pj graph refresh
./pj graph diff
~~~

Review the graph artifacts and stage only the intended, portable files together with the corresponding source/documentation changes. For example, stage explicit paths rather than blindly staging the entire worktree:

~~~bash
git add src tests docs graphify-out/graph.json graphify-out/GRAPH_REPORT.md graphify-out/graph.html graphify-out/manifest.json
git diff --cached
~~~

Commit the reviewed graph artifacts with the source revision they describe. For implementation work, commit each approved code step and its related documentation after reviewing the staged diff. Graphify's post-commit refresh may finish asynchronously. Check the hook log and `git status --short` afterward. If the graph becomes modified after the commit, review and commit that graph update before pushing. Push the reviewed commits only when explicitly intended.

After a pull or merge:

~~~bash
git pull --ff-only
./pj graph refresh
./pj graph diff
~~~

Do not push, merge, deploy, publish, or run migrations without explicit authorization. For the developer's requested workflow, commit each reviewed implementation step when the task is authorized for direct Git changes. The developer reviews/commits local graph refreshes when the assistant cannot execute the local CLI. Do not use `git add .` without reviewing ignored and generated files.

## How AI assistants should use GitHub

An assistant working from GitHub can inspect only the committed repository state; it cannot run the developer's local CLI or access uncommitted files unless it has a separately authorized local execution environment.

For a project question or modification:

1. Verify the target branch and latest commit.
2. Read the committed graph report and inspect relevant graph JSON nodes/edges when available.
3. Use the graph to identify likely source files and relationships.
4. Read the actual source, tests, configuration, and relevant ADRs.
5. Verify all important graph claims against source.
6. If graph artifacts are missing or may be stale, say so and perform source-based tracing instead.
7. After proposing or implementing source changes, state that the local graph must be refreshed and reviewed before the source+graph update is committed and pushed.

Do not claim to have run local Graphify queries, refreshed the local graph, or inspected uncommitted files unless evidence from that environment was actually provided.

## pj command contract

The root `pj` script remains Python standard-library-only. Its existing check pipeline remains separate from Graphify:

~~~bash
./pj doctor
./pj workflow validate
./pj check --list
./pj check --dry-run
./pj check
~~~

Graphify commands are optional workflow operations. For the developer's normal feature/fix flow, prefer `refresh` followed by `diff` when the graph must be brought current and reviewed:

~~~bash
./pj graph install
./pj graph status
./pj graph build
./pj graph update
./pj graph sync
./pj graph refresh
./pj graph diff
./pj graph query "question"
./pj graph path "A" "B"
./pj graph explain "symbol"
./pj graph watch
./pj graph hooks install
./pj graph hooks status
./pj graph hooks uninstall
~~~

Graphify must not be added to `pyproject.toml`, `uv.lock`, Docker, or `.pj/workflow.toml`. Missing Graphify must not make `pj doctor` or Python quality checks fail.

## Chat workflow conventions

These are optional natural-language shortcuts for conversations; they do not require a specific assistant or tool.

- `/help` — explain the available workflow and safety rules.
- `/status` — inspect branch, GitHub HEAD, known local state, graph artifact availability, and validation evidence.
- `/feature <goal>` — inspect graph/source/docs/tests; request and review a graph refresh if needed; research material options and ask for decisions; then implement in committed steps and finish migration/planning docs.
- `/fix <problem>` — trace graph/source to establish root cause; research material fix options and ask for a decision; then implement and commit each approved step.
- `/trace <area>` — query graph paths and verify them against source; cite concrete files and symbols.
- `/review` — inspect the complete diff, architecture, tests, security, and graph freshness.
- `/test` — run only authorized checks; otherwise provide exact commands and request output.
- `/sync` — ask the developer to run `./pj graph refresh` and `./pj graph diff` when local execution is unavailable; inspect the committed graph update. Never claim local work was run when it was not.
- `/branch <name>` — verify target and preserve uncommitted work before switching.
- `/merge <source> -> <target>` — compare branches, inspect conflicts and validation, and require explicit approval before merging.
- `/handover` — update docs/handover/current.md with verified state, actual checks, graph status, and next steps.
- `/create` — use the plan-first process for a new feature or component.

## Chatbrief-specific guardrails

- The application package is under `src/chatbrief/`; root `main.py` remains the composition root.
- Keep digest/domain logic platform-neutral. Platform-specific behavior belongs in adapters.
- Use the existing `MessageSource` and `MessageSender` abstractions for platform interactions.
- Keep `Message` limited to intrinsic, platform-neutral message data.
- Do not implement Bale credentials/configuration as if a Bale adapter already exists.
- Preserve architecture decisions in `docs/adr/` and update an ADR when a material decision changes.
- Python requirement is `>=3.14`; use uv and the committed `uv.lock`.
- The Astro website under `website/` has its own `package.json` and `package-lock.json`.
- Do not run the full test suite until the developer explicitly declares the current package/platform refactor ready for validation. The historical pre-refactor test baseline is not evidence about the current branch.

## Handover contract

At meaningful milestones, update `docs/handover/current.md` with:

- repository, branch, and verified commit;
- objective and decisions;
- completed and in-progress work;
- changed files and commit links when available;
- checks actually executed and their evidence;
- graph artifact availability and whether freshness is verified;
- local-only or uncommitted state explicitly marked unknown unless supplied;
- blockers and exact next steps.

Never invent local state, graph freshness, command output, or test results.
