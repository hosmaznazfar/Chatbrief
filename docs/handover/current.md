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

**Next:** continue resolving the remaining architecture/design questions and review the
Phase 1 migration proposal. Do not begin Phase 2 implementation until the design decisions
and migration proposal are approved. Before local work, synchronize the branch carefully
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
