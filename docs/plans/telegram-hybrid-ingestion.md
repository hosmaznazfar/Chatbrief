# Telegram Hybrid Ingestion and Multi-User Support

**Status:** Approved direction; implementation not started  
**Scope:** Future Telegram architecture evolution  
**Existing libraries:** Keep `python-telegram-bot` and Telethon

## Goal

Evolve Chatbrief from its current single-user, Telethon-backed collection flow into a multi-user service with two complementary Telegram ingestion paths:

1. **Central Bot API ingestion (default):** users can use Chatbrief without linking a personal Telegram account or providing a phone number.
2. **Optional user-account integration (historical access):** a user may explicitly link their own Telegram account through the existing Telethon integration to backfill history from chats that account can access.

Both paths must feed one platform-neutral message-processing and persistence pipeline. Digest generation must not depend on which Telegram API collected a message.

This is a target architecture and implementation plan, not a statement that multi-user support or Bot API ingestion already exists.

## Decisions

### 0. Chatbrief user identity and registration

- **Use Telegram identity as the Chatbrief user identity.** A user starts a private conversation with the central bot, and their Telegram user ID identifies their Chatbrief user record.
- Do not introduce a separate email/password account system for this Telegram-first product.
- Keep optional Telethon account linking separate from Chatbrief identity. Linking a personal Telegram account is an explicit capability for historical backfill, not a registration requirement and not a replacement for the bot identity used for Chatbrief authorization and delivery.
- Scope subscriptions, source permissions, digest preferences, schedules, and delivery records to the Chatbrief user identified by that Telegram user ID.
- Treat the Telegram user ID as an external identity key; do not use usernames or display names as stable identifiers.


### 0.1 Optional Telethon account-linking constraints

- A linked Telethon account must be the **same Telegram account** as the Chatbrief identity established through the central bot. During linking, compare the authenticated Telethon user's numeric Telegram ID with the Chatbrief user's Telegram ID; reject a mismatch.
- A Chatbrief user may have at most one active Telethon account/session link.
- Replacing an existing link requires explicit user confirmation. The replacement flow must revoke and invalidate the previous session so it cannot continue to be used.
- Linking and unlinking Telethon must not create, replace, or delete the user's Chatbrief identity, subscriptions, or digest preferences.
- This is an approved target policy; implementation details for safely rotating session credentials and handling failed re-link attempts remain part of the session-lifecycle design.

### 1. Retain the current libraries and implementation

- Keep `python-telegram-bot` for Bot API commands, updates, and message delivery.
- Keep Telethon for optional user-account authentication and historical retrieval.
- Do not introduce aiogram, Hydrogram, TDLib, GoyGram, or another Telegram client as part of this work.
- Preserve the current working Telegram behavior while introducing the new ingestion path incrementally.

### 2. Separate ingestion from digest generation

- Both Bot API updates and Telethon history results must be normalized into the same internal, platform-neutral `Message` representation.
- Introduce or refine an ingestion boundary only after inspecting the existing collector, message model, storage interfaces, and tests.
- Keep Telegram SDK types, update objects, MTProto entities, authentication, session management, and Telegram-specific identifiers inside the Telegram adapter/integration boundary.
- Digest collection, filtering, grouping, summarization, formatting, and delivery must not depend on Bot API or Telethon objects.

### 3. Central Bot API is the default

- The central bot is the default way to use Chatbrief.
- A user must be able to register, configure sources, and receive digests without linking a personal account.
- The bot must be added to a group/supergroup with sufficient message visibility (privacy mode disabled or bot administrator, as appropriate) and to channels it should ingest.
- Bot API ingestion is forward-looking. Telegram does not provide bots with arbitrary historical chat retrieval.
- Chatbrief must continuously receive and persist updates itself. Telegram's pending Bot API updates are retained for a limited period (currently up to 24 hours); this is not a substitute for Chatbrief's own durable storage.
- A requested lookback window can be served from Chatbrief's own stored messages only when collection coverage is known to be complete.

### 4. Telethon is optional and user-owned

- Linking a Telegram user account is explicit opt-in and is not required for normal bot use.
- Each linked account/session belongs to exactly one Chatbrief user.
- A linked account can backfill historical messages only from chats the Telegram account itself can access.
- Telethon history backfill and Bot API live ingestion must converge on the same normalization and persistence path.
- Bot-token MTProto authorization is not a substitute for user authorization for history methods restricted to users.

### 5. Separate chat access, subscriptions, and digest organization

These are distinct concepts and must not be conflated:

- **Chat/source access:** whether the central bot or a linked user account can read a Telegram chat.
- **User subscription:** whether a Chatbrief user has selected that chat as one of their digest sources.
- **Digest preferences:** lookback, filters, prompt overrides, delivery settings, and other per-user choices.
- **Digest grouping:** how a user's subscribed sources are grouped in their digest (including the existing channel/topic grouping concepts).

A Telegram group/supergroup is a source chat. A `DigestGroupConfig` grouping is an application-level digest organization feature; they are not the same thing.

### 6. Deduplicate across ingestion paths

- Define a stable source-message identity using the Telegram chat identifier and Telegram message identifier (with platform/source namespace where needed).
- Enforce uniqueness in persistent storage so overlapping Bot API ingestion and Telethon backfill cannot create duplicate messages.
- Handle edits, deletions, media metadata, and messages without text deliberately; do not assume message text is a safe identity.
- Confirm the correct key and update semantics against the existing schema before implementing migrations.

### 8. Shared archive and source-access policy

- Use one shared, deduplicated archive of source messages rather than a separate message copy for every subscriber.
- Per-user subscriptions reference source chats; subscription state and source-access authorization are separate.
- Enforce strict source-level access checks on every message/history/digest query. Shared storage must never imply shared user access.
- Public channels and public groups may be subscribed to by any Chatbrief user without channel/group administrator approval, provided the central bot can access the source.
- Private channels and groups require established access through the central bot or a linked Telegram user account.
- Any current Telegram administrator may register a private channel or private group and initially control its Chatbrief sharing policy; the creator does not have exclusive authority. For private groups, registration is initiated inside the group and the initiating user must be verified as a current administrator. For private channels, use the separate administrator-verification flow. Other Chatbrief users require explicit authorization before subscribing.
- If the registering administrator later loses administrator status or leaves a private channel/group, their Chatbrief management authority is revoked. Any current administrator of that Telegram chat may claim management of the existing Chatbrief source. The claim must verify current administrator status, preventing a source from becoming permanently orphaned.
- When management is transferred through this takeover process for either a private channel or private group, preserve existing user sharing authorizations and subscriptions. The new administrator inherits management authority and may subsequently change sharing policy; takeover alone must not silently revoke existing users.
- If Chatbrief cannot verify any current Telegram administrator for a private source, freeze its Chatbrief management operations: do not allow sharing-policy changes, new sharing authorizations, or new subscriptions until a current administrator is verified again. Preserve existing authorized subscriptions and archived messages; do not revoke existing users solely because management is temporarily unavailable. Continue or stop live ingestion according to the separate central-bot-access and authorized-subscription rules. Once an administrator is verified, restore management without requiring existing users to subscribe again.
- A user's membership/access through their own linked Telegram account does not automatically grant the central bot access, or grant other Chatbrief users access.
- Keep public-source discovery/availability distinct from the question of whether a particular ingestion path can technically read the source.

### 9. Subscription-driven ingestion and configurable retention

- Start collecting a source when its first authorized Chatbrief user subscribes.
- Continue collection while at least one authorized subscription remains active.
- Stop collection when the last authorized subscription ends or loses access.
- When the last authorized subscription ends, retain already archived messages for a configurable grace period; the default is **14 days**.
- If an authorized subscription is restored before the grace period expires, cancel the pending expiry and resume collection.
- If the grace period expires with no authorized subscribers, delete the archived messages for that source, subject to any separately approved legal/operational retention requirements.
- Revoking a user's authorization takes effect immediately. The grace period governs archive retention, not continued access for the revoked user.
- Make the grace period configurable; do not hardcode 14 days into deletion logic.

### 9.1 Rolling per-source message retention

- Bound the shared message archive with a rolling retention window for each source. The default is **14 days**: retain messages collected within the most recent 14 days and automatically delete older message records, even while the source has active authorized subscribers.
- Make this message-retention duration configurable; do not hardcode 14 days into cleanup logic.
- Apply the rolling message-retention rule independently of subscription state. Active subscriptions do not cause an unlimited accumulation of raw source messages.
- Keep the existing last-subscriber grace period as a separate source-lifecycle rule. When the last authorized subscription ends, start the configurable source-archive grace period (14 days by default). If an authorized user resubscribes before it expires, cancel full-source archive deletion; if it expires without an authorized subscriber, delete the source's remaining archived messages and source archive data.
- The source grace period does not extend the age of individual messages: messages older than the rolling message-retention window are still deleted. Resubscription cannot recover messages already expired under that policy.
- Digest lookback and AI summarization inputs must respect the retained archive window. Do not accumulate an unbounded raw-message corpus merely to provide context to the AI.
- Track collection coverage for the retained window separately from message rows, so pruning old messages does not make incomplete recent collection appear complete.

This is an approved retention direction; exact cleanup scheduling, transactional deletion behavior, indexes, and coverage bookkeeping belong in the schema and implementation design.

### 10. Telethon scope: explicit historical backfill only

- Telethon is optional and is used only for historical backfill explicitly requested by a user.
- The central Bot API is the only continuous ingestion path in this architecture.
- Do not use Telethon as a continuous collector or automatic fallback when the central bot cannot access a source.
- A source readable only through a user's linked account may be backfilled, but it will not receive ongoing collection under this policy.
- **Central-bot access is required for an active subscription.** If the bot cannot access a source, Chatbrief may offer a one-time historical backfill and summary through the linked account, but must not activate an ongoing subscription. The user must arrange central-bot access before an active, continuously updated subscription can begin.
- Users without linked accounts remain fully supported for sources the central bot can access; their historical lookback is limited to the shared archive's available messages.

### 7. Secure linked user sessions

- Treat Telethon session data as account credentials.
- Associate every session with its owning Chatbrief user; never share one user's session with another.
- Encrypt session material at rest and restrict access to the process/components that require it.
- Never log session contents, login codes, passwords, or other authentication secrets.
- Provide disconnect/revocation and session deletion flows.
- Define retention, backup, key management, and recovery behavior before enabling multi-user session storage in production.

### 10.1 Message edits, deletions, and overlapping backfill

- When Telegram reports an edit to an already archived source message, update the existing archived record to the latest known message content and metadata. Do not create a second logical message for the edit.
- When Telegram explicitly reports that a source message was deleted, reflect that deletion in the archive (for example, by marking the record deleted or removing it according to the eventual retention/audit design).
- Do not claim complete deletion detection: only apply deletion handling when the relevant Telegram integration actually receives reliable deletion information. Absence of a deletion event must not be interpreted as proof that a message still exists.
- When Telethon historical backfill overlaps with a message already collected through the Bot API, reconcile both observations against the same stable source-message identity and update the existing record rather than inserting a duplicate.
- The exact soft-delete versus hard-delete representation, edit history/audit requirements, and conflict-resolution rules remain schema/design decisions for the migration proposal.

This is an approved behavior direction; implementation and persistence semantics are not yet designed or implemented.

### 11. Central bot access loss and restoration

- If the central bot loses access to a private source, mark it inaccessible and suspend live Bot API ingestion.
- Preserve existing subscriptions and sharing authorizations in a suspended state; do not cancel subscriptions merely because bot access was lost.
- Preserve the shared archive. Access loss does not itself trigger archive deletion or change the configurable retention policy.
- Notify affected subscribers that live updates are paused because the central bot cannot access the source. Notification delivery and retry behavior remain implementation-design details.
- Do not use Telethon as a fallback collector. Telethon remains limited to explicit, user-requested historical backfill.
- When central-bot access is restored, automatically resume live ingestion if at least one authorized subscription remains and the source's management/sharing rules permit it.
- Restoring bot access does not bypass a frozen management state: if no current administrator can be verified, the existing no-admin policy still blocks new subscriptions and sharing-policy changes.
- If all subscriptions end while ingestion is suspended, apply the normal last-subscription lifecycle and configurable archive-retention grace period.

This is an approved target policy, not an implemented capability.

## Digest scheduling, incremental windows, and one-time requests

The user has approved the following product behavior direction. These are target requirements,
not implemented capabilities.

### Scheduled digest configuration

- Users configure digest schedules independently for their own digest groups (each group may contain one or more subscribed source chats).
- Require each user to configure a valid IANA timezone explicitly before allowing them to create a digest schedule. Provide a bot command such as `/timezone Europe/Berlin`; users may change the configured timezone manually at any time. Do not silently default scheduled digests to UTC when the user has not configured a timezone.
- If `/timezone` is invoked without an argument, show the user's currently configured timezone and explain how to set or change it. If the supplied timezone is not a valid IANA identifier, return a clear error with valid examples and leave the existing timezone unchanged.
- Support user-selected schedules such as every hour, daily, and a selected weekday/time (for example, Saturdays at 07:00). The scheduling model must be flexible enough for these patterns rather than assuming one global daily job.
- Define the hourly schedule as an elapsed-time interval: execute every 60 elapsed minutes, rather than once at each local clock-hour boundary. Daylight-saving transitions do not skip or duplicate an hourly execution; the user's configured timezone affects how execution timestamps are displayed, not the 60-minute interval.
- Store a timezone per Chatbrief user, configured explicitly by that user through bot commands. Use an IANA timezone identifier so daylight-saving and other timezone-rule changes can be handled by timezone-aware scheduling rather than a fixed UTC offset.
- Never infer or automatically change a user's configured timezone from IP address, VPN exit location, device location, Telegram metadata, or other environmental signals. The configured timezone remains in effect until the user explicitly changes it.
- Normalize and persist message timestamps and internal event timestamps in UTC. Use UTC as the universal storage/comparison basis; do not store source timestamps as user-local wall-clock values.
- Interpret that user's digest-group schedules in their explicitly configured timezone, and convert UTC timestamps into that timezone when presenting dates/times in digests or other user-facing output.
- When a user explicitly changes their timezone, apply the new timezone to all future schedule calculations and user-facing time conversions. If a digest execution is already in progress when the timezone changes, allow that execution to complete under the schedule occurrence that triggered it; apply the new timezone only to future occurrences. Do not cancel or restart an in-progress digest. Keep stored UTC timestamps unchanged; do not shift historical records. Recalculate future schedule occurrences using the new timezone. Preserve each existing schedule's configured local wall-clock time when changing timezone: for example, a daily 07:00 schedule remains at 07:00 in the newly configured timezone. Recalculate future occurrences under the new timezone; do not alter past digest boundaries, completed executions, or stored UTC timestamps.
- Resolve daylight-saving transitions in the user's configured timezone consistently: if a scheduled local time does not exist during the spring-forward transition, run once at the next valid local time; if it occurs twice during the fall-back transition, run once at the first occurrence. This avoids missing a scheduled digest or delivering it twice.
- For each scheduled digest group, summarize only the messages collected since that group's previous successful digest boundary, up to the current run. Do not repeatedly feed the entire retained 14-day archive to the AI on every scheduled run.
- Advance the group's processed/digest boundary only after the complete digest has been delivered successfully. If delivery fails, keep the previous successful boundary unchanged.
- Persist or otherwise retain the already-generated digest for delivery retries; retry delivery without regenerating the AI summary.
- Track delivery progress within a multi-message digest. If delivery fails partway through, resume from the first message not yet confirmed delivered rather than resending the entire digest. Advance the digest group's successful boundary only after every message in the digest has been delivered. Account for ambiguous send outcomes, where the platform may have accepted a message even though the client did not receive confirmation, and minimize duplicate delivery where possible.
- Use a configurable retry policy. Initial defaults: up to 3 retries after the initial attempt (4 total attempts), with delays of 1 minute, 5 minutes, and 15 minutes between retries.
- Make the retry count and delay policy configurable so they can be changed later without redesigning the scheduler.
- If all configured attempts fail, move the delivery into a pending-recovery state and notify the user. Preserve the already-generated digest and confirmed delivery progress; keep the successful digest boundary unchanged.
- After retry exhaustion, do not retry continuously. Automatically resume delivery when the system detects that the relevant delivery service is operational again, continuing from the first message not yet confirmed delivered.
- Retain the pending-recovery record until delivery completes or an explicitly designed user/admin resolution path handles it. Never silently discard it or skip its undelivered interval.
- Make retries idempotent where possible. Telegram does not provide a universal idempotency key for sending messages, so an ambiguous network failure may still occasionally cause duplicate delivery; implementation must account for and minimize this risk.
- The source archive's rolling retention remains independently bounded (14 days by default). If a scheduled digest has not run successfully for longer than the retained window, older messages may already have expired; the product must not imply they are still available.

### Raw collection mode (no AI summarization)

- Offer a per-digest-group mode that does not invoke an AI model.
- In this mode, collect messages from the group's sources during the configured interval and deliver them together in the user's configured destination chat.
- **Use copied messages, not Telegram forwards.** The delivered copies must not carry Telegram's forwarded-message header.
- Add source attribution separately to each copied message or message batch, and include a source link where available. The copy presentation must make the originating source clear even though the native forwarded-message attribution is absent.
- Copy supported media along with text messages, preserving the original media where Telegram's Bot API permits it. This includes photos, videos, documents, audio, and voice messages; verify the exact supported copy behavior and limits during implementation design.
- Add source attribution separately to copied media messages as well as text messages, with a source link where available.
- If an individual message or media item cannot be copied, skip that item and notify the user that the raw result is incomplete. Never silently present a partial result as complete.
- Exact attribution formatting, batching, per-media failure reporting, and Bot API capability/limit handling remain implementation-design details.

### One-time digest requests

- A user can request a one-time digest for a selected digest group, independently of its recurring schedule.
- The one-time request supports an AI-summarized mode and the raw collection mode.
- The requested time range can start at the present/current point or reach back to a user-selected point no more than 14 days in the past. The upper bound is the configured rolling archive-retention window; do not promise older data.
- One-time requests must respect source authorization, available collection coverage, and the same per-source access boundaries as scheduled digests.
- A one-time request must not silently change the recurring schedule or the group's next scheduled digest boundary.

## Important constraints and risks

- Bot API cannot backfill messages from before the bot had access or recover updates after Telegram's pending-update retention window expires.
- A linked user account cannot read chats that account has not joined or otherwise cannot access.
- A single central bot does not by itself make the application multi-tenant. The current single-user authorization and global source configuration must be replaced with explicit user ownership and authorization.
- Existing storage is currently optional and append-oriented. Its current schema and collection-coverage behavior must be reviewed before it can support reliable continuous ingestion, deduplication, and multi-user queries.
- The existing storage-completeness ADR states that stored rows alone do not prove collection completeness and that live collection remains authoritative. Any cache-first or stored-history digest behavior must preserve that guarantee by tracking successful collection coverage.
- Bot access to group messages depends on Telegram group privacy settings and bot membership/administration.
- This plan does not promise identical access to all messages across Bot API and user-account MTProto. Telegram permissions and method restrictions remain authoritative.

## Implementation sequence

Implement incrementally. Do not rewrite the existing Telegram source, sender, or bot as a single step.

### Phase 1 — Inspect current storage and digest lifecycle

- Trace the complete path from Telegram collection through normalization, filtering, storage, digest generation, and delivery.
- Inspect the current `Message` model, `MessageSource` / `MessageSender` protocols, collector/orchestration, storage backends and schema, configuration loader, command authorization, scheduler, and tests.
- Verify how message links, chat identifiers, message identifiers, media, timestamps, and sender metadata are currently represented.
- Identify the existing single-user assumptions, especially `target_user_id`, global `config.channels`, and user-specific sender tracking.
- Review ADR 0002 (storage completeness) and any storage/digest plans before proposing schema changes.
- Produce a concrete migration proposal with data model, ownership boundaries, compatibility impact, migration/backfill strategy, and acceptance criteria.
- Do not change application code or database schema during this inspection phase.

### Phase 1 findings — verified 2026-10-31

Phase 1 source inspection is complete. These findings describe the implementation at the
inspection revision; they are not implementation changes.

#### Current lifecycle and boundaries

- `Message` currently contains `text`, `sender`, `timestamp`, `link`,
  `channel_name`, `has_media`, and `media_type`. It has no platform namespace,
  stable chat/source ID, or message ID.
- `MessageSource` exposes connection lifecycle, all-channel and single-channel history
  fetching, and channel URL lookup. `TelegramMessageSource` implements it with one
  hard-coded Telethon session at `sessions/user.session`.
- `TelegramBot` is a python-telegram-bot command adapter. It registers command handlers
  and polls for updates, but it does not currently ingest ordinary group/channel messages.
- `PlatformBuilder` creates one Telegram source and one Telegram sender. `main.py`
  composes one source, sender, scheduler, command service, bot, and optional MCP server.
- The current digest flow fetches live messages, applies configured filters, optionally
  writes the filtered messages to storage, then summarizes and sends them. Storage writes
  are best-effort and are not a continuous update-ingestion mechanism.
- The scheduled digest is one global daily job. Manual commands and the sender both enforce
  the single configured `target_user_id`. Digest delivery tracking is stored in a local
  JSON file keyed by recipient ID, not in the message database.

#### Current persistence behavior

- SQLite and PostgreSQL use the same logical `messages` table fields: generated row ID,
  `channel_name`, `sender`, `text`, `timestamp`, `link`, `has_media`,
  `media_type`, and `collected_at`.
- Neither schema stores platform, Telegram chat ID, Telegram message ID, Chatbrief user
  ownership, ingestion path, edit state, or collection coverage.
- There is no uniqueness constraint for source messages. The SQLite tests explicitly verify
  that saving the same message twice inserts two rows.
- The read API filters by channel name and time only; it has no tenant/source identity filter.
- ADR 0002 remains authoritative: stored rows do not establish complete collection coverage,
  so digest/MCP collection continues to fetch from the live source.

#### Configuration and identity constraints

- `Config.channels` is a single global source list; `ChannelConfig.group` is digest
  organization, not Telegram group membership.
- `Settings.target_user_id` is mandatory in the configuration loader and is the only
  authorized recipient.
- The configuration loader currently requires `TELEGRAM_API_ID`,
  `TELEGRAM_API_HASH`, and `TELEGRAM_BOT_TOKEN` together. This conflicts with the
  target requirement that Bot API-only users must not need personal-account integration
  credentials. API ID/hash should become conditional on enabling/linking Telethon, while the
  bot token remains required for the central bot.
- The Telethon source requires an existing authorized local session file. There is no
  per-user session-linking, encryption, revocation, or ownership lifecycle.

#### Migration proposal — design direction, not an approved schema

The smallest coherent target appears to require these separate concepts:

1. **Chat/source identity:** a platform-qualified stable chat ID, with display metadata and
   access state. Telegram's human-readable name must not be the primary key.
2. **Message identity:** a platform-qualified chat ID plus platform message ID, with a
   uniqueness constraint. The normalized message content should remain platform-neutral;
   Telegram-specific IDs and update metadata belong at the ingestion/persistence boundary.
3. **Ingestion/access provenance:** record whether the central bot or a particular linked
   account can currently read a chat, and represent ingestion progress/coverage independently
   from the messages themselves.
4. **User subscriptions:** associate a Chatbrief user with a source chat, separately from
   the fact that the bot or a linked account can access that chat.
5. **Per-user digest preferences:** store lookback, filters, prompt overrides, grouping,
   schedule, and delivery target per user rather than on one global `Config`.
6. **Linked Telegram accounts:** store each user's Telethon session independently, encrypted
   at rest, with explicit connect/revoke/delete lifecycle.
7. **Delivery tracking:** move sent-message tracking from the local JSON file to durable,
   recipient-scoped records before supporting multiple recipients.

**Decision: use a shared, deduplicated message archive.** Per-user subscriptions reference
source chats rather than owning separate copies of each message. This avoids duplicate
message storage and supports cross-path deduplication. Enforce subscription- and
source-authorization checks on every read so shared storage never grants implicit access.
A user's ability to access a source, and the central bot's ability to ingest it, do not
automatically authorize other Chatbrief users to read it.

No final database schema, migration, or code change is approved by this inspection.

#### Phase 1 verification scope

Inspected the current message model, platform protocols and builder, Telegram source/bot/sender,
configuration models and loader, storage implementations, digest collector/service/builder,
scheduler, composition root, storage/digest/scheduler tests, ADR 0002, and the current
hybrid plan. No application tests or quality checks were run; this phase was source inspection
only. Local uncommitted Graphify rebuild output is not visible to this GitHub inspection.

### Phase 2 — Establish a normalized ingestion boundary

- Keep the current Telethon implementation operational.
- Define the smallest useful contract for delivering normalized messages and source metadata into the application/storage layer.
- Keep the contract platform-neutral; avoid exposing Telegram SDK objects or adding speculative generic abstractions.
- Add tests proving that existing Telethon collection still produces the same digest-relevant message data.
- Decide how ingestion outcomes and collection coverage are represented before enabling storage-backed lookback.

### Phase 3 — Add central Bot API ingestion

- Use the existing `python-telegram-bot` dependency and application lifecycle where appropriate.
- Receive new group/supergroup and channel messages with the required Telegram permissions.
- Normalize and persist incoming updates through the shared ingestion boundary.
- Handle retries, reconnects, duplicate updates, update ordering, service messages, media, edits, and graceful shutdown.
- Ensure ingestion is continuous and durable; do not rely on Telegram's pending-update queue as the message archive.
- Add integration tests for group/channel access assumptions and update normalization.

### Phase 4 — Introduce multi-user ownership and subscriptions

- Replace single-user-only authorization with explicit Chatbrief user identity and authorization.
- Replace the single global source list with user-owned subscriptions/preferences while keeping shared Telegram chat access distinct from each user's subscription.
- Define how a chat becomes available to users, who can authorize it, and how access is removed when the bot or linked account loses access.
- Scope digest queries, filters, grouping, scheduling, and delivery tracking to the correct user.
- Review the existing command throttling and sender tracking for tenant isolation.
- Design and test database constraints that prevent cross-user data exposure.

### Phase 5 — Adapt Telethon as an optional historical-backfill integration

- Add an explicit account-linking lifecycle for each Chatbrief user.
- Store each user's Telethon session securely and independently.
- Use Telethon only when a user explicitly requests historical backfill for a source accessible to that linked account.
- Send backfilled messages through the same normalization, deduplication, and persistence path as Bot API updates.
- Do not run Telethon as a continuous or fallback ingestion worker. Ongoing collection belongs to the central Bot API path.
- Require central-bot access before activating an ongoing subscription. If a source is accessible only through the linked Telethon account, offer a one-time historical backfill/summary only; do not activate an ongoing subscription. If central-bot access is later established, the user may then activate an ongoing subscription.
- Support cancellation, rate limits/flood waits, partial failures, progress, retry/resume, and disconnect/revocation.
- Keep users without linked sessions fully functional through Bot API ingestion; their historical summaries are limited to messages already available in the Chatbrief archive.

### Phase 6 — Reliability, security, and acceptance

- Enforce stable message uniqueness across Bot API and Telethon.
- Track collection coverage so missing/incomplete ingestion is never mistaken for an empty chat.
- Test restart recovery, duplicate delivery, overlapping backfill/live ingestion, partial failures, and authorization boundaries.
- Test that one user's sources, filters, linked sessions, digests, and delivery records cannot leak to another user.
- Add operational monitoring for ingestion lag, last successful update, backfill progress, and collection failures.
- Update configuration, deployment documentation, privacy/security documentation, and user-facing commands.
- Run migrations only after the schema design and migration plan are reviewed and explicitly approved.

## Acceptance criteria

- A user can use Chatbrief through the central bot without a personal Telegram session or phone-number login.
- The central bot can continuously ingest messages from groups/supergroups and channels where it has the necessary access.
- Digests use the common normalized message pipeline regardless of ingestion path.
- A user can optionally link their own Telegram account for historical backfill.
- Backfill is limited to chats accessible to that linked account.
- Bot API and Telethon overlap does not create duplicate stored messages.
- Collection completeness is represented explicitly; incomplete ingestion is not reported as a complete empty result.
- Source access, user subscriptions, digest preferences, and digest grouping are independent concepts.
- User data and Telegram sessions are isolated by Chatbrief user ownership.
- Existing Telegram digest behavior remains covered by regression tests throughout the migration.

## Non-goals

- Replacing `python-telegram-bot` or Telethon.
- Rewriting the digest/summarization pipeline around Telegram SDK types.
- Making Telethon mandatory for registration or ordinary use.
- Using a central bot token to bypass Telegram's user-only history restrictions.
- Assuming Bot API can retrieve arbitrary historical messages.
- Implementing Bale as part of this Telegram architecture work.
- Designing the final database schema before Phase 1 inspection.

## Documentation and decision tracking

- Update this plan as each phase is implemented; distinguish completed, deferred, and not-started work.
- Add or revise ADRs for material decisions such as message identity/deduplication, tenant ownership, session storage, and collection-coverage semantics.
- Update `CHATGPT_CONTEXT.md`, `AI_README.md`, and the current handover when the target architecture or implementation status materially changes.
- Keep README feature claims aligned with what is actually implemented; planned multi-user and hybrid capabilities must not be described as currently available.


## Manual pending-digest recovery command — approved

Provide a user-facing `/retry` command so a user can request recovery of a digest delivery that remains pending after automatic retries are exhausted.

- The command may retry only pending-recovery deliveries owned by the requesting Chatbrief user.
- Resume the existing persisted digest from the first message not confirmed delivered. Preserve confirmed delivery progress and existing duplicate-prevention safeguards.
- Do not generate a new AI summary, create a new digest interval, or advance the successful digest boundary until the complete existing digest is delivered.
- When a delivery enters pending recovery, notify the affected user and include clear, actionable instructions for invoking `/retry`.
- Include `/retry` in the bot's help/command guidance so users can discover it before they need it.
- If the user has exactly one pending delivery, `/retry` retries it directly.
- If the user has multiple pending deliveries, `/retry` lists them with stable, user-facing identifiers; the user selects one with `/retry <id>`.
- Pending-recovery notifications must include the delivery identifier and the exact `/retry <id>` command when the user needs to select among multiple pending deliveries. When only one delivery is pending, the notification may simply instruct the user to run `/retry`. The identifier must be sufficient to select the intended pending delivery and must not expose internal database identifiers or another user's data.

This is an approved target behavior, not an implemented capability. No application code, database schema, or migrations have changed.


## Delivery status and diagnostics command — approved

Keep ordinary user recovery separate from operational diagnostics.

- Provide `/status <id>` as an **administrator-only** command for inspecting a pending or failed delivery.
- Do not publish or advertise `/status` in ordinary user-facing bot help, command menus, or recovery notifications.
- Enforce administrator authorization server-side on every invocation using an explicitly configured allowlist of Telegram administrator user IDs. Hiding the command is not an authorization control.
- Unauthorized users must not receive delivery details or learn whether another user's delivery identifier exists.
- The administrator-facing response may show sanitized operational details, such as delivery state, attempt count, last-attempt time, and a safe high-level failure category. Do not expose raw exception text, stack traces, credentials, tokens, or sensitive API response data through the bot.
- Keep full technical errors and stack traces in application terminal logs, subject to normal secret-redaction rules. The bot is not a remote terminal/log viewer.
- Ordinary users continue to use `/retry` only for their own pending deliveries; user-facing notifications and retry listings remain concise and non-technical.

This is an approved target behavior, not an implemented capability. No application code, database schema, or migrations have changed.


### Media-aware AI summarization — future capability; design open

- Preserve media type metadata on normalized messages and distinguish a message that merely has media metadata from one whose actual media content is available for AI analysis.
- Keep three distinct per-digest-group modes: **raw collection (no AI)**, **AI text-only summarization**, and **AI text-plus-images summarization**.
- Raw collection remains the previously approved no-AI mode: copy supported messages/media with separate source attribution; it is not an AI summarization scope.
- For AI modes, text-only is the default. Text-plus-images may let a vision-capable model describe relevant available images alongside message text.
- The initial AI media-analysis capability should support images only (photos and image documents). Video, audio, and voice analysis are explicitly deferred; they may be added as future capabilities.
- Design a clear, extensible media-processing boundary so additional processors (for example, video/key-frame analysis, audio transcription/summarization, and voice-message processing) can be added independently without restructuring core ingestion, message persistence, or digest orchestration.
- Keep media-type identification and availability separate from media-specific processing. Unsupported or unavailable media must not break text summarization or supported image analysis; the digest should handle such items according to an explicit, user-visible omission/fallback policy.
- Image analysis is a future capability, not part of the currently approved raw-copy behavior and not an implemented feature.
- Do not assume that recording an image/media tag means the image bytes are retained or available to a model. Media download, storage, retention, access control, size/format limits, model capability, cost, and failure behavior remain open design decisions.
- The existing rolling per-source message retention policy does not yet define binary media retention. Decide whether and how media files are retained separately before implementation.

### Media-file storage and retention — approved

- Store retained binary media files separately from message records. Message metadata and the media-file lifecycle must remain distinct.
- Apply a configurable media-retention period, initially **14 days**.
- Delete a retained media file when its associated message expires. Media must not outlive the message record's retention lifecycle.
- Do not download or persist media that is not needed for an enabled/selected product operation. Retrieve or retain media only when required for raw copying, supported AI media analysis, or another explicitly supported workflow; avoid unnecessary collection.
- Enforce the same source-authorization rules for media access as for the associated message. Shared media storage must not grant access to users who are not authorized to read that source.
- Keep media retention independently configurable from message retention, while ensuring message expiry triggers deletion of its associated media. The initial 14-day media default aligns with the current rolling message-retention default.
- This policy defines the target behavior; exact storage backend, temporary-file handling, cleanup scheduling, deletion guarantees, and access-control implementation remain schema/implementation-design details.

### AI image-analysis failures and omissions — approved

- In the **AI text + images** mode, an image that cannot be analyzed must not fail the entire digest. Continue using the available message text and any images that were analyzed successfully.
- Skip an image when it cannot be retrieved, its format/content is unsupported by the selected AI provider, it exceeds the provider's input limits (for example, file-size, resolution, or other documented constraints), or image analysis otherwise fails.
- Include a concise user-visible note in the digest whenever one or more images were skipped. Explain the reason when it is known, distinguishing provider format/support limitations and provider input-limit violations from retrieval or processing failures. Do not imply that all images were analyzed.
- Keep sensitive or low-level technical failure details, including raw provider errors, in application logs with normal secret-redaction protections; do not expose raw exceptions or provider response payloads in the digest.
- Provider-specific supported formats, limits, and error classification must be verified for the selected model/provider during implementation. Do not invent or assume universal limits.
  
This is an approved target behavior, not an implemented capability. No application code, schema, migrations, or tests have changed.

### Chatbrief-side image limits before provider upload — approved

Before uploading images for AI analysis, Chatbrief must enforce configurable local
processing limits to control resource use, processing time, and provider costs:

- Configure a maximum image file size.
- Configure maximum image dimensions/resolution.
- Configure a maximum number of images included in one digest's AI image-analysis input.
- Support optional compression or resizing when an image exceeds a preferred processing
  size but remains within the applicable hard limits and can be transformed safely.
- Skip an image that exceeds a hard Chatbrief-side limit and report the omission in the
  digest, following the approved image-analysis failure/omission policy.

These Chatbrief-side limits are distinct from provider/model-specific input constraints.
Check the selected provider/model's documented requirements separately; do not assume
that passing local limits guarantees provider acceptance. Exact numeric defaults, supported
transformation formats/quality settings, and configuration interfaces remain to be designed
and verified during implementation.

This is an approved target behavior, not an implemented capability. No application code,
schema, migrations, or tests have changed.

#### Initial Chatbrief-side image-limit defaults — approved

The initial configurable defaults for AI image processing are:

- Maximum original image file size: **20 MB**.
- Maximum image width or height: **4096 pixels**.
- Maximum images included in one digest's AI image-analysis input: **10**.
- Preferred maximum dimension after resizing: **2048 pixels**.
- JPEG compression quality when compression is needed: **85%**.

Treat these as initial application defaults, not universal provider limits or immutable
constraints. Keep them configurable. Provider/model-specific constraints remain separate
and take precedence whenever they are stricter. Apply resizing/compression only when the
image can be transformed safely; skip and report images that exceed hard limits or cannot
be processed safely.

This is an approved target configuration, not an implemented capability. No application
code, schema, migrations, or tests have changed.


#### Image selection when the per-digest limit is reached — approved

When more eligible images are available than the configured maximum number of images for one digest's AI image-analysis input:

- Select the **most recent images** by their associated message timestamps, up to the configured limit.
- After selection, preserve chronological order among the selected images when supplying them to the AI model.
- Continue including all eligible message text; reaching the image limit must not exclude message text.
- Include a concise note in the digest stating how many images were omitted because the per-digest image limit was reached.
- Apply this selection deterministically. If implementation encounters equal timestamps, define a stable tie-breaker using source-message identity so repeated processing selects the same images.

This policy works with the approved initial maximum of 10 images while keeping the limit configurable. It is an approved target behavior, not implemented. Documentation-only update: no application code, schema, migrations, or tests changed/run.


#### Initial image formats for AI analysis — approved

The initial AI image-analysis capability must support these image formats:

- JPEG/JPG
- PNG
- WebP

Defer GIF support from the initial implementation. Animated-image frame selection/extraction is a separate concern and can be designed if GIF support is added later. Other formats may be considered in future extensions.

Local format support does not guarantee acceptance by a selected AI provider/model. Check provider/model-specific supported formats independently and apply the previously approved graceful omission behavior when a provider cannot accept an image.

This is an approved target scope, not implemented. Documentation-only update: no application code, schema, migrations, or tests changed/run.


#### Safe image transformations for AI analysis — approved

When preparing an image for AI analysis (including resizing to the preferred dimensions or compression):

- Preserve the original image format whenever the required transformation can be performed safely without changing formats.
- Convert PNG or WebP to JPEG only when necessary to satisfy the selected provider/model's requirements or to reduce image size.
- Preserve transparency when the source format supports it. Do not silently flatten transparent content onto an arbitrary background; if conversion to a format without transparency is necessary, use an explicitly defined safe handling policy or skip the conversion and report the omission.
- Never modify the retained original media file. Perform transformations on a separate processing copy, such as a temporary working file, and apply the approved temporary-file cleanup/security requirements.

These rules supplement the approved size, dimension, format, and provider-limit policies. This is an approved target behavior, not implemented. Documentation-only update: no application code, schema, migrations, or tests changed/run.


#### Temporary processing files — approved

Temporary files created while retrieving, resizing, or compressing media for an operation
must follow this policy:

- Use a dedicated temporary directory, separate from permanent/retained media storage.
- Generate unpredictable temporary filenames. Never use Telegram-provided filenames
  directly as filesystem paths.
- Apply restrictive filesystem permissions so other local users cannot read temporary
  originals or transformed copies.
- Delete temporary downloaded originals and transformed copies after processing, on both
  successful and failed processing paths.
- Design cleanup to account for interrupted processing and application restarts, not only
  normal completion (for example, by identifying and removing abandoned temporary files
  safely).

This is an approved target policy, not an implemented capability. Exact directory
placement, permission details, cleanup scheduling/recovery, and implementation mechanics
remain to be specified during implementation. No application code, schema, migrations,
or tests have changed.


#### Recovery cleanup for abandoned temporary files — approved

Temporary-file cleanup must cover both normal operation and interrupted processing:

- Run a cleanup pass at application startup to identify and remove abandoned files in the
  dedicated temporary directory.
- Also run periodic cleanup while the application is running so abandoned files do not
  accumulate until the next restart.
- Protect files belonging to active processing operations. Cleanup must distinguish active
  work from abandoned files using a reliable mechanism (for example, operation ownership/
  leases together with an age threshold); it must not delete a file merely because an
  operation is taking longer than expected.
- Keep cleanup scoped to Chatbrief's dedicated temporary directory and avoid touching
  unrelated files.

This is an approved target behavior, not implemented. The exact active-operation tracking,
age threshold, cleanup cadence, and failure handling remain implementation details. No
application code, schema, migrations, or tests have changed.

#### Media access authorization at every operation — approved

Enforce the same source-authorization rules for media as for its associated message at
every media operation, not only when a user initially requests a digest:

- Check the requesting user's authorization before downloading or retrieving media.
- Check authorization before reading, processing, or sending retained media.
- Do not expose permanent or temporary media paths or internal storage identifiers to users.
- Ensure that one user's authorization or access context cannot be reused to retrieve another
  user's media.
- Recheck authorization when executing delayed or queued media jobs. A job created while a
  user was authorized must not continue to access or deliver media if that authorization has
  since been revoked.

This is an approved target security policy, not an implemented capability. Exact enforcement
boundaries, authorization representation, and implementation mechanics remain to be specified
during implementation. Documentation-only update: no application code, schema, migrations,
or tests have changed or been run.

#### Revocation when media is shared by multiple authorized users — approved

When one Chatbrief user's authorization to a source is revoked, but the retained media
belongs to a shared source archive that other users remain authorized to access:

- Revoke the affected user's media access immediately.
- Do not delete the shared media solely because one user's authorization was revoked;
  preserve it for other currently authorized users and workflows.
- Ensure the revoked user cannot retrieve or use the media through previously created
  jobs, cached references, or previously obtained storage identifiers.
- Delete retained media according to the existing message/media retention and deletion
  lifecycle, or when it is no longer needed by any authorized workflow. Message expiry
  continues to trigger deletion of its associated media.

This is an approved target policy, not an implemented capability. Exact reference
invalidation, cache/job handling, and deletion coordination remain implementation details.
Documentation-only update: no application code, schema, migrations, or tests have changed
or been run.

#### Source removal and retained media lifecycle — approved

When a source is removed from Chatbrief:

- Stop new ingestion and new media retrieval for that source.
- Revoke subscriptions and source access immediately; the retention grace period does not
  preserve user access.
- Retain the source's remaining archived messages and associated retained media during the
  configurable last-subscriber/source-archive grace period (14 days by default), consistent
  with the approved source-retention policy.
- If an authorized user subscribes again before the grace period expires, cancel pending
  archive deletion and resume collection subject to the normal access rules.
- If the grace period expires without an authorized subscription, delete the source's
  remaining archived messages and associated retained media.

This keeps source lifecycle, message retention, and media retention consistent. The existing
rolling message-retention rule and message-expiry-triggered media deletion continue to apply
independently. This is an approved target policy, not implemented. Exact deletion scheduling,
coordination, and recovery behavior remain implementation details. Documentation-only
update: no application code, schema, migrations, or tests have changed or been run.

#### Media deletion failure and recovery — approved

Media deletion failures must not be silently discarded:

- Record failed deletions as durable pending-cleanup work.
- Retry automatically using bounded retries with increasing delays.
- After automatic retries are exhausted, continue reconciliation through a scheduled cleanup
  process so pending deletions are revisited.
- Pending deletion never grants access: authorization revocation and access checks remain
  effective while deletion is pending.
- Log sanitized technical failure details; do not expose filesystem paths, storage identifiers,
  or raw low-level errors to users.
- Track deletion state so application restarts do not lose pending cleanup work.

This policy applies to deletion triggered by message expiry, source removal, and retention
cleanup. Exact retry counts, delays, reconciliation cadence, and storage-specific deletion
semantics remain implementation details. This is approved target behavior, not implemented.
Documentation-only update: no application code, schema, migrations, or tests changed or run.

#### Message expiry when associated media deletion fails — approved

A media-storage deletion failure must not extend message-content retention:

- Delete expired message content on schedule according to the applicable retention policy.
  This includes readable text, sender details, and other user-facing message content.
- Preserve only a minimal internal cleanup record needed to retry and reconcile binary-media
  deletion, including an opaque storage reference, deletion state, and retry metadata.
- Keep this cleanup record inaccessible through normal message and media APIs.
- Remove the cleanup record after storage confirms that the associated media has been deleted.
- If deletion remains unsuccessful, retain the minimal record for later reconciliation rather
  than losing track of potentially orphaned media.

This separates message-content retention from reliable media-cleanup tracking. Exact cleanup
record fields and storage-specific confirmation semantics remain implementation details.
This is approved target behavior, not implemented. Documentation-only update: no application
code, schema, migrations, or tests changed or run.

#### User-requested account/data deletion — approved

Users must be able to request deletion of their own Chatbrief data through the bot:

- Revoke the requesting user's access and subscriptions immediately.
- Stop collection for any source for which that user was the last authorized subscriber,
  applying the existing source lifecycle and retention rules.
- Delete the user's personal preferences, schedules, delivery/recovery records, and other
  user-specific data.
- Revoke any linked Telethon session and delete its stored credentials/session data.
- Do not delete shared source messages or media still needed by other authorized subscribers.
  Shared archives follow the existing source lifecycle and retention rules when no authorized
  subscribers remain.
- Track deletion work until it completes, including failed cleanup, without retaining
  unnecessary personal data.
- Clearly explain what is deleted immediately and what shared data may remain temporarily
  under the existing retention policy.

This provides user control without destroying shared archives still legitimately needed by
other authorized subscribers. Exact request confirmation, workflow, deletion tracking, and
handling of legally required records remain design/implementation details. This is approved
target behavior, not implemented. Documentation-only update: no application code, schema,
migrations, or tests changed or run.

#### Account-deletion confirmation flow — approved

Account deletion requires an explicit two-step confirmation:

1. The user initiates the request with `/delete_account`.
2. The bot explains the consequences, including deletion of personal data and linked sessions,
   immediate loss of access, and the possibility that shared archives remain temporarily for
   other authorized subscribers.
3. The bot requests explicit confirmation through a short-lived confirmation action.
4. Deletion begins only after valid confirmation.
5. If the user cancels or the confirmation expires, no deletion takes place.
6. Once confirmed, deletion is irreversible. A returning user must create a new account.

The confirmation lifetime and exact interaction mechanics remain implementation details.
This is approved target behavior, not implemented. Documentation-only update: no application
code, schema, migrations, or tests changed or run.

#### Personal data export — approved

Users must be able to request an export of their own Chatbrief data through the bot:

- Include the user's preferences, schedules, subscriptions, delivery history, and messages
  they are currently authorized to access.
- Include shared-source messages only while the requesting user is currently authorized to
  access the corresponding sources.
- Exclude other users' personal information, credentials, Telethon sessions, and internal
  storage paths or identifiers.
- Deliver the completed ZIP directly to the requesting user's private Telegram chat as a
  document, rather than providing a web download link or using long-lived local archive storage.
- Keep the generated ZIP in local staging only while it is being built and uploaded; remove
  the local archive after Telegram confirms successful delivery.
- Treat the Telegram document message as the user-facing export. Its initial configurable
  availability period defaults to 24 hours; then attempt to delete the bot's message.
- Exporting must not change subscriptions, retention, or account state.

Authorization must be enforced when selecting content and immediately before Telegram
 delivery. Telegram cannot enforce Chatbrief authorization after delivery or revoke a copy
already downloaded by the user. Exact staging, delivery, expiry, and cleanup mechanics remain
design/implementation details. This is approved target behavior, not implemented.
Documentation-only update: no application code, schema, migrations, or tests changed or run.

#### Include retained media in personal exports — approved (Option B)

Personal data exports include actual retained binary media files when the requesting user is
currently authorized to access them:

- Apply the existing media retention, source authorization, and per-operation media-access
  checks. Shared storage does not grant access.
- Include only media that remains retained and available at export time.
- Apply configurable export size limits.
- Omit media that has expired, is unavailable, or exceeds export limits, and clearly report
  the omission and its reason where known.
- Do not expose internal storage paths or identifiers in the archive or report.
- The completed archive is delivered to the requesting user's private Telegram chat and
  the bot's delivery message is subject to the 24-hour initial expiry policy.

Exact size limits remain open; the approved archive layout and reporting requirements are specified in the detailed design below. This is
approved target behavior, not implemented. Documentation-only update: no application code,
schema, migrations, or tests changed or run.

#### Personal data export — detailed approved design

This section consolidates the approved export decisions in this existing implementation plan.
It supersedes any earlier wording that described these now-approved choices as undecided.
It is a target specification, not evidence that export functionality is implemented.

##### Scope and authorization

Include the requesting user's preferences, schedules, subscriptions, delivery history,
and **all currently accessible retained messages**, not only messages previously included
in digests. Include actual retained binary media when the requester is authorized.

- Include shared-source messages and media only while the requesting user is authorized
  to access the corresponding source. Shared storage alone does not grant access.
- Exclude other users' personal information, credentials (including Telethon sessions and
  authentication secrets), internal filesystem paths/storage identifiers, and content the
  requester is not authorized to access.
- Apply existing retention rules and per-operation media access checks. Export does not
  extend retention, delete source media, or modify subscriptions, messages, or account state.
- Check authorization when selecting content and before every archive download.

##### Archive structure

Create two separate ZIP archives and deliver them automatically in sequence when each
is eligible and within Telegram's upload limit. The text archive is primary; the media
archive is a separate optional companion.

Primary archive, `chatbrief-export.zip`:

```text
chatbrief-export.zip
├── README.txt
├── export.json
└── export-report.json
```

- `export.json`: structured personal data and authorized retained messages.
- `export-report.json`: export timestamp, completeness information, and media omissions
  with reasons where known.
- `README.txt`: archive structure and interpretation guidance.

Optional companion archive, `chatbrief-media.zip`:

```text
chatbrief-media.zip
├── README.txt
├── media-manifest.json
└── media/
    ├── images/
    ├── videos/
    ├── documents/
    └── audio/
```

- `media/`: actual retained media binaries that pass authorization, availability, and
  retention checks and fit within the media archive's size limit.
- `media-manifest.json`: included media metadata and omissions/reasons where known, without
  exposing internal storage paths or identifiers.
- `README.txt`: media archive structure and interpretation guidance.

Use safe archive-relative filenames in both archives; never expose internal storage paths
or identifiers. Text data must not depend on the media archive being present.

##### Size limits and omissions

Use separate configurable size limits for the primary text archive and optional media
archive, each respecting Telegram's standard cloud Bot API `sendDocument` upload limit
(currently 50 MB).

- Always build and send the primary text archive first. It contains all eligible structured
  personal data and retained messages; it does not contain binary media.
- Build the companion media archive separately and automatically send it after the text
  archive when eligible media is available and the completed ZIP fits its configured limit.
- If media is expired, unavailable, unauthorized, or cannot fit, omit it from the media ZIP
  and record omissions/reasons in the primary export report and media manifest where known.
  If no media can be included, do not send an empty media archive.
- Never let media size or availability prevent delivery of a valid text archive. Text is the
  primary export; media is an optional companion.
- Never silently truncate JSON or produce a corrupt ZIP. If structured data and messages
  alone exceed the primary archive limit, fail clearly rather than silently dropping or
  truncating personal data.

Exact size limits and the policy for structured data/messages exceeding the primary limit
remain to be confirmed after inspecting realistic data volumes and deployment constraints.

##### Snapshot and authorization revocation

Record a fixed cutoff timestamp when the export request is accepted. Personal data and
message scope is bounded by that timestamp; later-arriving messages are not included.
Media availability is checked during generation and unavailable media is reported as omitted.

If authorization for any source whose content has been selected for the export is revoked
before Telegram delivery, including while generation is running, invalidate the **entire**
export:

- Do not send the ZIP to Telegram.
- Schedule deletion of the local archive and temporary files.
- Notify the user that the export is unavailable because authorization changed.
- Require a new export under current authorization.

Recheck authorization immediately before sending. After Telegram accepts the document,
Chatbrief cannot enforce later authorization changes on a copy the user can already access;
if authorization is revoked before the 24-hour expiry, attempt to delete the bot's Telegram
message, subject to Telegram's deletion limits. Do not imply that this can revoke a copy
already downloaded by the user.

##### Generation workflow and concurrency

Generate exports asynchronously:

1. The user requests an export through the bot.
2. Chatbrief creates and queues the job, records the cutoff timestamp, and acknowledges
   the request without waiting for generation.
3. A background worker collects eligible structured data, messages, and media.
4. Build the primary text ZIP and its completeness report; independently build the optional
   media ZIP when eligible media is available.
5. Immediately before each primary delivery attempt, recheck authorization and send the
   primary text ZIP to the requesting user's private Telegram chat with `sendDocument`.
   Retry transient Telegram/network failures a bounded number of times. Do not retry
   permanent failures; if the retry policy is exhausted, mark the export `Failed` and
   clean up local artifacts. The exact attempt count, backoff, and handling of
   Telegram-provided retry delays remain to be specified during implementation design.
6. After Telegram confirms the primary delivery, persist its chat/message identifiers and
   delivery timestamp. This establishes the overall export's `Ready` state.
7. If a media ZIP exists and fits its limit, recheck authorization and send it as a separate
   document, then persist its delivery identifiers and timestamp. Record media delivery as
   a separate outcome (`Sent`, `Omitted`, `Failed`, or `DeliveryUnknown`) without changing
   the successful primary export's `Ready` state. If Telegram may have accepted the media
   document but Chatbrief cannot durably record its message identifier, do not blindly
   resend it. Delete the local staged media ZIP and temporary files after preserving
   durable attempt metadata; do not retain the archive while waiting for reconciliation.
   Reconcile the outcome where possible and show unresolved uncertainty in `/export status`.
   An explicit user action is required to request a fresh media delivery when the outcome
   cannot be established; regenerate the media archive under current authorization and
   explain that this may produce a duplicate.
8. Remove local ZIPs and temporary files after their respective Telegram deliveries are
   confirmed, or after the corresponding failure/omission cleanup is complete. A media
   upload failure does not fail the text export and does not require the user to regenerate
   the primary archive; show the media outcome in `/export status`.
9. The user can check status or cancel an eligible job.

**Optional media upload retries:** Retry transient Telegram/network failures for the
media companion a small, bounded number of times. Do not retry permanent failures, such as
Telegram rejecting the file because it exceeds the upload-size limit. Exhausting the retry
policy leaves the primary export `Ready` and records the media outcome as `Failed`; it must
not trigger regeneration or retransmission of the primary text archive. The exact attempt
count, backoff, and handling of Telegram-provided retry delays remain to be specified during
implementation design.

Allow at most one active export per user. The concurrency restriction covers both
background generation and the ready-for-download period:

- `Queued`, `Collecting`, and `Packaging` exports are active and block another request.
- A `Ready` export remains active and blocks another request until its delivered Telegram
  document messages reach their 24-hour expiry or are revoked (for example, by cancellation
  or authorization invalidation).
- `Cancelled`, `Failed`, `Invalidated`, and `Expired` exports do not block a new request.

A user may therefore have only one export whose Telegram delivery is within its availability
period. This prevents multiple concurrently available export messages from accumulating for
the same user.

##### User-visible states and notifications

Use these user-visible states:

| State | Meaning |
|---|---|
| `Queued` | Waiting for a worker |
| `Collecting` | Gathering personal data and messages |
| `Packaging` | Building the ZIP and adding media |
| `Ready` | Primary text ZIP was delivered; optional media ZIP was also delivered when eligible and within limits |
| `Cancelled` | User cancelled the export |
| `Failed` | Generation failed |
| `Invalidated` | Authorization changed and the archive is unavailable |
| `Expired` | Download period ended |

Notify the user only when the primary export becomes `Ready`, fails, or is invalidated. A
failure or omission of the optional media delivery does not change the overall export state
or generate a separate terminal export notification. Show the media outcome in `/export
status`; do not send notifications for intermediate state transitions. Internal cleanup and
media-delivery details need not be exposed as top-level export states.

##### Telegram delivery, expiry, and revocation

Deliver the ZIP using the Telegram Bot API `sendDocument` method to the requesting user's
private chat. The user must have an available private bot conversation for delivery.

- Do not create a public URL or download token. The Telegram chat identity is resolved from
the authenticated Chatbrief user; never accept an arbitrary destination chat from a command.
- Persist the Telegram chat ID and separate sent message IDs, returned document `file_id`
  values when available, and delivery/expiry timestamps for the text and media documents as
  job metadata needed for status, cleanup, and recovery.
- Keep each ZIP in local staging only until Telegram confirms successful delivery of that
  document; then remove that archive and its temporary files. Do not treat Telegram's
  `file_id` as a revocable download token.
- The initial configurable availability period defaults to **24 hours** for both delivered
  documents. At expiry, attempt to delete each bot Telegram message and mark the export
  `Expired` when the expiry policy is applied. Retry failed message-deletion attempts where
  possible.
- Telegram's Bot API only permits deleting messages sent less than 48 hours ago. Retry
  temporary deletion failures automatically while deletion remains possible; stop retrying
  once Telegram's 48-hour deletion window has passed or the failure is otherwise permanent.
  Persist deletion/cleanup outcomes and pending retry state durably so application restarts
  do not lose track of outstanding cleanup. A deletion failure must not extend the export's
  user-facing availability period or keep it in `Ready` indefinitely. Treat deletion as
  best-effort, not a guarantee that Telegram will erase the hosted file or all copies.
- Chatbrief cannot revoke a file the user has already downloaded, forwarded, or otherwise
  copied. Do not promise remote deletion of user-held copies.
- Recheck source authorization immediately before delivery. After delivery, a later
  authorization change can trigger a best-effort deletion of the bot message, but cannot
  retroactively prevent access to a copy already obtained.

##### Cancellation and cleanup

Cancellation can stop a queued or in-progress job. If the ZIP has already been delivered,
cancellation requests deletion of the bot's Telegram message and schedules any remaining
local staging cleanup.

- Stop further collection and packaging as soon as practical.
- Schedule deletion of partial archives and temporary files.
- Repeated cancellation is idempotent.
- Repeating cancellation for an already cancelled, expired, invalidated, or failed job
  does not change its state.
- If cancellation and completion/delivery race, make the competing transition atomic so
  only one outcome wins. If delivery has already succeeded, cancellation is best-effort
  Telegram message deletion and cannot revoke a copy already downloaded.
- Cancellation does not alter account data, subscriptions, messages, or retained source media.
- A copy already downloaded by the user cannot be remotely deleted.

Deletion is scheduled, not assumed to have succeeded synchronously.



##### Explicit recovery from ambiguous delivery

Provide `/export retry` for a job whose primary or media document delivery is
`DeliveryUnknown`. Do not make an automatic resend the default: Telegram may already
have accepted the earlier document, so a retry can create a duplicate.

- The command is available only when at least one document delivery for the current job
  is unresolved as `DeliveryUnknown`.
- Before retrying, explain which document has an uncertain outcome and that Telegram may
  already have received it; ask the user to explicitly confirm the retry.
- For an ambiguous primary delivery, regenerate and resend the primary text archive using
  the original request cutoff and current authorization checks. Keep the same export job
  and preserve the earlier attempt and its uncertainty in durable delivery history.
- For an ambiguous media delivery, regenerate and resend only the media archive. Do not
  regenerate or resend the already-confirmed primary text archive.
- Recheck current authorization during regeneration and immediately before delivery, using
  the existing invalidation policy. Do not reuse a staged archive from the ambiguous attempt.
- Persist each retry as a distinct delivery attempt so status and audit history do not erase
  the earlier uncertain result. Resolve the relevant delivery outcome only after the retry
  has a confirmed result; if it is also ambiguous, retain `DeliveryUnknown`.
- Keep the existing job and its original cutoff/expiry semantics; a retry must not silently
  create a new export request or extend an already-established primary delivery expiry.

##### Export-job relational schema direction

Use a **hybrid relational design** for durable export-job persistence:

- `export_jobs` stores the job's identity, owning Chatbrief user, lifecycle state,
  original request cutoff, and lifecycle timestamps/expiry information.
- `export_delivery_attempts` stores each primary-text or media-document delivery attempt,
  its attempt number and outcome, relevant Telegram delivery identifiers, timestamps, and
  retry/reconciliation information. Retries are new rows; never overwrite an earlier
  ambiguous attempt.
- `export_cleanup_tasks` stores durable pending cleanup work, including Telegram message
  deletion and any required local staging cleanup/retry state.
- Keep lifecycle, ownership, relationships, and fields needed for constraints or routine
  queries in relational columns with appropriate keys and indexes.
- Use JSON columns for variable or evolving metadata, archive reports/manifests, and other
  structured payloads that do not need relational querying or integrity constraints.
- Do not store ZIP binaries in the job database. Archives remain in protected temporary
  staging only for the duration required by the approved generation/delivery workflow.
- Keep the persistence behind the previously approved storage interface, independent of
  optional message-history storage, with SQLite as the initial backend and a future
  PostgreSQL implementation possible without changing export business logic.

This approves the logical storage boundary and hybrid modeling approach, not the final
column list, JSON schema, index definitions, foreign-key policy, migration layout, or
transaction boundaries. Those must be finalized against the existing storage conventions
and tested before implementation.

##### Database-backed worker claims and leases

Use **database-backed leases** to coordinate export workers without an external queue:

- A worker claims a queued or recoverable job through an atomic database operation, ensuring
  that only one valid lease holder owns a job at a time.
- Persist the lease owner/worker identity, lease expiry, and a monotonically changing claim
  generation or equivalent fencing value. A stale worker must not commit job transitions or
  delivery-attempt results after its lease has been superseded.
- Workers renew leases while performing long-running collection or packaging work. Exact
  lease duration and renewal cadence remain implementation decisions.
- If a worker exits or crashes without renewing, the lease expires and another worker can
  reclaim the job. Recovery follows the approved restart rules, including partial-artifact
  cleanup, the original request cutoff, and current authorization checks.
- Keep claim, renewal, and state-change transactions short. Never hold a database
  transaction or SQLite write lock during collection, archive generation, or Telegram calls.
- Support bounded concurrent processing of different users' jobs in the initial application instance, controlled by the approved export-specific global concurrency setting. Preserve the per-user active-export rule; choose the conservative default after inspecting deployment resources and realistic export workloads.
- A lease does not make Telegram side effects transactional. If a worker loses its lease
  around a Telegram send, apply the existing ambiguity rules: do not blindly resend an
  attempt whose outcome may be unknown; persist and reconcile it as `DeliveryUnknown`
  where appropriate.
- Keep coordination behind the export persistence boundary for SQLite initially and
  PostgreSQL later. Do not introduce Redis, Celery, or an external queue initially.

This approves the lease-based coordination model, not exact lease duration, heartbeat
interval, concurrency limit, or database implementation details. Finalize those against
the existing application lifecycle, SQLite behavior, and realistic workload.

##### Fair scheduling across users

Use **per-user fair scheduling** for queued export work:

- Preserve FIFO order among a given user's eligible queued jobs.
- Select the next user fairly across users with eligible work, rather than using one global
  FIFO queue that allows a single user's backlog to dominate.
- Keep the scheduler's selection and job claim atomic with respect to competing workers,
  using the approved database-backed claim/lease mechanism.
- A user with an active export remains subject to the existing one-active-export rule;
  fair scheduling does not bypass per-user eligibility or authorization checks.
- Do not introduce user/job priority tiers or configurable priority weights initially.
  The scheduling policy should remain simple and predictable.
- Define the precise fairness mechanism (for example, persisted last-served ordering or a
  monotonically increasing enqueue/dispatch sequence) during implementation after reviewing
  the existing database and concurrency model. It must remain correct across process restarts
  and must not rely solely on in-memory round-robin state.

This approves fair rotation between users and FIFO within each user's queue, not a specific
SQL query or fairness data structure.

##### Configurable worker concurrency

Make the maximum number of simultaneously processed export jobs configurable through an
export-specific application setting, provisionally named `export.max_concurrent_jobs`:

- The setting is a global limit for the running application instance, not a per-user limit.
  The existing one-active-export-per-user rule remains independently enforced.
- Provide a conservative default suitable for the initial deployment. Determine its exact
  value after inspecting deployment memory/CPU constraints and measuring representative
  collection, archive-generation, and upload workloads; do not guess a capacity now.
- Validate the setting as a positive integer and reject invalid configuration at startup
  with a clear configuration error.
- Apply the configured limit to active worker claims/processing, while retaining database
  leases and fair per-user scheduling. Lowering the limit must not invalidate already-running
  leases or interrupt in-flight exports; it should reduce new claims until active work falls
  below the new limit.
- Keep the setting independent of user identity and do not add automatic resource-based
  scaling for the initial implementation.
- Confirm the final setting name, configuration nesting, and integration with existing
  configuration conventions during source inspection.

This approves operator-configurable, globally bounded concurrency, not a numeric default
or a final configuration key until existing configuration conventions and deployment
resources are inspected.

##### Graceful worker shutdown

Use **graceful cooperative shutdown** for the export worker lifecycle:

- On application shutdown, stop claiming new export jobs immediately.
- Allow active jobs a bounded, configurable grace period to finish normally.
- When the grace period is exhausted, request cooperative cancellation at safe checkpoints.
  Collection and packaging should stop promptly where possible and schedule cleanup of
  partial archives and temporary files.
- Do not forcibly abandon an in-flight Telegram send or other external side effect without
  recording/reconciling its outcome. If shutdown or cancellation makes delivery confirmation
  uncertain, preserve the attempt as `DeliveryUnknown` and follow the approved ambiguity
  recovery policy; never blindly resend after restart.
- Ensure workers stop renewing leases when they relinquish a job. Release a lease explicitly
  only when the worker has safely stopped and durable state/artifact cleanup is consistent;
  otherwise allow the lease to expire and let normal recovery take over.
- On restart, apply the existing recovery rules: resume queued work, restart interrupted
  collection/packaging with the original cutoff and current authorization, and preserve
  confirmed delivery/expiry metadata and pending cleanup tasks.
- The grace period is an application shutdown setting, separate from
  `export.max_concurrent_jobs`. Its default and final configuration name must follow
  existing application configuration conventions and deployment shutdown limits.
- Shutdown must remain bounded: after the grace period and safe-stop handling, the
  application may exit with durable state sufficient for recovery. Do not wait indefinitely
  for a slow source or Telegram request.

This approves cooperative shutdown and bounded graceful completion, not a numeric grace
period or exact setting name. Those must be selected after reviewing the deployment
environment, application lifecycle, and cancellation behavior of existing async operations.

##### Export job metadata retention

Use **immediate deletion of export-job records when the export's availability period expires**:

- When a Ready export reaches its configured expiry and the expiry policy is applied, delete its job record and associated delivery-attempt history rather than retaining a separate operational history period.
- For jobs that end without becoming Ready (Cancelled, Failed, or Invalidated), delete their job and attempt records as part of terminal cleanup once required local and Telegram cleanup work has completed or is no longer actionable.
- Do not delete records while they are still needed to resolve an active or ambiguous delivery, enforce the per-user active-export rule, or drive pending cleanup/reconciliation.
- Keep only the minimum durable cleanup-task information required to complete outstanding Telegram-message deletion or local staging cleanup. Remove that task when cleanup completes or becomes permanently non-actionable (including expiry of Telegram's deletion window).
- Do not retain exported message content, archive binaries, media manifests, or unnecessary Telegram delivery identifiers for historical diagnostics. Remove associated cleanup metadata when it is no longer actionable.
- This policy minimizes retained personal metadata. It intentionally gives up long-term export-job troubleshooting and delivery history after the export lifecycle has ended.

The exact transaction ordering and deletion implementation must preserve crash recovery: do not remove the final durable cleanup/reconciliation record before its work is complete or safely abandoned. This is an approved retention policy, not yet implemented.

##### Automatic Telegram delivery retry limits

Use the **conservative bounded retry policy** for primary and optional media document delivery:

- Allow at most **three attempts per document**: one initial attempt and up to two automatic retries.
- Retry only failures classified as transient. Do not retry permanent failures, including Telegram rejection because an archive exceeds the applicable upload-size limit.
- Use exponential backoff between retries, starting at 5 seconds and capped at 30 seconds.
- When Telegram supplies a `retry_after` delay, respect it whenever it is longer than the locally calculated backoff. Do not retry before Telegram's requested delay.
- Exhausting the attempt budget makes primary delivery `Failed`; for optional media, record media delivery as `Failed` without changing an already-`Ready` primary export.
- Preserve each attempt as a distinct durable delivery-attempt record. An outcome that may have succeeded but cannot be confirmed remains `DeliveryUnknown` and must follow the explicit reconciliation/retry policy; it is not treated as an ordinary transient failure and must not be blindly resent.

This approves the attempt count and backoff policy, not the final exception mapping or Telegram error-classification implementation. Those must be verified against the installed `python-telegram-bot` version and tested. Approved target behavior, not implemented.

##### Telegram message deletion retry policy

- Retry temporary Telegram message-deletion failures with bounded exponential backoff, starting at 1 minute and capped at 1 hour.
- If Telegram provides `retry_after` longer than the calculated backoff, schedule the next attempt no earlier than that delay.
- Stop retrying immediately for permanent deletion errors and when the 48-hour Telegram message-deletion window closes. Deletion is best effort; retries must not extend the user's export-availability expiry.
- Persist cleanup-attempt state and the next retry due time in the durable cleanup record so retries survive process restarts. Retain that minimal record only while deletion remains actionable, then remove it under the approved cleanup-metadata retention policy.

##### Temporary export archive staging protection

- Use a dedicated private staging directory for temporary export archives and files.
- Restrict directory permissions to `0700` and staged file permissions to `0600`, accessible only to the Chatbrief service account.
- Rely on host-level disk encryption where available; do not add application-managed archive encryption keys for the initial implementation.
- Delete staged archives and temporary files promptly after confirmed delivery or when generation, packaging, delivery, cancellation, or invalidation cleanup makes them unnecessary. Staging is temporary working storage, never the authoritative archive store.
- Inspect the deployment's filesystem, service account, and host encryption capabilities before implementation. Define audit logging separately without recording exported content or unnecessary personal data.

##### Export behavior on account deletion

- Account deletion cancels any queued or running export and removes its staged archives and temporary files.
- Immediately invalidate any `Ready` export. Best-effort delete its delivered primary and optional media Telegram messages while Telegram's deletion window remains open; use the approved bounded cleanup retry policy.
- Account deletion must not leave an export available to the deleted user. Telegram deletion is best effort and cannot revoke copies already downloaded or forwarded.
- If Telegram deletion remains pending after the account record is removed, retain only the minimum durable cleanup metadata needed to identify the bot-sent destination/messages and complete or safely abandon deletion. The cleanup task must remain actionable without relying on the deleted Chatbrief user record.
- Once cleanup is complete or no longer actionable, remove the export job, delivery-attempt, and cleanup metadata under the approved export metadata-retention policy.

##### Remaining design work before implementation

Resolve these points only after inspecting the existing architecture and deployment constraints:

- Exact archive-size, item-count, generation-duration, and resource limits, respecting the
  Telegram Bot API `sendDocument` upload limit (currently 50 MB for standard cloud Bot API).
- Primary archive oversize policy — approved (Option A): if the complete primary text export alone exceeds the configured archive/upload limit, fail the export clearly and explain that it exceeds the supported limit. Never truncate, split, or silently omit primary structured data/messages. Narrowing export scope is outside the initial design unless approved separately.
Use `/export` with subcommands rather than separate top-level commands:

- `/export request` starts a new export.
- `/export status` shows the current export state and, when ready, confirms primary text
  delivery, the separate media outcome (`Sent`, `Omitted`, `Failed`, or `DeliveryUnknown`), and the expiry time(s)
  of any delivered Telegram messages.
- `/export cancel` cancels generation or revokes a ready archive and schedules its deletion.
- `/export retry` explicitly retries a primary or media document whose delivery is `DeliveryUnknown`, after warning the user that a duplicate may result and obtaining confirmation.

If a request is blocked by an existing active export, explain its current state and, for a
ready export, when its Telegram message is scheduled to expire. Exact argument parsing and bot-framework
handler structure must follow the existing command conventions after source inspection.
- Show state-based progress only, using the existing user-visible states (`Queued`, `Collecting`, `Packaging`, and `Ready`). Do not display numeric percentages because total work cannot be estimated reliably in advance, particularly with variable message and media availability. Users can query the current state with `/export status`. Do not send automatic notifications for intermediate states; notify only when the primary export becomes `Ready`, `Failed`, or `Invalidated`.
- **Export-job persistence is independent of optional message-history storage.** Export
  requests must remain available when the existing message-storage feature is disabled;
  do not store export jobs exclusively in that optional message store.
- Use a dedicated durable job-storage boundary for export lifecycle records. SQLite is the
  recommended default implementation. Keep this persistence independent of message-history
  storage configuration and lifecycle.
- Keep export orchestration and business logic behind a storage interface so a PostgreSQL
  implementation can be added later without changing export behavior. Do not introduce
  PostgreSQL-specific assumptions into the export workflow.
- Run export workers within the existing application lifecycle and coordinate claims with the approved database-backed lease model. Support bounded concurrency across different users; do not add Redis, Celery, or another external queue initially.
- The initial deployment target is one running application instance, **not one user**.
  It must support multiple Chatbrief users concurrently. Export jobs, status, cancellation,
  download tokens, and authorization must be isolated by Chatbrief user identity. The
  one-active-export rule applies independently per user; one user's export must never
  globally block another user's export.
- Do not assume a single-user process model in schemas, job ownership, authorization,
  command handling, or worker coordination. Keep the design extensible to multiple
  application instances/workers later, but do not require distributed execution initially.
- **Single-instance, multi-user deployment and restart recovery.** The initial deployment
  uses one Chatbrief application instance with in-process workers, database-backed leases,
  and bounded concurrency, while supporting multiple users concurrently. Per-user export
  limits and ownership remain isolated.
- On application startup, leave durable `Queued` jobs queued for processing. Recover
  interrupted `Collecting` and `Packaging` jobs by cleaning up their partial attempt
  artifacts and safely restarting the export from the beginning, using the original
  request cutoff and current authorization checks.
- Preserve `Ready` jobs, their original 24-hour expiry, and Telegram delivery identifiers
  across restarts. The local ZIP should already have been deleted after confirmed delivery.
  Resume/retry scheduled Telegram message deletion after expiry or invalidation; never extend
  the original expiry on restart.
- If Telegram may have accepted a document but Chatbrief crashed before durably recording
  the returned message identifier, persist/recover the attempt as `DeliveryUnknown`. Do not
  blindly resend the document, and do not mark the export `Ready` without confirmed delivery
  metadata. Reconcile the outcome where possible using available Telegram/application
  evidence. Delete the local staged ZIP and temporary files after preserving durable
  delivery-attempt metadata; do not retain sensitive archives while waiting for
  reconciliation. Keep the unresolved job visible in status and block another export
  request while reconciliation is pending. If delivery cannot be established, the user
  may explicitly request a fresh export; regenerate it using the original cutoff where
  still valid and current authorization, and explain that this may produce a duplicate
  Telegram document. That explicit action resolves the per-user block. Do not silently
  convert an ambiguous attempt into success or failure.
- Design queue claiming, worker leases, atomic state transitions, and duplicate-worker
  prevention consistently with the initial single-instance deployment while keeping
  boundaries extensible to multiple instances/workers later.
- Complete the atomic state-transition matrix and authorization race handling through
  finalization. Define durable cleanup retries and reconciliation after crashes/restarts.
- Exact export JSON/report schema, schema version, message fields, and media metadata; exact relational columns, keys, indexes, JSON payload boundaries, and transaction constraints for the approved hybrid job schema.
- **Media archive filenames — approved (Option A):** Store files only under the predefined media category directories (`media/images/`, `media/videos/`, `media/documents/`, and `media/audio/`). Derive each archive filename from a sanitized basename, discarding all source directory components. Resolve collisions deterministically with a suffix and never overwrite an existing entry. Preserve the original source filename in the media manifest for reference, but never use it as an archive path. Reject a filename/path that remains invalid after normalization. Exact sanitization rules, collision suffix format, archive path validation, and entry-count limits must be defined during implementation design after inspecting the existing media/storage boundaries.
- Interactions with source removal, retention cleanup, and shutdown.
- **Export failure classification — approved (Option A):** Automatically retry only failures positively identified as transient, such as temporary network/service unavailability and rate limiting, using the separately approved bounded retry policy for the affected operation. Treat invalid input/data, authorization or access failures, unsupported media, archive/upload size rejection, and configuration errors as permanent; do not retry them automatically. Unknown or unclassified errors fail safely without automatic retry rather than being assumed transient. Preserve the existing separate policies for Telegram document delivery and Telegram message-deletion cleanup; do not let a generation retry bypass their attempt limits or `DeliveryUnknown` handling. Exact exception-to-category mapping and any phase-specific retry limits/backoff must be verified against the installed dependencies and existing architecture before implementation.

Do not introduce new abstractions, schema, or application changes before inspecting the
existing storage, authorization, worker/scheduler, bot, cleanup, and test boundaries.
Implementation must proceed in small reviewable stages with tests and this plan updated
alongside each stage. This documentation change does not alter application code, schema,
migrations, or tests.

