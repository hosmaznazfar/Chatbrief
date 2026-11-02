# Chatbrief — current project handover

# Current status — 2026-11-02 (authoritative update)

> This section supersedes older status statements later in this handover. Historical notes remain for audit context; use this section for the current implementation stage.

- **Repository:** `hosmaznazfar/Chatbrief`
- **Active branch:** `refactor/chatbrief-package-layout`
- **Latest shared-archive implementation:** migration 4 is followed by typed identity/source repositories (`archive.py`), message/coverage repositories (`archive_content.py`), and focused tests in `test_application_archive.py` and `test_application_archive_content.py`. The implementation commits include `f435ee3`, `e37be5f`, `0524f87`, `de9af38`, and subsequent public-export/test fixes.
- **Local worktree:** not visible from the GitHub editing environment. Preserve local Graphify output and other uncommitted work when pulling.
- **Package/layout and platform-abstraction migration:** complete.
- **Dependency/package upgrades:** complete.
- **Step 3e validation:** developer-confirmed — focused delivery/storage tests **19 passed**; full suite **631 passed, 7 skipped**, coverage **93.40%**; Ruff lint passed; Ruff format passed (**8 files already formatted**); Pyright **0 errors, 0 warnings, 0 informations**.
- **Step 4a implementation and validation:** `ExportWorker` provides injected state-based phase dispatch, bounded concurrency, renewable leases, stale-handler cancellation, retry backoff, and bounded shutdown grace. Developer-confirmed validation on 2026-11-02: Ruff lint passed, Ruff format reported **102 files already formatted**, Pyright reported **0 errors, 0 warnings, 0 informations**, and pytest collected **652 tests** with **7 skipped** and **93.19% coverage**. The pasted output ended before pytest's final summary, so the exact passed count is not recorded.
- **Graphify:** optional development tooling for code navigation and impact analysis, not a runtime feature or implementation deliverable.
- **Step 4b-1 validation:** developer confirmed the migration-4 tests and validation checks passed. Seven PostgreSQL integration tests were skipped because `TELEBRIEF_TEST_PG_URL` was not configured; no PostgreSQL integration result is claimed.
- **Step 4b-2 implementation:** added typed repositories for identity/source/access/authorization/subscription records and for normalized messages/coverage intervals, plus focused tests. Local validation is pending. The repositories preserve identity-only users, distinguish technical access from user grants, never infer grants from subscriptions, preserve deletion markers, and coalesce only overlapping/adjacent complete coverage.
- **Next stage:** validate Step 4b-2 locally, then implement the authorization-aware export snapshot query. It must fail closed for unknown visibility, require active authorization for private sources, require available Bot API or the requesting user's own Telethon access, honor the requester's selection scope, exclude deleted/post-cutoff messages, and surface uncovered intervals. Never read or automatically backfill legacy message-history rows. Do not wire the worker into startup until real phase handlers exist.

> This section supersedes older status statements later in this handover. Historical notes remain for audit context; use this section for the current implementation stage.

- **Repository:** `hosmaznazfar/Chatbrief`
- **Active branch:** `refactor/chatbrief-package-layout`
- **Latest implementation commits:** `982f82f` (migration 3), `e455ccf` (fenced delivery repository), `0cd3686` / `c279805` (lease-aware delivery tests), `b887b24` (migration tests), `e8cc771` (plan), `6abb408` (checklist), and `342d3c1` (replacement-worker fencing assertion).
- **Local worktree:** not visible from the GitHub editing environment. Preserve local Graphify output and other uncommitted work when pulling.
- **Package/layout and platform-abstraction migration:** complete.
- **Dependency/package upgrades:** complete.
- **Step 1 validation:** developer-confirmed — focused tests **99 passed**, full suite **602 passed, 7 skipped**, coverage **94.73%**, Ruff lint passed, Pyright reported 0 errors/warnings/information, and Ruff format passed.
- **Step 3a validation:** developer-confirmed — focused tests **109 passed**, Ruff lint/format passed, Pyright **0 errors/warnings/information**, full suite **612 passed, 7 skipped**, coverage **94.42%**.
- **Step 3b validation:** developer-confirmed — focused tests **119 passed**, Ruff lint/format passed, Pyright **0 errors/warnings/information**, full suite **622 passed, 7 skipped**, coverage **94.07%**.
- **Step 3c validation:** developer-confirmed — Ruff lint/format and Pyright passed; full suite **627 passed, 7 skipped**, coverage **93.38%**.
- **Step 3d validation:** developer-confirmed — focused tests **33 passed**, Ruff lint/format and Pyright passed, full suite **629 passed, 7 skipped**, coverage **93.39%**.
- **Step 3e implementation:** delivery attempts now persist their creating worker ID and lease generation; starting and finishing attempts require the current live lease and exact attempt-generation match. Migration 3 and stale-worker tests are implemented remotely; local validation is pending.
- **Graphify:** optional development tooling for code navigation and impact analysis, not a runtime feature or implementation deliverable.
- **Next stage:** validate Step 3e. Then implement export worker orchestration with bounded concurrency, phase dispatch, and cooperative lifecycle shutdown; preserve lease fencing on all worker-owned mutations.

## Step 3b implementation update — delivery attempts and cleanup tasks

Implemented in source; local validation is not yet clean. Initial developer run: **118 passed, 1 failed** in the focused set; full suite **621 passed, 1 failed, 7 skipped**, coverage **94.02%**. Ruff lint found C901 in `_validate_finish_metadata`; Pyright found an optional SQLite row passed to `_cleanup_from_row`. The developer also confirmed Ruff format passed (**8 files already formatted**). Fixes for the test failure and both static-check issues are committed as `44ec74e`; rerun all checks before considering this slice validated. Added:

- `src/chatbrief/application_storage/delivery.py`: typed delivery-attempt and cleanup-task models, `ExportDeliveryRepository`, and `ExportCleanupRepository`.
- `src/chatbrief/application_storage/__init__.py`: public exports for the new repository APIs and models.
- `tests/test_application_delivery.py`: focused tests for primary/media attempts, owner scoping, sequential retries, ambiguous delivery handling, cleanup scheduling/retries, and cleanup survival after parent-job deletion.

Delivery attempts are created in short transactions and finalized only once. A failed attempt can be retried with a new number; an unresolved or delivery-unknown attempt blocks automatic retry to avoid duplicate sends. Media delivery requires a confirmed primary send. Successful primary attempts satisfy the existing `ready` transition guard. Telegram delivery identifiers remain confined to the restricted attempt table.

Cleanup tasks can target Telegram messages or opaque staging keys. They are created only for jobs owned by the supplied user, remain after parent-job deletion through the approved `ON DELETE SET NULL` relationship, and can be retried or moved to a terminal state. Due-task listing includes overdue-deadline pending tasks so a future worker can explicitly abandon them rather than silently dropping them.

No schema migration, external Telegram call, archive generation, filesystem cleanup, worker lease, or user-facing command was added. The developer must rerun local validation against `44ec74e`; this GitHub-only environment cannot execute `uv` checks. The new source changes also require a Graphify refresh/review.

## Step 2 validation follow-up — 2026-11-02

The developer confirmed that the focused lifecycle/migration/configuration tests and the full pytest suite passed after adding `pythonpath = .` to `pytest.ini`. Ruff lint, Ruff formatting, and Pyright had also passed in the preceding run. Exact follow-up pytest counts were not provided and are intentionally not inferred.

The developer then ran `./pj graph sync`; Graphify reported no code-graph topology changes. The developer reviewed/updated the graph and pushed `ab53ac1`. This graph revision predates the export repository source files added below and is now stale for the current source revision.

## Implementation update — application-state database foundation and startup lifecycle

**Step 1 — database foundation:** implemented and developer-validated.

- `src/chatbrief/application_storage/`: required application database boundary and SQLite migration runner.
- Migration 1: `export_jobs`, `export_delivery_attempts`, and `export_cleanup_tasks` with approved checks, foreign keys, and indexes.
- `application_storage.path` configuration defaults to `data/application.db`; the existing optional `storage.path` / `data/messages.db` remains independent.
- Focused migration/configuration tests cover schema creation/idempotency, FK activation, partial uniqueness, checksum drift, rollback, and path validation.

**Step 2 — application lifecycle:** implemented and developer-validated.

- Root `main.py` constructs and initializes `ApplicationDatabase` after configuration/logging and before platform services, scheduler, command service, bot, or MCP server construction.
- `ChatbriefApp` retains the initialized database object for future service/repository injection.
- Initialization failure follows the existing failure path and prevents the rest of the application from starting.
- `tests/test_application_lifecycle.py` covers startup ordering and fail-closed behavior.
- The developer confirmed the focused and full pytest runs passed after the pytest import-path correction. Ruff lint, formatting, and Pyright had passed in the preceding run.
- The database initializer owns a scoped connection and closes it before returning. It does not hold a persistent connection or pool, so no artificial shutdown close method was introduced.

**Step 3a — export-job repository:** implemented in source; local validation pending.

- Added `application_storage/exports.py` with typed job/state models and `ExportRepository`.
- Added job creation with opaque internal/export UUIDs, owner-scoped reads, active-job lookup, and atomic expected-state transitions.
- The partial unique index enforces one blocking job per user; the repository translates the specific conflict to `ActiveExportExistsError`.
- Invalid lifecycle edges and mutable-field changes are rejected. Terminal timestamps and JSON metadata are handled in the same short transaction. The generic transition API allows forward progress/failure only; cancellation, invalidation, and expiry are reserved for cleanup-aware operations.
- A `ready` transition requires a persisted successful primary delivery attempt and matching delivery/expiry timestamps. Delivery-attempt write APIs are intentionally not yet implemented, so this guard prevents premature readiness until that next slice lands.
- Added `tests/test_application_exports.py`; local checks have not yet been run for this slice.

No legacy message schema or data was modified, and no backfill was attempted.

**Graphify:** the developer's graph sync and pushed graph commit `ab53ac1` describe the code before Step 3a. Refresh and review Graphify after the current source slice is validated; do not stage generated artifacts blindly.

## Working rules for the implementation stage

1. Treat approved ADRs and plans as binding architecture; do not reopen decisions without a concrete implementation contradiction.
2. Distinguish approved target behavior from implemented behavior. Mark each implementation slice complete only after code and focused tests establish it.
3. Keep work small and reviewable. Start with the first dependency in the approved implementation sequence; avoid further broad design rounds.
4. Keep the optional legacy message-history store separate from the required application-state/export persistence store, and preserve the approved no-guessing rule for legacy data.
5. Recheck local Git status and Graphify rebuild completion before staging. Never stage generated Graphify changes blindly.
6. Report test results as developer-confirmed unless the exact command output is available in the current session.

---


**Updated:** 2026-11-02  
**Repository:** https://github.com/hosmaznazfar/Chatbrief  
**Active branch:** `refactor/chatbrief-package-layout`  
**Verified GitHub HEAD before this handover update:** branch created from `refactor/chatbrief-package-layout`; see the latest branch commit for the current HEAD.
**Branch comparison:** 117 commits ahead of `main`, 0 behind (at the verified comparison).
**Local worktree:** unknown; GitHub cannot show local uncommitted changes.

## Product purpose

Chatbrief is an asynchronous AI-powered messaging digest application. It collects messages from configured Telegram channels, filters irrelevant content, summarizes and groups useful information with configurable AI providers, and delivers readable digests on demand or on a schedule.

The current implemented platform adapter is Telegram. Bale is a future adapter target; the enum/configuration boundary exists, but no Bale source, sender, or bot adapter is implemented.

- The primary `export.json` uses separate top-level data sections (preferences, schedules, subscriptions, delivery history, messages, and source relationship records) with explicit export-scoped relationships; exact fields and reference format remain in detailed schema design.

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

**Status: completed; tests passed and dependency upgrades completed.**

The code and test migration work is complete. The developer has confirmed that tests now pass and all package/dependency upgrades are complete.

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

## Historical refactor checklist (superseded by the 2026-11-02 status update)

1. Review the committed branch changes in the developer's local checkout after checking `git status`; preserve any local work before pulling.
2. Perform the final local static review and resolve any issues found.
3. Wait for the developer to explicitly authorize validation. Do not run the full test suite before that approval.
4. Once authorized, run the configured checks, including Ruff lint/format, Pyright, and pytest. Also run the repository's configured Pylint, Bandit, and Vulture checks as appropriate.
5. Record the actual command output and fix any failures before declaring the refactor complete.

Historical note: the earlier handover recorded validation as pending. That statement is superseded by the developer's 2026-11-02 confirmation that tests passed. The pre-refactor baseline remains historical and should not be substituted for the current run's actual output.

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

## Historical next-action notes (superseded by the 2026-11-02 current-status section)

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

The Chatbrief user-identity decision is now approved:

- A user's Telegram ID, obtained when they start a private conversation with the central bot,
  is their Chatbrief identity.
- Do not introduce a separate email/password account system for this Telegram-first product.
- Optional Telethon account linking is separate from Chatbrief registration and is used only
  for explicitly requested historical backfill.
- Use the stable Telegram user ID, not username or display name, as the external identity key.
- Scope subscriptions, permissions, digest preferences, schedules, and delivery records to
  this Chatbrief user identity.

This is an approved target-architecture decision, not an implemented capability. No
application code, database schema, or migrations have changed.

The Telethon account-linking constraints are now approved:

- The linked Telethon account must be the same Telegram account as the Chatbrief identity. Linking verifies that the authenticated Telethon numeric user ID matches the Telegram user ID obtained through the central bot.
- Each Chatbrief user may have at most one active Telethon link.
- Replacing an existing link requires explicit confirmation and must revoke/invalidate the previous session.
- Linking or unlinking Telethon does not create, replace, or delete the Chatbrief identity, subscriptions, or digest preferences.
- Safe credential rotation and failed re-link behavior remain to be designed before implementation.

These are approved target-architecture rules, not implemented capabilities. No application code, database schema, or migrations have changed.

The private-channel registration authority decision is now approved:

- Any current Telegram channel administrator may register a private channel with Chatbrief and initially control its Chatbrief sharing policy.
- The channel creator does not have exclusive registration authority.
- Registration must verify that the person initiating it is a current channel administrator; a channel link or ordinary channel post alone is not proof.
- Other Chatbrief users still require explicit authorization before subscribing to a private source.

This is an approved target policy, not an implemented capability. No application code, database schema, or migrations have changed.

The private-channel administrator-loss policy is now approved:

- If the administrator who registered a private channel leaves it or loses Telegram administrator status, their Chatbrief management authority is revoked.
- Any current administrator of that Telegram channel may claim management of the existing Chatbrief source after current administrator status is verified.
- This avoids permanently orphaning private sources. It does not grant subscription access to other Chatbrief users automatically; explicit sharing authorization remains required.

This is an approved target policy, not an implemented capability. No application code, database schema, or migrations have changed.

The administrator-takeover permission behavior is now approved:

- When a new current Telegram channel administrator claims management after the previous manager loses administrator status or leaves, preserve existing Chatbrief sharing authorizations and subscriptions.
- The new administrator inherits management authority and may subsequently change the sharing policy.
- The takeover itself must not silently revoke existing users or interrupt their authorized subscriptions.

This is an approved target policy, not an implemented capability. No application code, database schema, or migrations have changed.

The same administrator registration, takeover, and permission-preservation policy is now approved for **both private channels and private groups**:

- Any current administrator may register either type of private source. For a private group, registration is initiated inside the group and the initiating user must be verified as a current administrator. Private channels retain their separate administrator-verification flow.
- If the registering administrator leaves or loses administrator status, their Chatbrief management authority is revoked.
- Any current administrator of that Telegram chat may claim management after verification.
- Existing sharing authorizations and subscriptions are preserved during takeover; the new manager may subsequently change the sharing policy.

This clarifies and extends the earlier channel-specific takeover decision to private groups. It is an approved target policy, not an implemented capability. No application code, database schema, or migrations have changed.

The no-verifiable-administrator behavior for private channels and groups is now approved:

- If Chatbrief cannot verify any current Telegram administrator, freeze management operations for that private source.
- While frozen, do not permit sharing-policy changes, new sharing authorizations, or new subscriptions.
- Preserve existing authorized subscriptions and archived messages; do not revoke existing users solely because management is temporarily unavailable.
- Continue or stop live ingestion according to the independent central-bot-access and authorized-subscription rules.
- When a current administrator is verified again, restore management without requiring existing users to subscribe again.

This is an approved target policy, not an implemented capability. No application code, database schema, or migrations have changed.

## Latest approved architecture decision — central bot access loss

The central-bot access-loss policy is now approved and recorded in
`docs/plans/telegram-hybrid-ingestion.md`:

- If the central bot loses access to a private source, mark it inaccessible and suspend live ingestion.
- Preserve existing subscriptions and sharing permissions in a suspended state, along with the shared archive.
- Notify affected subscribers that live updates are paused.
- Do not use Telethon as a continuous fallback; it remains historical-backfill-only.
- Automatically resume Bot API ingestion when access is restored, if at least one authorized subscription remains and the source's management/sharing rules permit it.
- Access restoration does not bypass the no-verifiable-administrator freeze policy.
- If all subscriptions end during the pause, apply the normal configurable archive-retention grace period.

This is an approved target policy, not an implemented capability. No application code,
database schema, or migrations have changed.

**Historical note — superseded 2026-11-02:** architecture decisions and the Phase 1 migration proposal have since been approved. Proceed with implementation under the current-status section at the top of this document. Before local work, synchronize the branch carefully
and preserve any uncommitted Graphify output; the handover records post-rebase Graphify
changes that were local and unreviewed.

## Latest approved message lifecycle behavior

The message edit/deletion behavior is now approved and recorded in
`docs/plans/telegram-hybrid-ingestion.md`:

- A reported edit updates the existing archived message; it does not create a second logical message.
- A deletion is reflected only when the Telegram integration receives reliable explicit deletion information. Chatbrief must not claim it can detect every deletion.
- Overlapping Bot API collection and Telethon backfill reconcile against the same stable source-message identity and update one record.
- Soft-delete versus hard-delete representation, edit history, and conflict resolution remain open schema/design details.

The user also raised the two-week message-retention default. The previously approved 14-day rule applies after the last authorized subscription ends. Clarification is pending on whether the user intends a different rule that expires every message 14 days after collection even while subscriptions remain active.

No application code, schema, or migrations have changed.

## Retention clarification — confirmed

The user confirms the previously approved archive-retention policy without change:
when the last authorized subscription to a source ends, retain that source's archived
messages for a configurable grace period, **14 days by default**. If an authorized
subscription resumes before expiry, cancel pending deletion and resume collection.
If the grace period expires with no authorized subscribers, delete that source's
archived messages.

This is not a per-message TTL: messages are not automatically deleted 14 days after
collection while an authorized subscription remains active. The 14-day default and
configurable grace-period behavior were already recorded in the architecture plan.

## Retention policy clarification — rolling message window

The user has clarified that the archive must also have a rolling per-source message
retention limit to prevent unbounded database growth. The architecture plan now records
two independent policies:

- **Rolling message retention:** keep only the most recent 14 days of messages per source
  by default, deleting older message records even while subscriptions remain active.
  This duration is configurable. Digest lookback and AI inputs must use only retained data.
- **Last-subscriber source grace period:** when the last authorized subscription ends,
  retain the source's remaining archive for a configurable 14-day grace period by default.
  A timely resubscription cancels full-source deletion, but cannot restore messages already
  removed by rolling retention. If the grace period expires without resubscription, delete
  the source's remaining archived messages and archive data.

These are separate controls: the source grace period does not extend individual message
lifetimes. Collection coverage for the retained window must be tracked independently so
pruning old messages does not falsely imply complete recent coverage.

This is an approved retention direction, not implemented behavior. No application code,
database schema, or migrations have changed.

## Digest behavior and scheduling requirements

The user has clarified and approved this target product behavior; it is recorded in
`docs/plans/telegram-hybrid-ingestion.md`:

- Users configure schedules per digest group, with patterns such as hourly, daily, or a
  selected weekday/time (for example, Saturday at 07:00).
- Each scheduled AI digest processes only messages collected since that digest group's
  previous successful digest boundary, not the entire 14-day archive on every run.
- A digest group can instead use a **raw collection mode** that skips AI and delivers
  messages collected during the configured interval together in the user's destination chat.
- Users can request a one-time digest for a selected group, choosing AI summary or raw
  collection mode, and a start point from now back to at most 14 days ago.
- One-time requests do not alter the recurring schedule or its next digest boundary.
- All modes remain subject to the rolling per-source 14-day archive, collection coverage,
  source authorization, and Telegram delivery limits.

Implementation details still to design include successful-boundary/idempotency semantics,
raw message presentation and media handling, and flexible schedule representation.
No application code, schema, or migrations have changed.


## Raw collection presentation — approved

The user selected **copied messages**, not Telegram forwards, for the per-digest-group
raw collection mode:

- Chatbrief delivers copies in the configured destination chat without Telegram's
  forwarded-message header.
- Source attribution must be added separately, with a source link where available.
- Exact attribution formatting, batching, media handling, and behavior for content
  that cannot be copied remain design details to verify against Telegram Bot API
  capabilities and limits.

This is an approved target behavior, not an implemented capability. The plan records
the decision in `docs/plans/telegram-hybrid-ingestion.md`. No application code,
database schema, or migrations have changed.

## Daylight-saving schedule behavior — approved

The user has approved the DST transition policy for per-user local digest schedules:

- If a scheduled local time does not exist during the spring-forward transition, run once at the next valid local time.
- If a scheduled local time occurs twice during the fall-back transition, run once at the first occurrence.
- This avoids missing a scheduled digest or delivering it twice.

The policy is recorded in `docs/plans/telegram-hybrid-ingestion.md`. It is an approved target behavior, not an implemented capability. No application code, database schema, or migrations have changed.

Timezone changes are now explicitly user-controlled; see the approved policy below.


The timezone configuration and change policy is now approved:

- Users explicitly configure their IANA timezone through Chatbrief bot commands.
- Do not infer or automatically change it based on VPN/IP location, device location, Telegram metadata, or other environmental signals.
- Normalize and store message timestamps and internal event timestamps in UTC.
- Interpret schedules in the user's explicitly configured timezone and convert UTC timestamps to that timezone for digest and user-facing display.
- When the user manually changes the timezone, apply it to all future schedule calculations and display conversions. Recalculate future schedule occurrences; never rewrite or shift stored UTC timestamps or historical records.

This supersedes the earlier open question about timezone-change behavior. The policy is recorded in `docs/plans/telegram-hybrid-ingestion.md`. It is an approved target behavior, not an implemented capability. No application code, database schema, or migrations have changed.

## Timezone setup prerequisite — approved

The user has approved requiring explicit timezone configuration before digest scheduling:

- A Chatbrief user must configure a valid IANA timezone before creating any digest schedule.
- Provide a bot command such as `/timezone Europe/Berlin`.
- Invoking `/timezone` without an argument displays the currently configured timezone and explains how to set or change it.
- An invalid IANA timezone identifier returns a clear error with valid examples and leaves the existing timezone unchanged.
- Do not silently default a user's scheduled digests to UTC when no timezone has been configured.
- Users may manually change their timezone at any time; the previously approved UTC-storage and local-time scheduling/display policy applies.

This requirement is recorded in `docs/plans/telegram-hybrid-ingestion.md`. It is an approved target behavior, not an implemented capability. No application code, database schema, or migrations have changed.

## Timezone changes preserve schedule wall-clock times — approved

When a user explicitly changes their configured timezone:

- Preserve the local clock time configured for each existing schedule. For example, a daily 07:00 schedule remains at 07:00 in the newly configured timezone.
- Recalculate future schedule occurrences using the new timezone.
- Do not alter past digest boundaries, completed executions, historical records, or stored UTC timestamps.

This is an approved target behavior recorded in `docs/plans/telegram-hybrid-ingestion.md`. It is not implemented; no application code, database schema, or migrations have changed.

## Hourly schedule semantics — approved

An hourly digest schedule uses elapsed-time scheduling:

- Run every 60 elapsed minutes, not at each local clock-hour boundary.
- Daylight-saving transitions must not skip or duplicate an hourly execution.
- The user's configured timezone controls display of execution timestamps, not the elapsed 60-minute interval.

This is an approved target behavior recorded in `docs/plans/telegram-hybrid-ingestion.md`. It is not implemented; no application code, database schema, or migrations have changed.

## Timezone changes during active digests — approved

If a user changes their timezone while a scheduled digest execution is already in progress:

- Allow the in-progress execution to finish under the schedule occurrence that triggered it.
- Apply the new timezone only to future schedule occurrences.
- Do not cancel or restart the in-progress digest.

This is an approved target behavior recorded in `docs/plans/telegram-hybrid-ingestion.md`. It is not implemented; no application code, database schema, or migrations have changed.

## Scheduled digest delivery retries — approved

The scheduled digest delivery policy is approved:

- Advance a digest group's successful boundary only after the complete digest has been delivered.
- On delivery failure, retain the previous successful boundary and retry delivery using the already-generated digest; do not regenerate the AI summary for each retry.
- Retry policy is configurable. Initial defaults are 3 retries after the initial attempt (4 total attempts), with delays of 1 minute, 5 minutes, and 15 minutes.
- Retry count and delays can be changed later through configuration.
- If all attempts fail, mark delivery as failed, keep the boundary unchanged, and notify the user. Do not silently skip the undelivered interval.
- Make retries idempotent where possible. Telegram has no universal idempotency key for sending messages, so ambiguous network failures can still occasionally produce duplicate delivery; implementation should minimize and account for this risk.

This is an approved target behavior recorded in `docs/plans/telegram-hybrid-ingestion.md`. It is not implemented; no application code, database schema, or migrations have changed.

## Partial digest delivery recovery — approved

For digests delivered as multiple Telegram messages:

- Track which messages have been confirmed delivered.
- If an attempt fails partway through, resume from the first message not yet confirmed delivered instead of resending the whole digest.
- Advance the digest group's successful boundary only after every message has been delivered.
- Account for ambiguous send outcomes and minimize duplicate delivery where possible.

This is an approved target behavior recorded in `docs/plans/telegram-hybrid-ingestion.md`. It is not implemented; no application code, database schema, or migrations have changed.

## Digest retry exhaustion and pending recovery — approved

After all configured delivery attempts are exhausted:

- Move the digest delivery into a pending-recovery state and notify the user.
- Preserve the generated digest and confirmed per-message delivery progress; do not advance the successful digest boundary.
- Do not retry continuously after exhaustion. Automatically resume when the system detects that the relevant delivery service is operational again, continuing from the first message not yet confirmed delivered.
- Retain the recovery record until delivery completes or an explicitly designed user/admin resolution path handles it. Never silently discard the undelivered interval.

This is an approved target behavior recorded in `docs/plans/telegram-hybrid-ingestion.md`. It is not implemented; no application code, database schema, or migrations have changed.


## Manual pending-digest recovery command — approved

The user approved a manual `/retry` command for pending digest deliveries:

- A user may request retry only for their own pending-recovery deliveries.
- Retry resumes the saved digest at the first message not confirmed delivered; it does not regenerate the AI summary or reset confirmed progress.
- The successful digest boundary advances only after the complete digest is delivered.
- When automatic retries are exhausted and a delivery enters pending recovery, notify the affected user and include clear instructions for using `/retry`.
- Include `/retry` in the bot's help/command guidance so it is discoverable.
- If exactly one delivery is pending, `/retry` retries it directly.
- If multiple deliveries are pending, `/retry` lists them with stable user-facing IDs; `/retry <id>` selects the intended delivery.
- A pending-recovery notification must include the delivery ID and exact `/retry <id>` instruction when selection is needed. If only one delivery is pending, it may simply tell the user to run `/retry`.
- IDs must be user-facing selection identifiers, not exposed internal database identifiers, and must never reveal another user's data.

This is an approved target behavior, not implemented. No application code, schema, or migrations have changed. The plan was updated in commit `20bc89d34a3e9320a40596ad3f5026e56bca9dcc`. No tests were run.


## Delivery recovery and diagnostics decisions — consolidated handover

The user has now approved the complete target behavior for scheduled digest delivery failure and recovery. The detailed requirements are recorded in `docs/plans/telegram-hybrid-ingestion.md`. The decisions made in sequence are:

1. **Retry policy:** configurable retry count and delays; initial default is 3 retries after the initial attempt (4 total attempts), delayed by 1 minute, 5 minutes, and 15 minutes. Retry the already-generated digest; do not regenerate the AI summary. Advance the digest group's successful boundary only after complete delivery.
2. **Partial delivery:** persist confirmed per-message delivery progress. If a multi-message digest fails partway through, resume from the first message not confirmed delivered rather than resending the entire digest. Account for ambiguous Telegram send outcomes and minimize duplicates; Telegram does not provide a universal idempotency key.
3. **Exhaustion and automatic recovery:** after all configured attempts fail, move the delivery into pending recovery, notify the user, preserve the generated digest and confirmed progress, and leave the successful boundary unchanged. Do not retry continuously after exhaustion. Automatically resume when the system detects that the relevant delivery service is operational again. Retain the recovery record until successful completion or an explicitly designed resolution path; never silently discard the interval.
4. **User `/retry` command:** users can manually recover only their own pending deliveries. It resumes the saved digest from the first unconfirmed message; it does not generate a new summary, create a new interval, or reset progress. Include `/retry` in ordinary bot help.
5. **Retry selection and notification IDs:** if the user has one pending delivery, `/retry` retries it directly. If multiple deliveries are pending, `/retry` lists them with stable user-facing IDs, and `/retry <id>` selects one. When selection is needed, the pending-recovery notification includes the ID and exact command. IDs are selection handles, not internal database IDs, and must not expose another user's data.
6. **User-facing status versus diagnostics:** ordinary bot messages and retry listings stay concise and non-technical. Do not expose stack traces, raw exceptions, credentials, tokens, or sensitive API responses to users.
7. **Administrator-only diagnostics:** provide `/status <id>` only for explicitly configured Telegram administrators. Do not include it in public/user help, command menus, or user recovery notifications. Enforce the administrator allowlist server-side on every invocation; merely hiding the command is insufficient. Unauthorized users must not obtain delivery details or discover whether another user's ID exists. An authorized administrator may see sanitized status, attempt count, last-attempt time, and a safe high-level failure category.
8. **Terminal logging:** full technical errors and stack traces belong in application terminal logs, with normal secret-redaction protections. The bot must not act as a remote terminal or raw-log viewer.

All of the above are approved target requirements, not implemented features. No application code, database schema, or migrations have changed. Documentation-only updates were made in this session:
- Plan commit: `272bb536c922bc456cb1f82789daf4fb61070bd4`.
- Handover update follows this plan update.
- No tests or application checks were run.

**Next design work:** continue resolving remaining architecture details one decision at a time. Do not start implementation or schema/migration work until the remaining decisions and Phase 1 migration proposal are reviewed and explicitly approved. Before any local work, inspect the working tree and preserve any uncommitted Graphify output; do not assume the local branch is synchronized.


## Raw media copying approved; image-aware AI summarization remains open

The user approved extending raw collection mode to copy supported media, not only text:

- Copy supported photos, videos, documents, audio, and voice messages with the original media where the Bot API permits.
- Add separate source attribution to copied media messages, including a source link where available.
- If an item cannot be copied, skip it and notify the user that the raw result is incomplete. Never silently report a partial result as complete.
- Exact Bot API support, batching, attribution formatting, and failure handling still require implementation-level verification.

The user also wants a future capability to summarize images. The plan now records this as a separate, unresolved design area: preserve media-type metadata and distinguish a media tag from actual image content being available to a vision-capable model. A possible per-digest-group choice is text-only versus text plus supported image content.

Image analysis is **not yet approved as a detailed behavior or implemented**. Media file download/storage/retention, access control, size and format limits, model capability/cost, and failure behavior remain open. In particular, the existing 14-day message-row retention policy does not yet define binary media-file retention.

Plan update: `ff7f7489f0b42ef06d0e274aa38f69a1e8a090d5`. This was a documentation-only update; no application code, schema, migrations, or tests were changed/run.


## Digest processing modes clarified and approved

The user confirmed that the previously discussed no-AI raw collection mode remains a distinct option alongside the two AI modes. Each digest group has three target modes:

1. **Raw collection (no AI):** copy supported messages and media to the configured destination with separate source attribution.
2. **AI text-only:** summarize message text without analyzing image contents. This is the default AI mode.
3. **AI text + images:** summarize text and analyze available image content using a vision-capable model, incorporating relevant visual information.

Raw collection is not an AI summarization scope. The two AI modes are separate choices within AI summarization. Media-file availability, storage/retention, access control, model support/cost, and failure handling remain open design details. No application code, schema, migrations, or tests were changed/run.


## Extensible AI media processing — approved direction

The user approved starting AI media analysis with images only while designing the architecture so additional media capabilities can be added later without major restructuring.

- Initial AI media analysis: images only (photos and image documents).
- Video, audio, and voice-message analysis are deferred future capabilities, not part of the initial implementation scope.
- Define a modular media-processing boundary with independently addable processors. Future examples include video/key-frame analysis, audio transcription and summarization, and voice-message processing.
- Keep media-type detection/availability separate from media-specific processing. Unsupported or unavailable media must not break ordinary text summarization or supported image analysis; define an explicit omission/fallback behavior.
- This extensibility requirement does not mean implementing all media processors now. Raw collection still aims to copy all supported media types under its separate approved behavior.

The plan also notes that media-file storage/retention, access control, model capability/cost, limits, and failure policy remain open. No application code, schema, migrations, or tests were changed/run.

## Media-file storage and retention — approved

The user approved a separate media-file retention policy, now recorded in
`docs/plans/telegram-hybrid-ingestion.md`:

- Store retained binary media separately from message records.
- Make media retention configurable, initially **14 days**.
- Delete a retained media file when its associated message expires; media must not outlive
  its message's retention lifecycle.
- Avoid downloading or persisting media that is not needed for an enabled/selected
  operation. Retrieve or retain it only when required for raw copying, supported AI image
  analysis, or another explicitly supported workflow.
- Apply the same source-authorization rules to media access as to the associated message.
  Shared storage must not imply shared access.

Media retention is independently configurable from message retention, while message
expiry triggers deletion of associated media. Exact storage backend, temporary-file
handling, cleanup scheduling, deletion guarantees, and access-control implementation
remain design details.

This is an approved target policy, not an implemented capability. The update was
documentation-only: no application code, schema, migrations, or tests were changed/run.
Plan commit: `5a766184b53ef96bdee71c986926bee6b680baac`.

## AI image-analysis failure behavior — approved

The user approved graceful handling when images cannot be analyzed in the AI text-plus-images
digest mode:

- Do not fail the entire digest because an image cannot be analyzed. Continue with available
  text and images analyzed successfully.
- Skip images that cannot be retrieved, are unsupported by the selected AI provider, exceed
  that provider's input limits (such as file size, resolution, or other documented
  constraints), or otherwise fail analysis.
- Add a concise note to the digest when images were skipped. Explain the reason when known,
  including provider format/support limitations and provider input-limit violations.
  Never imply all images were analyzed if some were skipped.
- Keep raw provider errors and low-level technical details in application logs, with normal
  secret redaction; do not expose them in user-facing digests.
- Verify supported formats and limits for the selected provider/model during implementation;
  do not assume universal limits.

This is an approved target behavior, not implemented. Documentation-only update; no
application code, schema, migrations, or tests changed/run.
Plan commit: `a28b532a64fad573c2820133fbac165c34cd7f15`.

## Chatbrief-side image limits before provider upload — approved

The user approved configurable image-processing limits enforced by Chatbrief before
images are uploaded for AI analysis:

- Maximum image file size.
- Maximum image dimensions/resolution.
- Maximum number of images included in one digest's AI image-analysis input.
- Optional compression or resizing when an image exceeds a preferred processing size but
  remains within hard limits and can be transformed safely.
- Images exceeding a hard Chatbrief-side limit are skipped, with the omission explained
  in the digest under the previously approved image-failure policy.

These local limits are separate from provider/model-specific input constraints, which must
also be checked against the selected provider's documented requirements. Exact numeric
defaults, transformation formats/quality settings, and configuration interfaces remain
open design details for implementation.

This is an approved target behavior, not implemented. Documentation-only update:
no application code, schema, migrations, or tests changed/run.
Plan commit: `478de64c8dd8e3b83b4ef170aec2e208b40a9a6f`.

### Initial Chatbrief-side image-limit defaults — approved

The user approved these initial configurable defaults for AI image processing:

- Maximum original image file size: **20 MB**.
- Maximum image width or height: **4096 pixels**.
- Maximum images included in one digest's AI image-analysis input: **10**.
- Preferred maximum dimension after resizing: **2048 pixels**.
- JPEG compression quality when compression is needed: **85%**.

These are initial application defaults, not universal provider limits or immutable
constraints. Keep them configurable. Provider/model-specific limits remain separate and
take precedence whenever stricter. Resize/compress only when safe; skip and report images
that exceed hard limits or cannot be processed safely.

This is an approved target configuration, not implemented. Documentation-only update:
no application code, schema, migrations, or tests changed/run.
Plan commit: `6dac337899a7aa53ae10374239d54b013368f086`.


## Deterministic image selection at the per-digest limit — approved

The user approved how Chatbrief selects images when a digest has more eligible images than
the configured maximum (initially 10):

- Select the most recent images by their associated message timestamps, up to the configured
  limit.
- Preserve chronological order among the selected images when sending them to the AI.
- Continue including all eligible message text; excluding images must not exclude their
  associated message text.
- Add a concise digest note stating how many images were omitted because the per-digest
  image limit was reached.
- Selection must be deterministic. If timestamps tie, implementation must use a stable
  tie-breaker based on source-message identity so repeated processing selects the same set.

This is an approved target behavior, not implemented. The plan was updated in commit
`d89c927a39bfbf87348d844f166a6403430ecff4`. Documentation-only change: no application code,
schema, migrations, or tests changed/run.


## Initial AI image formats — approved

The user approved the initial image formats for AI image analysis:

- JPEG/JPG, PNG, and WebP are in scope initially.
- GIF is deferred because animated-image frame selection/extraction needs separate design.
- Other formats may be considered later.
- Provider/model-specific format support must still be checked independently. Local format
  support does not guarantee provider acceptance; use the previously approved graceful
  omission behavior when an image cannot be analyzed.

This is an approved target scope, not implemented. The plan was updated in commit
`33875a39b6422ddbbcf0de156cb88c1e2e9fe443`. Documentation-only change: no application code,
schema, migrations, or tests changed/run.


## Safe image transformations for AI analysis — approved

The user approved the image-transformation policy:

- Preserve the original format when resizing/compression can be done safely in that format.
- Convert PNG or WebP to JPEG only when needed for selected provider/model compatibility
  or to reduce image size.
- Preserve transparency where supported. Do not silently flatten transparent content onto
  an arbitrary background. If conversion to a format without transparency is necessary,
  use an explicitly defined safe policy or skip/report the image.
- Never modify the retained original media file. Transform a separate processing copy and
  apply appropriate temporary-file cleanup/security handling.

This is an approved target behavior, not implemented. The plan was updated in commit
`94ac07237d4ac9d3099efc68e5fb1d5518a15cfe`. Documentation-only change: no application code,
schema, migrations, or tests changed/run.


## Temporary media-processing files — approved

The user approved the temporary-file handling policy for media retrieval and image
transformation:

- Use a dedicated temporary directory separate from permanent/retained media storage.
- Generate unpredictable filenames; never use Telegram-provided filenames directly as
  filesystem paths.
- Apply restrictive filesystem permissions so other local users cannot read temporary
  originals or transformed copies.
- Delete temporary downloaded originals and transformed copies after processing, whether
  processing succeeds or fails.
- Ensure cleanup also handles interrupted processing and application restarts, including
  safe identification/removal of abandoned temporary files.

This is an approved target policy, not implemented. Exact directory placement, permission
details, cleanup scheduling/recovery, and implementation mechanics remain to be specified.
Documentation-only update: no application code, schema, migrations, or tests changed/run.
Plan commit: `e1f98856a309803860f723510fefdbff7963c28c`.


## Recovery cleanup for abandoned temporary media files — approved

The user approved extending temporary-file cleanup beyond normal processing completion:

- Run cleanup at application startup to identify and remove abandoned files in the
  dedicated temporary directory.
- Run periodic cleanup while the application is running.
- Protect files belonging to active processing operations. Use a reliable mechanism to
  distinguish active work from abandoned files (for example, operation ownership/leases
  together with an age threshold); do not delete files simply because an operation is slow.
- Restrict cleanup to Chatbrief's dedicated temporary directory.

The exact active-operation tracking, age threshold, cleanup cadence, and failure handling
remain implementation details. This is an approved target behavior, not implemented.
Documentation-only update: no application code, schema, migrations, or tests changed/run.
Plan commit: `6dfa7121f101c0ba000ddb04af0a1212820596e2`.

## Media access authorization at every operation — approved

The user approved enforcing source authorization for media at every access/processing
boundary, not only when a digest is requested:

- Check authorization before downloading or retrieving media.
- Check authorization before reading, processing, or sending retained media.
- Never expose permanent/temporary media paths or internal storage identifiers to users.
- Prevent one user's authorization context from being reused to retrieve another user's media.
- Recheck authorization for delayed/queued jobs so revocation after job creation prevents
  subsequent media access or delivery.

This is an approved target security policy, not implemented. Exact enforcement boundaries
and implementation mechanics remain to be designed. Documentation-only update: no
application code, schema, migrations, or tests changed/run.
Plan commit: `941d091bf18fbe1f84c2c659ea4d77cf3ab05e1b`.

## Shared media behavior when one user's access is revoked — approved

The user approved the shared-archive revocation policy:

- Revoke the affected user's media access immediately.
- Do not delete shared retained media solely because one user's access was revoked when
  other users remain authorized to access it.
- Block the revoked user from using queued jobs, cached references, or previously obtained
  storage identifiers to retrieve or process the media.
- Delete media according to the existing retention/message-deletion lifecycle, or when no
  longer needed by any authorized workflow. Message expiry still triggers deletion of its
  associated media.

This is an approved target policy, not implemented. Exact reference invalidation,
cache/job handling, and deletion coordination remain implementation details.
Documentation-only update: no application code, schema, migrations, or tests changed/run.
Plan commit: `1a12f75a64b9ff661746e8e8643f3ccb49a99335`.

## Source removal and retained media lifecycle — approved

The user approved the source-removal policy:

- Stop new ingestion and media retrieval for the removed source.
- Revoke subscriptions and source access immediately; the grace period is retention only,
  not continued user access.
- Retain remaining archived messages and associated media during the configurable
  last-subscriber/source-archive grace period (14 days by default).
- An authorized resubscription before expiry cancels pending deletion and resumes collection
  under the normal access rules.
- If the grace period expires without an authorized subscription, delete remaining source
  messages and associated retained media.

The rolling per-message retention rule and message-expiry-triggered media deletion continue
to apply independently. This is an approved target policy, not implemented. Documentation-
only update: no application code, schema, migrations, or tests changed/run.
Plan commit: `38d5559f9f178b76b1301f9eeaf504df69cce2ab`.

## Media deletion failure and recovery — approved

The user approved durable recovery for media deletion failures:

- Persist failed deletions as pending-cleanup work rather than silently dropping them.
- Retry automatically with bounded retries and increasing delays.
- Continue revisiting exhausted items through scheduled cleanup/reconciliation.
- Keep authorization revoked while deletion is pending; pending deletion never permits access.
- Keep sanitized technical failure details in logs, never exposing filesystem paths, storage
  identifiers, or raw low-level errors to users.
- Persist deletion state so restarts do not lose pending cleanup work.

Applies to message expiry, source removal, and retention cleanup. Exact retry counts, delays,
reconciliation cadence, and storage-specific behavior remain implementation details. This is
approved target behavior, not implemented. Documentation-only: no application code, schema,
migrations, or tests changed/run.
Plan commit: `8826aede93e018e50f24c5afe16514d84dc0b491`.

## Message expiry when associated media deletion fails — approved

The user approved keeping message-content retention independent from binary-media deletion
success:

- Delete expired message content on schedule, including readable text, sender details, and
  other user-facing content.
- Retain only a minimal internal cleanup record needed to retry/reconcile media deletion,
  containing an opaque storage reference, deletion state, and retry metadata.
- Keep this record inaccessible through normal message and media APIs.
- Remove it when storage confirms media deletion.
- If deletion remains unsuccessful, retain the minimal record for later reconciliation.

Exact cleanup-record fields and storage-specific confirmation semantics remain implementation
details. This is approved target behavior, not implemented. Documentation-only: no application
code, schema, migrations, or tests changed/run.
Plan commit: `6e3c7b717647d624c9be4f527599659aa58e6757`.

## User-requested account/data deletion — approved

The user approved a bot-accessible request to delete their own Chatbrief data:

- Revoke the user's access and subscriptions immediately.
- Stop collection for sources where they were the last authorized subscriber, following
  existing source lifecycle/retention rules.
- Delete personal preferences, schedules, delivery/recovery records, and other user-specific
  data.
- Revoke linked Telethon sessions and delete stored credentials/session data.
- Preserve shared source messages/media still needed by other authorized subscribers; apply
  existing source lifecycle/retention rules when no authorized subscribers remain.
- Track deletion work through completion, including cleanup failures, without retaining
  unnecessary personal data.
- Explain immediate deletion versus shared data that may remain temporarily under existing
  retention rules.

Exact confirmation/workflow, deletion tracking, and legally required record handling remain
design/implementation details. This is approved target behavior, not implemented.
Documentation-only: no application code, schema, migrations, or tests changed/run.
Plan commit: `8a9aea0ed0b6bf5a18da0e53ddca2f6b9ebbcf73`.

## Account-deletion confirmation flow — approved

The user approved a two-step account-deletion flow:

1. User initiates with `/delete_account`.
2. Bot explains deletion consequences, immediate access loss, linked-session deletion, and
   shared archives that may remain temporarily for other authorized subscribers.
3. Bot requests explicit confirmation using a short-lived confirmation action.
4. Deletion starts only after valid confirmation.
5. Cancellation or confirmation expiry means no deletion.
6. Confirmed deletion is irreversible; a returning user must create a new account.

Confirmation lifetime and interaction mechanics remain implementation details. Approved
target behavior, not implemented. Documentation-only: no application code, schema,
migrations, or tests changed/run.
Plan commit: `4e31698d4c82db28ab884b12564918b57d5db5e7`.

## Personal data export — approved

The approved export target behavior is specified in
[`docs/plans/telegram-hybrid-ingestion.md](../plans/telegram-hybrid-ingestion.md),
under **Personal data export — detailed approved design**. It is not implemented.

- Export the requesting user's preferences, schedules, subscriptions, delivery history,
  and all currently accessible retained messages. Include actual retained media only when
  it is available and the requester remains authorized.
- Produce a primary text ZIP and a separate optional media ZIP. Deliver both directly to
  the requesting user's private Telegram chat with Bot API `sendDocument`; do not use
  public or user-bound web download links.
- Record a fixed request cutoff, enforce source authorization during collection and before
  each delivery, and invalidate the whole export if relevant authorization is revoked
  before delivery.
- The initial configurable availability period is 24 hours. Expiry and revocation trigger
  best-effort deletion of the bot's Telegram message(s); copies already downloaded or
  forwarded cannot be revoked.
- Generate asynchronously with durable export-job storage independent of optional
  message-history storage. The initial deployment is one application instance supporting
  multiple users concurrently, with per-user job isolation and one active export per user.
- Use the approved hybrid relational persistence design: relational job, delivery-attempt,
  and cleanup-task records for lifecycle/ownership/constraints; JSON columns for evolving
  metadata and reports. Keep ZIP binaries out of the database. Exact columns, indexes,
  transaction boundaries, and JSON schemas remain to be designed against source conventions.
- Coordinate worker claims with database-backed leases: atomic claims, renewable expiry, stale-worker fencing, and bounded concurrency across different users. A lease does not make Telegram sends transactional; ambiguous delivery must follow the existing `DeliveryUnknown` recovery policy. Exact lease and concurrency values remain open.
- Schedule queued jobs fairly across users while preserving FIFO order within each user's queue. Keep scheduling durable across restarts and coordinate selection with atomic leased claims; no priority tiers initially.
- Bound simultaneous exports with a configurable, application-wide export concurrency setting (provisional `export.max_concurrent_jobs`), separate from the per-user active-export limit. Use a conservative default chosen after resource/workload inspection; no automatic scaling.
- On shutdown, stop new claims, allow active exports a bounded configurable grace period, then request cooperative stops at safe checkpoints. Preserve durable state and cleanup; ambiguous Telegram sends remain `DeliveryUnknown`, and leases are released only after safe relinquishment or allowed to expire.
- Support `/export request`, `/export status`, `/export cancel`, and confirmed
  `/export retry` for ambiguous document delivery. Retry warns that Telegram may already
  have received the document, retries only the uncertain document, and preserves attempt
  history.
- Primary text delivery determines overall `Ready`; optional media delivery has its own
  outcome. Restart recovery must not blindly resend an ambiguous Telegram delivery.

This is approved target behavior, not implemented functionality. The detailed plan is the
source of truth for archive layout, state transitions, retries, cleanup, and remaining
implementation decisions. Documentation-only: no application code, schema, migrations,
or tests changed/run.

## Include retained media in personal exports — approved (Option B)

The user selected Option B: include actual retained binary media in personal exports when
the user is currently authorized to access it.

- Enforce existing media retention, source authorization, and per-operation access checks;
  shared storage does not grant access.
- Include only media retained and available at export time.
- Apply configurable export size limits.
- Omit expired, unavailable, or over-limit media and clearly report omissions and reasons
  where known.
- Never expose internal storage paths or identifiers.
- Apply the approved user-bound download link and 24-hour initial export expiry.

Exact size limits, archive layout, and reporting format remain implementation details.
Approved target behavior, not implemented. Documentation-only: no application code, schema,
migrations, or tests changed/run.
Plan commit: `829b2f969452e11e14c51ae1d9b42185dbad69bf`.


## Export job metadata retention — approved

The user selected immediate deletion of export-job records after their lifecycle ends:

- Delete the job record and delivery-attempt history when a Ready export's availability expires.
- For Cancelled, Failed, and Invalidated jobs, remove job/attempt records after required cleanup is complete or no longer actionable.
- Preserve only the minimum durable cleanup/reconciliation records while outstanding work still needs them; remove them when completed or no longer actionable.
- Do not retain archives, exported content, media manifests, or delivery history for long-term diagnostics.

This minimizes retained personal metadata at the cost of long-term troubleshooting history. Deletion ordering must preserve crash recovery. Approved target behavior, not implemented. No application code, schema, migrations, or tests changed.


## Export Telegram delivery retry limits — approved

The user approved a conservative bounded retry policy for each primary or optional media document:

- At most three attempts total: one initial attempt and up to two automatic retries.
- Retry only transient failures, with exponential backoff starting at 5 seconds and capped at 30 seconds.
- Respect Telegram's `retry_after` whenever it exceeds the calculated backoff.
- Do not retry permanent failures, including upload-size rejection.
- Exhausted primary attempts produce `Failed`; exhausted media attempts produce media `Failed` without changing a successfully delivered primary export.
- Preserve attempts independently. Ambiguous outcomes remain `DeliveryUnknown` and follow explicit reconciliation; never treat them as ordinary transient failures or blindly resend.

Exact exception classification must be verified against the installed `python-telegram-bot` version. Approved target behavior, not implemented. No application code, schema, migrations, or tests changed.


## Export Telegram message-deletion retry policy — approved

The user approved bounded exponential retries for best-effort deletion of delivered export messages:

- Retry temporary deletion failures starting at 1 minute, with a 1-hour cap.
- Respect Telegram `retry_after` whenever it is longer than the calculated backoff.
- Stop on permanent errors or when Telegram's 48-hour deletion window closes; retries do not extend the user's export-availability expiry.
- Persist cleanup-attempt state and next retry time so cleanup survives restarts. Retain the minimal cleanup record only while deletion remains actionable.

Approved target behavior, not implemented. Documentation-only: no application code, schema, migrations, or tests changed.


## Export progress notifications — approved

The user approved completion-only notifications for personal export jobs:

- Do not send automatic notifications for intermediate states such as `Queued`, `Collecting`, or `Packaging`.
- Users can query state-based progress through `/export status`; do not show percentages.
- Notify only when the primary export becomes `Ready`, `Failed`, or `Invalidated`.

Approved target behavior, not implemented. Documentation-only: no application code, schema, migrations, or tests changed.


## Temporary export archive staging protection — approved

The user approved filesystem-based protection for temporary personal-export archives:

- Use a dedicated private staging directory, with `0700` directory and `0600` file permissions, accessible only to the Chatbrief service account.
- Rely on host-level disk encryption where available; do not introduce application-managed archive-encryption keys initially.
- Delete staged archives and temporary files promptly when delivery or failure/cancellation/invalidation cleanup no longer needs them. Staging is temporary working storage, not authoritative archive storage.
- Inspect deployment filesystem, service-account, and host-encryption capabilities before implementation. Audit logging must not capture exported content or unnecessary personal data.

Approved target behavior, not implemented. Documentation-only: no application code, schema, migrations, or tests changed.


## Export behavior on account deletion — approved

Account deletion cancels queued/running exports, removes staged files, and immediately invalidates Ready exports. Chatbrief best-effort deletes delivered primary and media Telegram messages within Telegram's deletion window using the approved retry policy. Any outstanding deletion task retains only the minimum destination/message metadata needed to finish or safely abandon cleanup without the deleted user record. Once cleanup is complete or no longer actionable, export job, attempt, and cleanup metadata are removed under the approved retention policy. Telegram deletion cannot revoke copies already downloaded or forwarded. This is approved target behavior, not implemented; documentation-only, with no application code, schema, migrations, or tests changed/run.


## Media export filenames — approved (Option A)

Media ZIP entries use only the predefined media category directories. Archive filenames are generated deterministically from export-local `media_ref` values, with only validated safe extensions where known; original filenames are not preserved in ZIP paths or manifest metadata because they may contain personal or third-party information. Validate generated paths and resolve any collision deterministically without overwriting. Exact safe-extension mapping and path validation remain implementation-design details. This is approved target behavior, not implemented; documentation-only, with no application code, schema, migrations, or tests changed/run.


## Oversized primary export — approved (Option A)

If the complete primary text export alone exceeds the configured archive/upload limit, fail the export clearly and explain that it exceeds the supported limit. Never truncate, split, or silently omit primary structured data/messages. Narrowing export scope is not part of the initial design unless separately approved. This is approved target behavior, not implemented; documentation-only, with no application code, schema, migrations, or tests changed/run.


## Export retry classification — approved

Automatically retry only clearly transient failures, such as temporary network/service outages or rate limits. Invalid input/data, authorization/access failures, unsupported media, size rejection, and configuration errors are permanent. Unknown errors fail safely without automatic retry. Keep the separately approved Telegram send and deletion retry policies, including their attempt limits and ambiguous-delivery handling. Verify exact exception mapping and any phase-specific retry limits against installed dependencies and the existing architecture before implementation. Approved target behavior, not implemented; documentation-only; no code, schema, migrations, or tests changed/run.


## Export invalidation on source removal — approved (Option A)

If a source or retained data item included in an export is removed, or retention cleanup deletes it, before all applicable Telegram deliveries complete, invalidate the entire export. Unrelated source removals do not affect the job. Do not deliver a partial archive or continue with a stale snapshot; stop remaining work and delete staging files. If the primary ZIP was already delivered while optional media delivery remains, invalidate the export and best-effort delete already-delivered export documents using the approved Telegram cleanup policy. Keep only minimum actionable cleanup metadata. A fresh request is required and uses a new cutoff/current authorization. This does not change the separately approved post-delivery revocation or account-deletion policies. Exact event hooks and race/cleanup integration remain implementation-design work. Approved target behavior, not implemented; documentation-only; no code, schema, migrations, or tests changed/run.


## Personal export JSON schema version — approved (Option A)

The primary archive's `export.json` includes a top-level integer `schema_version`, starting at `1`. It versions the exported document structure independently of the Chatbrief application release, so consumers can interpret retained exports after application upgrades. Increment it for incompatible format changes; exact fields and compatibility rules remain part of the detailed schema design. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Personal export report schema version — approved (Option A)

The primary archive's `export-report.json` has its own top-level integer `schema_version`, starting at `1`. It is versioned independently from both `export.json` and the Chatbrief application release, and is incremented for incompatible report-format changes. This lets report consumers evolve independently from consumers of the primary data document. Exact report fields and compatibility rules remain part of detailed schema design. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Personal media manifest schema version — approved (Option A)

The optional media archive's `media-manifest.json` has its own top-level integer `schema_version`, starting at `1`. It is versioned independently from `export.json`, `export-report.json`, and the Chatbrief application release, and is incremented for incompatible manifest-format changes. This lets media consumers evolve independently from both primary-archive documents. Exact manifest fields and compatibility rules remain part of detailed schema design. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export archive README format and schema guidance — approved

Both ZIP archives use `README.md` (renamed from `README.txt`). Each README documents archive structure and usage, identifies the JSON document(s) included, explains their top-level `schema_version` fields, and states that each document's version is independent of the other export documents and the Chatbrief application release. Incompatible format changes increment the corresponding document's version. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export JSON schema compatibility — approved (Option A)

Apply this policy independently to `export.json`, `export-report.json`, and `media-manifest.json`: adding an optional field is compatible and does not increment that document's `schema_version`; removing or renaming an existing field, changing its type, or changing its meaning/semantics is incompatible and requires incrementing that document's version. Each document remains independently versioned. Additional edge cases remain for detailed schema design. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.

## Export schema unknown-field handling — approved (Option A)

Consumers of `export.json`, `export-report.json`, and `media-manifest.json` ignore unrecognized fields instead of rejecting a document solely for containing them. This keeps consumers forward-compatible with optional fields added in compatible revisions. It does not relax validation of required fields, malformed values, or other schema constraints. Approved target behavior, not implemented; documentation-only; no code, schema, migrations, or tests changed/run.

## Export schema required-field handling — approved (Option A)

Consumers reject `export.json`, `export-report.json`, or `media-manifest.json` when a field required by that document's schema is missing; they do not silently substitute defaults. Optional fields may be absent according to their documented semantics. Exact required/optional field sets remain open for detailed schema design. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export schema null-value handling — approved (Option A)

For `export.json`, `export-report.json`, and `media-manifest.json`, `null` is accepted only for fields explicitly declared nullable in that document's schema; a null in any other field makes the document invalid. An omitted optional field remains distinct from an explicit null. Exact nullable field sets remain open for detailed schema design. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export schema unsupported-version handling — approved (Option A)

Consumers must reject `export.json`, `export-report.json`, or `media-manifest.json` when the document's `schema_version` is unsupported, and clearly report that version. They must not attempt best-effort parsing with a different schema. Unknown fields are ignored only within a supported version. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export JSON root shape — approved (Option A)

`export.json`, `export-report.json`, and `media-manifest.json` must each have a top-level JSON object containing that document's `schema_version` and document-specific fields. Top-level arrays and scalar JSON values (strings, numbers, booleans, or null) are invalid. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export JSON duplicate-key handling — approved (Option A)

Reject `export.json`, `export-report.json`, or `media-manifest.json` if any JSON object contains duplicate member names, at any nesting level. Do not rely on parser-specific first/last-key behavior. This prevents ambiguous interpretation across parsers. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export `schema_version` value validation — approved (Option A)

In `export.json`, `export-report.json`, and `media-manifest.json`, `schema_version` must be a JSON integer greater than zero. Reject zero, negative values, decimals (including `1.0`), strings (including `"1"`), booleans, null, and all other non-integer or non-positive values. Do not coerce or normalize values. Apply independently to each document. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export missing `schema_version` — approved (Option A)

`export.json`, `export-report.json`, and `media-manifest.json` are invalid if the top-level `schema_version` field is missing. Consumers must not infer a default version, including version `1`. Apply independently to each document. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export JSON object member-name case sensitivity — approved (Option A)

JSON object member names are case-sensitive. Consumers must match documented field names exactly (`schema_version` and `Schema_Version` are different names). A differently cased name does not satisfy a required field; if the exact required spelling is absent, the document is invalid. Apply at every object level in `export.json`, `export-report.json`, and `media-manifest.json`. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export JSON object member-name Unicode handling — approved (Option A)

Compare JSON object member names by their exact Unicode code-point sequences; do not normalize names before comparison. Visually identical names with different code-point sequences are distinct. Apply at every object level in `export.json`, `export-report.json`, and `media-manifest.json`, alongside case-sensitive matching. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


## Export JSON object member-name whitespace handling — approved default (Option A)

Compare JSON object member names exactly; do not trim leading or trailing whitespace. Whitespace is part of the name: `" schema_version"` and `"schema_version "` do not match `schema_version` and cannot satisfy that required field. Apply at every object level in all three export JSON documents, alongside case-sensitive and exact Unicode code-point matching. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.



## Export schema conventions — working defaults

The detailed export schema uses a shared opaque UUID `export_id` and common UTC `created_at` across all included JSON documents; `export.json` also carries the acceptance `cutoff_at`. Timestamps use RFC 3339 UTC strings with trailing `Z`, preserving available sub-second precision. Cross-record relationships use export-local `src-`, `msg-`, and `media-` references; these are not database/Telegram IDs and are not stable across separate exports. Arrays and ZIP entries have documented deterministic ordering, while semantically ordered user configuration remains in its configured order. Exact section fields and shapes remain in detailed design. This is a recommended working default, not implemented.



## Export JSON document shapes — working defaults

Schema v1 requires the common metadata plus all six approved primary sections: `preferences` is an object; `schedules`, `subscriptions`, `delivery_history`, `messages`, and `sources` are arrays. Empty categories use empty objects/arrays rather than omission or null. Source and message records are referenced with export-local references, not internal/Telegram identifiers. The report requires result, counts, omissions, and warnings. The media manifest lists only binaries actually included, with safe archive-relative paths, byte sizes, content types where known, and SHA-256 checksums. Cross-document export IDs/timestamps and all references must validate. Field-level content/privacy and application-model alignment remain open; no implementation.



## Export report and media validation — working defaults

Report results are `complete` or `complete_with_omissions`; omissions use stable reason codes, category, count, and explanation. Counts/byte sizes are non-negative integers. Media manifest entries use SHA-256 of exact archived bytes, exact uncompressed byte size, MIME type only when known, and one of four predefined media categories. ZIP paths are safe relative paths under the corresponding category directory; filenames are generated from export-local `media_ref` values with validated extensions where known, and any collision is resolved deterministically without overwriting. Manifest entries and ZIP binaries must match one-to-one. Authorization revocation/source deletion invalidates the export rather than becoming a normal omission. Implementation details remain unverified/not implemented.



## Exported message privacy — approved

Include authorized retained message content, captions, timestamps, and necessary message metadata, but exclude third-party profile/identity data: sender display names, usernames, Telegram user IDs, profile photos, phone numbers, participant/contact lists, and forwarded/quoted author identity metadata. Do not expose Telegram transport IDs. This excludes profile data, not the authorized message content itself. Approved policy; not implemented.

## Export schema follow-up — message/source/media defaults

The export design now has repository-aligned working recommendations based on inspection of the committed `Message`, Telegram adapter, storage, and configuration models:

- Export authorized message text/captions and source timestamps; exclude author/profile identity, Telegram transport IDs/links, and synthetic author references. Do not invent reply/forward/reaction/edit/service-event fields absent from the retained model.
- Use stable media categories rather than localized labels. Media-only messages must not gain invented user-authored placeholder text; legacy placeholder conversion remains a migration-design item.
- Source records use only a safe configured display label and platform; exclude Telegram IDs, usernames, invite/deep links, internal keys, and session identifiers.
- Preferences are an explicit allowlist of user-owned choices, never a raw config dump. Exclude target Telegram user IDs, credentials, sessions, storage paths, internal class paths, and operational settings.
- Recommended media privacy default: generated deterministic archive filenames based on export-local media refs; omit original filenames from both ZIP paths and manifest metadata.
- Recommended v1 purpose: portable archival/inspection snapshot, not a restore/import or account-migration contract. Future import requires separate design.
- Exact field mapping and legacy-data conversion remain open for Phase 1 migration design. These are documentation recommendations only; no code, tests, or migrations changed/run.

## Export report and media-only message semantics — working defaults

Repository inspection confirmed the current Telethon adapter synthesizes localized display placeholders (for example `[Photo]`) for media-only messages. Recommended v1 behavior:
- Export retained message body/caption as plain text; `text` may be empty for media-only messages. Do not export synthetic display placeholders as authored text.
- Strip a legacy placeholder only when its synthetic origin is reliably known. If provenance is ambiguous, preserve stored text rather than risk deleting genuine authored content.
- Keep an authorized retained media-only message in `export.json` even when its binary is unavailable. The media manifest lists only binaries actually present in the companion ZIP.
- Message source timestamp is optional only if genuinely unavailable; never substitute export creation/collection time.
- Binary media categories are image, video, document, audio. Poll/location/other interactive or service payloads are not media binaries in v1; unsupported eligible payloads are reported as media omissions where applicable.
- Do not use `has_media` as a promise that a binary is included. Message media references resolve only to actual companion archive items; manifest is authoritative.

Report defaults:
- Omission codes: `expired`, `unavailable`, `unsupported`, `size_limit`, `missing_content`, `not_exportable`. `unsafe_filename` is removed because original filenames are never used; unsafe filesystem inputs are never read and are reported as `not_exportable` if otherwise eligible.
- Omission categories: preferences, schedules, subscriptions, delivery_history, messages, media. Aggregate by category/reason with positive count and safe explanation; no private IDs, paths, filenames, or omitted content.
- `complete_with_omissions` only when eligible requested content is actually absent. Empty categories are not omissions; failed/invalidated jobs do not produce a successful report.
- Fixed non-negative included counts: preferences, schedules, subscriptions, delivery_history, messages, sources, media_files, media_bytes; `omitted_media_items` only when known. Counts reflect actual archive contents.
- Warnings are structured `{code,message}`; initial codes: `legacy_media_placeholder_removed`, `media_metadata_incomplete`, `timestamp_unavailable`. Warnings alone do not change result. Messages must not expose source text, identifiers, filenames, paths, traces, or secrets.
- These are recommended schema semantics, not implemented. Legacy placeholder provenance and exact field mapping remain Phase 1 migration-design items. No application code, tests, or migrations changed/run.

## Export preference/source field allowlist — working defaults

- Export only requesting-user-owned, user-meaningful values; do not copy the current single-user/global config wholesale.
- Potential typed preferences: lookback, output language, digest mode, emoji/statistics choices, topic deduplication, and user-owned digest-group definitions, only when stored per user in the future domain model.
- Subscription records may include the requester's source-specific lookback, digest-group assignment, and authored prompt override when these are user-owned. Preserve user-authored prompt text as data.
- Exclude prompt-template paths, composer/filter Python class paths, arbitrary filter dictionaries, executable/plugin code, credentials/API keys, service endpoints, deployment limits/timeouts, global model/runtime config, and storage/database config.
- Export filters only through stable versioned data-only allowlists. Unsupported filter configuration is omitted with `not_exportable`; never serialize arbitrary Python objects or import paths.
- Provider/model choice is included only if Phase 1 establishes it as an explicit user-owned preference rather than operator configuration.
- Source records contain platform enum and safe display label only; no source usernames/IDs/invite links/private URLs/transport IDs. Missing required source linkage is invalid snapshot data, not a dangling or synthetic source ref.
- Exact field keys depend on the future user-scoped model and Phase 1 migration proposal. Documentation-only; no application code, tests, or migrations changed/run.

## Phase 1 export persistence migration proposal — approved for implementation

The existing message store is optional, uses inline `CREATE TABLE IF NOT EXISTS`, and has no versioned migration runner or application-wide user table. Proposed additive migration:
- Required application-state store independent of optional message history; SQLite first, provisional `data/application.db`; leave `data/messages.db` unchanged.
- Minimal versioned migration runner using existing DB dependencies, `schema_migrations(version, applied_at, checksum)`, transactional migrations, checksum drift rejection, SQLite foreign keys enabled per connection.
- `export_jobs`: internal UUID, unique export_id, owner Telegram user ID, constrained job/media states, cutoff/created/updated/delivery/expiry timestamps, lease owner/expiry/generation, next_run_at, opaque staging key, optional validated report/manifest JSON, stable error code.
- `export_delivery_attempts`: job FK, primary/media kind, unique attempt number per kind/job, outcome, timestamps/retry time, restricted Telegram chat/message/file IDs, sanitized error code. Append-only.
- `export_cleanup_tasks`: nullable job FK ON DELETE SET NULL, cleanup type/state, target Telegram IDs or opaque staging key, bounded retries/deadline/error. Survives job/account deletion only while actionable.
- Partial unique index for one blocking job per user (queued/collecting/packaging/ready); indexes for queue, owner, lease, expiry, attempts, cleanup. Short atomic transactions; lease-generation fencing; no transaction across network/archive work.
- Additive only. No edits to legacy messages/delivery JSON/config/sessions and no automatic backfill: old messages lack reliable owner/source/message identity. Any backfill requires a separate proof-based mapping proposal.
- First migration creates only export tables and migration metadata. PostgreSQL support, future shared domain tables, workers/commands/archive/delivery implementation, and legacy backfill remain out of scope.
- This proposal is approved for implementation. Approval does not mean its schema/migrations are already implemented; deliver them in tested, reviewable slices.


## Validation follow-up — 2026-11-02

The developer fast-forwarded the local branch to `377f234` and ran the documented focused checks using the project interpreter (Python 3.15.2). The first run produced:

- Focused pytest: **95 passed, 4 failed**. All four failures were caused by tests writing `async with await database.connect()`. An awaited `aiosqlite.Connection` has already started its worker thread; entering it again as an async context manager attempted to start the thread twice.
- Ruff lint: passed.
- Ruff format check: one formatting issue in `tests/test_application_storage.py`.
- Pyright: 0 errors, 0 warnings, 0 informations.
- Coverage: the focused two-file run reported 16.49%, below the repository-wide 49% threshold. This is not a valid full-suite coverage result; run the full suite after fixing the focused failures.

Correction committed on the branch: `49f2d4d` replaces the invalid connection context usage with a test helper that awaits the configured connection once and closes it in `finally`. The test file was also reformatted. The plan now records the observed validation results. **The correction has not yet been run locally**, so do not proceed to startup integration until the focused tests, formatter, and full suite are rerun successfully. Ruff lint and Pyright passed before this test-only correction; rerun them as part of the verification set.

The pull triggered Graphify's background rebuild. The developer should check that rebuild has finished and inspect `git status --short` before committing any generated graph changes; do not stage Graphify output blindly.


## Application-state database validation — developer-reported results

After syncing through `af0fed4`, the developer reran validation on Python 3.15.2:

- Focused tests with `--no-cov`: **99 passed**.
- Full suite: **602 passed, 7 skipped**.
- Full-suite coverage: **94.73%** (required 49%).
- Ruff lint: passed.
- Pyright: 0 errors, 0 warnings, 0 informations.
- Ruff format check: still reported one line in `tests/test_application_storage.py`.

The remaining formatting line was corrected in commit `14a2681` (single-line SQL execute context). The plan records the successful test results. The format check has **not** yet been rerun after that commit; do not mark Step 1 completely validated until it passes. The source/test logic itself is validated by the reported full suite. Next, sync the formatting correction and run the formatter check (and optionally lint/Pyright again); then proceed to application startup lifecycle integration.

Graphify started its background rebuild after the pull. Verify local rebuild completion and inspect graph changes before staging; no graph freshness claim is made here.
