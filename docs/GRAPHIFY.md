# Graphify — shared code knowledge graph

Graphify is Chatbrief's optional code-graph integration for AI-assisted development. Its purpose is to make the relationships between modules, symbols, imports, calls, and other code elements available in the Git repository, so an assistant working from GitHub can inspect the same architectural map as a developer working locally.

Graphify is development tooling only. It is not imported by the application, is not a runtime dependency, and is not part of the `pj` Python check pipeline.

## Repository contract

The generated graph is a **versioned project artifact**. Commit the `graphify-out/` directory to the same branch as the source revision it describes.

The primary outputs are:

| File | Purpose |
|---|---|
| `graphify-out/graph.json` | Machine-readable graph containing nodes and relationships. This is the authoritative graph input for Graphify query/MCP tools and for AI inspection. |
| `graphify-out/GRAPH_REPORT.md` | Human-readable architecture summary, notable connections, and suggested questions. |
| `graphify-out/graph.html` | Interactive visualization for developers. |

Graphify may create additional support files depending on its version and analysis mode. Inspect generated output rather than assuming a fixed list. Do not commit credentials, local configuration, caches, or unrelated temporary files.

Do not add `graphify-out/` to `.gitignore`. The graph is intentionally shared through GitHub, not treated as a private local cache.

## Installation (optional, per developer machine)

Graphify requires Python 3.10 or newer. Install its isolated CLI with uv:

```bash
uv tool install graphifyy
graphify --version
```

The PyPI package is spelled `graphifyy` (two trailing y characters); the installed command is `graphify`.

For Codex, register the Graphify skill if it is not already installed:

```bash
graphify codex install
```

Installation and skill registration are local developer-machine setup. Do not add Graphify to `pyproject.toml`, `uv.lock`, Docker images, application startup, or `.pj/workflow.toml`.

Official references:
- [Graphify quickstart](https://graphiffy.com/docs)
- [Installation](https://graphiffy.com/docs/install)
- [CLI reference](https://graphiffy.com/docs/cli)
- [Tutorial](https://graphiffy.com/docs/tutorial)

## Build and refresh

Graph generation is performed from the coding assistant session using the installed skill. In Codex, the skill invocation uses `$graphify`:

First build (from the Chatbrief repository root):

```text
$graphify .
```

Refresh after meaningful source changes or after pulling changes from GitHub:

```text
$graphify . --update
```

The update mode re-scans changed files instead of rebuilding everything. If the installed Graphify version or assistant integration exposes a different invocation, follow its current official CLI/skill help rather than guessing.

Do not assume that installing the CLI or registering the skill has generated a graph. Confirm that the three primary output files exist and inspect the report before treating the graph as available.

## Git workflow: keep graph and source in sync

The graph is a snapshot. Refresh it **before** committing source changes so the source and graph can be reviewed and pushed together.

Recommended sequence:

1. Make the intended source/documentation changes.
2. Refresh the graph with `$graphify . --update` in Codex.
3. Inspect `graphify-out/GRAPH_REPORT.md` and the graph diff.
4. Check `git status --short` and confirm the graph describes the working tree you intend to commit.
5. Stage and commit the source changes and the reviewed `graphify-out/` artifacts together.
6. Push the branch when explicitly intended.

Do not rely on a post-commit hook as the only refresh mechanism for this workflow: a hook that updates the graph after a commit can leave the refreshed graph uncommitted and out of sync with the source commit. If a hook is used, inspect and commit its resulting graph changes afterward.

Never stage, commit, or push automatically as part of an AI workflow. The developer reviews and approves Git operations.

## Instructions for AI assistants using GitHub

When a task involves understanding, tracing, changing, or reviewing Chatbrief:

1. Verify the repository, requested branch, and latest GitHub commit.
2. Check whether `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json` exist on that exact branch.
3. Read the architecture report first for orientation. Inspect the relevant portion of `graph.json` when its size and available GitHub access make that practical.
4. Use graph nodes and edges to identify likely modules, symbols, dependencies, and call paths. Search the source and tests to verify every relationship relevant to the task.
5. Follow source references to their actual current definitions and call sites. Prefer source code, tests, and architecture decisions over a graph inference.
6. If the graph is missing, stale, incomplete, or unavailable through GitHub, say so. Continue by tracing the actual source; do not claim to have queried a local graph or MCP server.
7. Before proposing a substantial change, assess the graph's relevant callers/dependents and likely impact. After implementation, identify whether the graph needs refreshing.
8. Update this repository's tracked handover with graph availability/freshness only when verified.

Graphify labels relationships as extracted, inferred, or ambiguous. Treat inferred and ambiguous edges as leads to investigate, not established facts. Even extracted relationships must be checked against the current source when correctness matters.

### ChatGPT and local coding assistants

A local Codex session may use the Graphify skill/CLI directly. A ChatGPT conversation working through GitHub does not automatically have access to a developer's local filesystem or local Graphify MCP server. For ChatGPT, the committed `graphify-out/` artifacts are the shared handoff: read them from the selected GitHub branch along with the current source.

Do not state that ChatGPT queried Graphify MCP unless that integration was actually available and used in the current session.

## Workflow conventions

- `/status`: report whether graph artifacts exist on the selected branch and whether their relationship to the current source revision is verified.
- `/feature`: inspect the graph for relevant components and dependents, then verify against source/tests before planning.
- `/fix`: use graph paths to locate likely flow, then trace the actual implementation and regression coverage.
- `/trace`: use the graph to identify paths and relationships; cite concrete source paths and verify them.
- `/review`: check whether changed source files have corresponding graph updates and whether generated artifacts are appropriate for the diff.
- `/sync`: refresh the local graph when running in a capable local coding assistant, inspect generated changes, and never commit/push automatically.
- `/handover`: record whether the graph artifacts are present and committed; do not claim freshness without evidence.

## Limitations

- A committed graph can become stale if source changes are pushed without regenerating it.
- The graph is an aid to navigation and impact analysis, not a substitute for reading source, tests, configuration, or ADRs.
- Dynamic dispatch, reflection, runtime wiring, and framework behavior may not be represented completely.
- A ChatGPT GitHub integration can read committed artifacts but cannot refresh a graph on the developer's machine.
