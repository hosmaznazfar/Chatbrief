# Chatbrief — new chat starter

Copy the prompt below into a new ChatGPT conversation and replace the task.

```text
We are working in https://github.com/hosmaznazfar/Chatbrief.

First verify the current GitHub repository, intended branch, and latest commit. Read AI_README.md, CHATGPT_CONTEXT.md, docs/AI_WORKFLOW.md, docs/handover/current.md, docs/GRAPHIFY.md, FEATURE_IMPLEMENTATION_CHECKLIST.md, README.md, relevant ADRs/plans, and the current source/tests. Reconcile the handover with the actual branch. Do not assume the local working tree is clean or synchronized; ask me for local git status when needed.

Before broad source exploration, check whether graphify-out/GRAPH_REPORT.md and graphify-out/graph.json exist on the selected branch. Use the committed Graphify report/graph to locate relevant components and relationships, then verify important edges against current source, tests, and ADRs. If the graph is absent, stale, incomplete, or does not represent current code relationships, ask me to run `./pj graph refresh` and `./pj graph diff`; I will review and commit the portable graph artifacts, then you inspect the new graph commit together with its source revision. The graph is a navigation aid, not the source of truth. Do not claim access to my local filesystem or Graphify CLI.

Follow the project architecture: src/chatbrief is the Python package; main.py is the root composition entry point; platform-specific behavior stays behind MessageSource/MessageSender adapters; digest/domain logic stays platform-neutral. Preserve existing ADRs and avoid speculative abstractions.

For a new feature or bug fix, inspect the graph and source first. List every material design decision, research current options online when relevant, compare trade-offs, recommend an option, and ask me to decide before changing application code. Once decisions and scope are approved, implement one small step at a time directly in the intended Git branch; review each diff, update related docs/tests, and commit that step before proceeding. After implementation, finalize the relevant migration and planning Markdown files.

Do not run the full test suite until I explicitly say the current refactor is ready for validation. Never claim a command ran without actual output. Use uv and existing project tooling. Graphify is optional local development tooling managed through ./pj graph commands; it is not an application dependency or part of the Python check pipeline.

On my local machine, Graphify runs as a standalone CLI through `./pj graph refresh` and `./pj graph diff` (lower-level build/update/sync commands remain available). Do not configure Codex, an editor skill, or MCP. The graph artifacts are committed to GitHub with the source revision they describe. Do not claim to have refreshed the local graph unless I provide command output. For an authorized task, commit each reviewed implementation step; do not push, merge, deploy, publish, or run migrations without my explicit approval.

At the end, update docs/handover/current.md with verified GitHub branch/commit, completed changes, actual validation, graph artifact availability/freshness, deferred checks, blockers, and exact next steps. Commit each reviewed implementation step for an authorized task. Do not push, merge, deploy, publish, or migrate without my explicit approval.

My task: [DESCRIBE TASK]
```
