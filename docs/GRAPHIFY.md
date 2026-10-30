# Graphify — local CLI and Git-shared code graph

Chatbrief uses the standalone Graphify CLI to build and maintain a code knowledge graph locally. The generated graph artifacts are committed to GitHub so ChatGPT and other assistants inspecting the repository can understand code relationships without access to the developer's machine.

**This integration does not install or configure Codex, another AI editor, an assistant skill, or an MCP server.** Graphify is invoked locally through the project helper, **pj**.

Graphify is optional development tooling. It is not imported by Chatbrief, is not an application dependency, and is not part of the Python quality-check pipeline.

## What is shared through Git

The primary graph outputs are:

| Artifact | Purpose | Git policy |
|---|---|---|
| graphify-out/graph.json | Machine-readable nodes and relationships; suitable for graph-aware inspection and local CLI queries | Commit |
| graphify-out/GRAPH_REPORT.md | Human-readable architecture report, communities, and notable paths | Commit |
| graphify-out/graph.html | Interactive graph visualization | Commit |
| graphify-out/manifest.json (when generated) | Portable file manifest used to track indexed inputs | Commit |
| graphify-out/cost.json | Local run/cost metadata | Ignore |
| graphify-out/.graphify_python | Local Python interpreter path | Ignore |
| graphify-out/cache/ | Optional extraction cache; keep out of Git to avoid machine-specific/cache churn | Ignore |

Graphify may produce additional files as its version evolves. Review new files before staging them; do not assume every file under graphify-out/ is shareable. The repository's .gitignore excludes known local-only files while leaving the graph and report available to Git.

## Install the standalone CLI

Requirements: Python 3.10+ and uv. Chatbrief's pj itself still requires Python 3.14+.

~~~bash
./pj graph install
graphify --version
~~~

This runs uv tool install graphifyy. The PyPI package is graphifyy (double y); the installed executable is graphify.

No graphify install, graphify codex install, skill registration, editor configuration, MCP setup, application dependency, or API key is needed for the default code-only workflow.

## Build the initial graph

From the repository root:

~~~bash
./pj graph build
~~~

This invokes Graphify's headless local extraction in code-only mode (graphify extract . --code-only) with GRAPHIFY_BACKEND=none. It parses code locally using Tree-sitter and does not send code to an external model. It intentionally indexes code rather than semantically extracting Markdown/other documents.

For a deliberate semantic pass over supported documents, use:

~~~bash
./pj graph build --semantic
~~~

Semantic extraction may use the Graphify backend configured in the environment and can send document content to that provider. Use it only when you have configured and approved the backend/data handling. The default workflow remains local code-only.

## Update and synchronize

After source changes:

~~~bash
./pj graph update
~~~

After pulling or merging changes from GitHub:

~~~bash
./pj graph sync
~~~

- update runs Graphify's incremental update against the existing graph.
- sync builds the graph if it does not exist; otherwise it incrementally updates it.
- Both default to GRAPHIFY_BACKEND=none, keeping the operation local/code-only.
- Add --semantic only when you explicitly want Graphify's configured semantic backend to process changed documents.

The code-only update can update code relationships without an API key. If you change Markdown/ADR/documentation and want those documents semantically linked into the graph, run the semantic mode with a backend you have deliberately configured. Otherwise ChatGPT can still read those tracked documents directly from GitHub.

## Query the local graph

The local CLI can query the generated graph without an AI editor:

~~~bash
./pj graph query "how does digest collection reach message delivery?"
./pj graph path "MessageSource" "MessageSender"
./pj graph explain "PlatformBuilder"
~~~

These commands delegate to graphify query, graphify path, and graphify explain. Graphify labels relationships as extracted, inferred, or ambiguous. Treat inferred/ambiguous edges as investigation leads, and verify important relationships against source, tests, and ADRs.

## Git automation

Install Graphify's Git hooks once per local clone:

~~~bash
./pj graph hooks install
./pj graph hooks status
~~~

Graphify installs local Git hooks for post-commit, branch checkout, merge, and rewrite operations, and configures a merge driver for graph.json. Code-only graph refreshes run locally without an LLM. The install may also add a graphify-out/graph.json rule to the tracked .gitattributes; inspect and commit that project-level rule if it is appropriate.

After git pull or a merge, run ./pj graph sync to incorporate the incoming changes. The hooks do not replace this explicit post-pull step.

Uninstall only Graphify's hook sections and merge-driver configuration with:

~~~bash
./pj graph hooks uninstall
~~~

Graphify preserves unrelated hook content, but always inspect local Git configuration and .gitattributes before and after installation/removal.

### Recommended source-to-GitHub cycle

1. Modify source and tests.
2. Run ./pj graph sync before committing.
3. Review graphify-out/GRAPH_REPORT.md, the generated graph diff, and git status --short.
4. Stage the source changes and reviewed graph artifacts together.
5. Inspect the staged diff and commit.
6. Check ./pj graph status. Graphify's post-commit hook may finish its refresh asynchronously; if graph artifacts changed afterward, review and commit those changes before pushing.
7. Push only after the source and graph are in sync.

Example:

~~~bash
./pj graph sync
git status --short
git add src tests docs graphify-out
git diff --cached
git commit
./pj graph status
# If the hook produced a new graph diff, review and commit it.
git push
~~~

Do not blindly use git add . just to include the graph. Keep secrets, sessions, local caches, and unrelated generated files out of the commit.

Graphify never stages, commits, or pushes on behalf of the developer. pj also does not perform those Git operations automatically.

## pj graph command reference

| Command | Action |
|---|---|
| ./pj graph install | Install the standalone CLI with uv |
| ./pj graph status | Show CLI availability, primary artifact presence, Git graph changes, and hook status |
| ./pj graph build | Initial code-only local build |
| ./pj graph build --semantic | Build with configured semantic backend |
| ./pj graph update | Incremental local/code-only update |
| ./pj graph update --semantic | Incremental update allowing configured semantic backend |
| ./pj graph sync | Build if missing; otherwise update |
| ./pj graph query "question" | Query graph |
| ./pj graph path "A" "B" | Find a path between graph nodes |
| ./pj graph explain "symbol" | Explain a node and its connections |
| ./pj graph watch | Run Graphify's filesystem watcher (requires its optional watch extra) |
| ./pj graph hooks install | Install Graphify Git hooks and merge driver |
| ./pj graph hooks status | Inspect installed hooks and merge driver |
| ./pj graph hooks uninstall | Remove Graphify hooks and merge driver |

Graphify is deliberately not added to .pj/workflow.toml: it is an optional architecture tool, not a required test/lint check. pj doctor reports whether the CLI is installed but does not fail if it is absent.

## How ChatGPT uses the graph from GitHub

A ChatGPT session working through GitHub cannot execute the developer's local Graphify CLI or read the local filesystem. It can read the committed artifacts on the selected branch.

For project questions and changes, the assistant should:

1. Verify the repository, branch, and latest commit.
2. Read graphify-out/GRAPH_REPORT.md for broad architecture orientation.
3. Inspect the relevant nodes/edges in graphify-out/graph.json when practical.
4. Use graph paths to identify likely source files and call/dependency relationships.
5. Verify all task-critical relationships against the current source, tests, and architecture decisions.
6. State clearly if graph artifacts are missing or may be stale; continue by tracing source directly.

The graph is a navigation and impact-analysis aid, not the source of truth. Source code, tests, configuration, and ADRs remain authoritative.

## Official references

- [Graphify repository and CLI README](https://github.com/Graphify-Labs/graphify)
- [Graphify CLI reference](https://graphiffy.com/docs/cli)
- [Graphify installation](https://graphiffy.com/docs/install)
- [Graphify tutorial](https://graphiffy.com/docs/tutorial)


## Complete the report and visualization

The extraction command can successfully write `graphify-out/graph.json` without creating the human-readable report or HTML visualization. When Graphify prints a message recommending `cluster-only`, run that command from the repository root:

~~~bash
graphify cluster-only .
./pj graph status
~~~

Prefer `./pj graph refresh` to perform extraction/update and report generation in one command. Then run `./pj graph diff` to inspect the Git changes before committing. The expected shareable outputs are `graphify-out/graph.json`, `graphify-out/GRAPH_REPORT.md`, and `graphify-out/graph.html`; commit `manifest.json` when generated and confirmed portable. Do not consider the graph complete until the report and visualization are present. Repeat `graphify cluster-only .` after `./pj graph sync` or `./pj graph update` when those commands leave the report/visualization missing or stale.

Review generated files before staging. Internal analysis data and root markers may contain implementation details or absolute machine paths; do not commit them without verifying their purpose and portability. Likewise, do not assume assistant-specific files such as `.codex/hooks.json` or generated agent instruction files are required. Chatbrief's intended integration is the local CLI, pj commands, and Git hooks—not a Codex/editor/assistant integration.
