# Chatbrief — current project handover

**Updated:** 2026-10-30  
**Repository:** https://github.com/hosmaznazfar/Chatbrief  
**Active branch:** `refactor/chatbrief-package-layout`  
**Verified GitHub HEAD before this handover update:** `4d2fed3cd15fa4164eb7ce697a762d8dea0088fa`  
**Branch comparison:** 107 commits ahead of `main`, 0 behind (at the verified comparison).  
**Local worktree:** unknown; GitHub cannot show local uncommitted changes.

## Product purpose

Chatbrief is an asynchronous AI-powered messaging digest application. It collects messages from configured Telegram channels, filters irrelevant content, summarizes and groups useful information with configurable AI providers, and delivers readable digests on demand or on a schedule.

The current implemented platform adapter is Telegram. Bale is a future adapter target; the enum/configuration boundary exists, but no Bale source, sender, or bot adapter is implemented.

The project also includes SQLite/PostgreSQL storage, extension hooks for filters and prompts, configurable digest grouping, and an optional MCP server.

## Current architecture

- Python package: `src/chatbrief/`; imports use `chatbrief.*`.
- Root `main.py` is the application composition root.
- `PlatformBuilder` constructs the selected platform's `MessageSource`, `MessageSender`, and `Bot`.
- Platform-neutral contracts live in `chatbrief.platforms.base`.
- `CommandService`, `DigestScheduler`, digest collection/building, storage, formatting, summarization, and MCP logic receive platform-neutral dependencies.
- Telegram-specific authentication, fetching, channel/message URL generation, sending, and bot command handling live under `chatbrief.platforms.telegram`.
- `Message` remains platform-neutral. Individual message links are represented by `Message.link`; channel URL generation belongs to the `MessageSource` adapter.
- `PlatformBuilder` is the sole platform-construction path. The obsolete `chatbrief.platforms.factory` module has been removed.

## Package/platform refactor status

**Status: implementation migration ready for validation.**

The code and test migration work on this branch is complete. Validation is deliberately still pending.

Completed in this work:

1. Migrated test imports to the canonical `chatbrief.*` package paths, including the Telegram and extension tests.
2. Replaced the legacy `tests/test_core.py` suite with `tests/test_digest.py`, migrating its behavior coverage to the focused digest collector, builder, service, cache, and validator modules. The tests were migrated rather than simply discarded.
3. Added `tests/platform/test_builder.py` for Telegram adapter construction, command-service injection, and the explicit unsupported-Bale behavior.
4. Updated `tests/conftest.py` to construct `Config` with the required `Platform.TELEGRAM` value.
5. Removed the obsolete platform factory. The standalone summarizer utility now obtains its source through `PlatformBuilder`.
6. Made `TelegramBot` require an injected `CommandService`; removed its stale service-construction fallback and adapter-level application entry point. Root `main.py` remains responsible for wiring and startup.
7. Updated `PlatformBuilder.create_bot()` and `main.py` to pass the already-constructed command service.
8. Updated `CommandService` tests to verify injected source/sender dependencies and sender-based cleanup.
9. Fixed the remaining type-checking-only `src.chatbrief.*` import in the prompt protocol.
10. Validated package-data configuration by inspection: the bundled prompt template is included by setuptools.
11. Aligned coverage configuration with the installed package name: `chatbrief` in pytest, CI, Makefile, and `pyproject.toml`.
12. Updated the README, config example, Dockerfile, Compose service, session helper, and localized UI branding for Chatbrief. Docker Compose now builds the local `chatbrief:latest` image; the README no longer claims an unverified GHCR image is published.
13. Updated the bundled prompt default to the canonical package path while retaining compatibility with the previous `src/prompts/base_summary.txt` setting.
14. Archived the completed extensibility and storage implementation plans under `docs/plans/completed/`. Their original paths and commands remain as historical design context; implementation items are checked off where verified, while validation items remain unchecked.

A source/test import review found no remaining imports rooted at a top-level `src.*` package. Historical documentation under the archived plans and ADRs may still mention the original pre-package paths; those references are intentionally retained as historical context.

## Remaining before the refactor can be declared complete

1. Review the committed branch changes in the developer's local checkout after checking `git status`; preserve any local work before pulling.
2. Perform the final local static review and resolve any issues found.
3. Wait for the developer to explicitly authorize validation. Do not run the full test suite before that approval.
4. Once authorized, run the configured checks, including Ruff lint/format, Pyright, and pytest. Also run the repository's configured Pylint, Bandit, and Vulture checks as appropriate.
5. Record the actual command output and fix any failures before declaring the refactor complete.

No full tests or quality checks have been run during this work. The historical pre-refactor baseline (471 passed, 7 skipped, 80.28% coverage) is not evidence that this branch currently passes.

## Graphify state

Graphify remains optional local development tooling, not an application dependency or required Python check.

The developer indicated the graph-refresh step had already been handled and did not request another refresh. No local Graphify command was run in this session.

The verified GitHub tree currently contains `graphify-out/graph.json` and `graphify-out/manifest.json`; `GRAPH_REPORT.md` and `graph.html` are not present in that remote snapshot. The tracked `.graphify_analysis.json` and `.graphify_root` files also remain in the branch. Treat the committed graph as an aid, not as proof of current local state; verify important relationships against source and tests. Any Graphify artifact hygiene is a separate follow-up and is not a blocker for the package/platform code migration.

## Workflow and safety rules

- Follow `docs/AI_WORKFLOW.md` and `AI_README.md` for graph-first exploration, research before material design decisions, small reviewed implementation steps, and commit-per-step development.
- Keep platform-specific behavior inside adapters. Do not add Bale credentials/configuration that imply Bale is implemented.
- Keep Graphify optional and outside runtime dependencies and `.pj/workflow.toml`.
- Preserve user changes. Do not stage, commit, push, merge, deploy, publish, or run migrations without the applicable authorization.
- Report validation as passed, failed, skipped, or not run. Never claim an unperformed check.

## Immediate next action

The implementation changes are committed to `refactor/chatbrief-package-layout`. The developer should inspect local status and bring the branch into the local checkout without overwriting uncommitted work. When satisfied that the implementation is ready, explicitly authorize validation; until then, keep the full test suite deferred.
