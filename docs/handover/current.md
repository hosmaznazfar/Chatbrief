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

Media ZIP entries use only the predefined media category directories. Archive filenames are derived from sanitized basenames after discarding source directory components; collisions receive deterministic suffixes and must never overwrite an existing entry. The original source filename remains available in the media manifest but is never used as an archive path. Reject names/paths that remain invalid after normalization. Exact sanitization and suffix rules, path validation, and entry-count limits remain implementation-design details. This is approved target behavior, not implemented; documentation-only, with no application code, schema, migrations, or tests changed/run.


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
