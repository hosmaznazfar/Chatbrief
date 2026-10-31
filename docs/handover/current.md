# Chatbrief — current project handover

**Updated:** 2026-10-31  
**Repository:** https://github.com/hosmaznazfar/Chatbrief  
**Active branch:** `upgrade/full-project-modernization`  
**Verified GitHub HEAD before this handover update:** branch created from `refactor/chatbrief-package-layout`; see the latest branch commit for the current HEAD.
**Branch comparison:** 117 commits ahead of `main`, 0 behind (at the verified comparison).
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
- `PlatformBuilder` is the sole application platform-construction path. The obsolete `chatbrief.platforms.factory` module has been removed.

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

The developer ran `./pj graph refresh` and `./pj graph diff` locally on
`refactor/chatbrief-package-layout`. The refresh completed, reporting 2,045 nodes,
4,822 edges, and 97 communities. The developer committed the resulting artifacts as
`214a215` and pushed that commit.

The developer then rebased onto the two remote documentation commits. The Graphify
post-rebase hook launched another background rebuild; the subsequent local status showed
additional modified files under `graphify-out/`. Those post-rebase changes remain local and
unreviewed in this handover. Do not assume they are portable or stage them blindly.

The committed report is a navigation aid only. Verify task-critical relationships against
source, tests, configuration, and ADRs. No local Graphify query was run by this GitHub-only
inspection.

## Workflow and safety rules

- Follow `docs/AI_WORKFLOW.md` and `AI_README.md` for graph-first exploration, research before material design decisions, small reviewed implementation steps, and commit-per-step development.
- Keep platform-specific behavior inside adapters. Do not add Bale credentials/configuration that imply Bale is implemented.
- Keep Graphify optional and outside runtime dependencies and `.pj/workflow.toml`.
- Preserve user changes. Do not stage, commit, push, merge, deploy, publish, or run migrations without the applicable authorization.
- Report validation as passed, failed, skipped, or not run. Never claim an unperformed check.

## Immediate next action

Phase 1 of the Telegram hybrid-ingestion plan has been inspected against the committed
source. The findings and an initial migration proposal are recorded in
`docs/plans/telegram-hybrid-ingestion.md`. The plan remains at approved target direction;
no application code or database schema has changed.

The following architecture decisions have now been approved and are recorded in
`docs/plans/telegram-hybrid-ingestion.md`:

- Shared, deduplicated message archive with per-user subscriptions and strict source-access
  boundaries.
- Public channels/groups are subscribable without administrator approval when the central bot
  can access them.
- Private sources require established access; sharing a private source with other Chatbrief
  users requires explicit authorization from its access owner.
- Collect only while at least one authorized subscription exists.
- When the last authorized subscription ends, retain messages for a configurable grace period
  (14 days by default); restore subscription before expiry to cancel pending deletion.
- Authorization revocation is immediate; retention does not preserve revoked-user access.

No application code, database schema, or migrations have changed. These are target-policy
decisions only.

The optional Telethon role is now also decided:

- Telethon is used only for explicit, user-requested historical backfill from chats accessible
  to that user's linked account.
- The central Bot API is the only continuous ingestion path.
- Telethon is not a continuous collector or automatic fallback when the central bot cannot
  access a source. Such a source can be backfilled, but will not receive ongoing updates under
  the approved scope.
- Users without linked accounts remain supported for bot-accessible sources; their historical
  lookback is limited to messages already in the shared archive.

No application code, database schema, or migrations have changed. These remain approved target
architecture decisions, not implemented capabilities.

The source-registration policy is now approved:
- Public channels and groups: registration through the bot's private chat, if bot access is available.
- Private groups: registration initiated by an administrator inside the group, with administrator verification.
- Private channels: a separate administrator-verification flow; an ordinary channel post is not sufficient proof of the human poster's identity.
- The verified source owner controls private-source sharing. Bot access alone does not establish Chatbrief ownership.

The source-registration decision above is approved. The remaining source-access policy
decision is now also approved:

- **Central-bot access is required for an active subscription.** A source accessible only
  through a user's linked Telethon account may be used for an explicitly requested, one-time
  historical backfill and summary.
- If the central bot cannot access that source, Chatbrief must not activate an ongoing
  subscription. Telethon must not be used as a continuous collector or automatic fallback.
- Once central-bot access is established, the user may activate an ongoing subscription;
  continuous collection then uses the central Bot API.
- This keeps the meaning of an active subscription consistent: it receives ongoing updates,
  rather than only a historical snapshot.

The implementation plan and this handover now record this decision. No application code,
database schema, or migrations have changed. These are approved target-architecture rules,
not implemented capabilities.

Continue with the next architecture/design step before Phase 2; do not begin application
implementation until the remaining design decisions and the Phase 1 migration proposal have
been reviewed.
