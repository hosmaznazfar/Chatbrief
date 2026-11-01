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
- Support user-selected schedules such as every hour, daily, and a selected weekday/time (for example, Saturdays at 07:00). The scheduling model must be flexible enough for these patterns rather than assuming one global daily job.
- Store a timezone per Chatbrief user, configured explicitly by that user through bot commands. Use an IANA timezone identifier so daylight-saving and other timezone-rule changes can be handled by timezone-aware scheduling rather than a fixed UTC offset.
- Never infer or automatically change a user's configured timezone from IP address, VPN exit location, device location, Telegram metadata, or other environmental signals. The configured timezone remains in effect until the user explicitly changes it.
- Normalize and persist message timestamps and internal event timestamps in UTC. Use UTC as the universal storage/comparison basis; do not store source timestamps as user-local wall-clock values.
- Interpret that user's digest-group schedules in their explicitly configured timezone, and convert UTC timestamps into that timezone when presenting dates/times in digests or other user-facing output.
- When a user explicitly changes their timezone, apply the new timezone to all future schedule calculations and user-facing time conversions. Keep stored UTC timestamps unchanged; do not shift historical records. Recalculate future schedule occurrences using the new timezone.
- Resolve daylight-saving transitions in the user's configured timezone consistently: if a scheduled local time does not exist during the spring-forward transition, run once at the next valid local time; if it occurs twice during the fall-back transition, run once at the first occurrence. This avoids missing a scheduled digest or delivering it twice.
- For each scheduled digest group, summarize only the messages collected since that group's previous successful digest boundary, up to the current run. Do not repeatedly feed the entire retained 14-day archive to the AI on every scheduled run.
- Advance the group's processed/digest boundary only after successful completion/delivery, with retry behavior designed so failures do not silently skip messages. Exact transaction/idempotency behavior remains part of implementation design.
- The source archive's rolling retention remains independently bounded (14 days by default). If a scheduled digest has not run successfully for longer than the retained window, older messages may already have expired; the product must not imply they are still available.

### Raw collection mode (no AI summarization)

- Offer a per-digest-group mode that does not invoke an AI model.
- In this mode, collect messages from the group's sources during the configured interval and deliver them together in the user's configured destination chat.
- **Use copied messages, not Telegram forwards.** The delivered copies must not carry Telegram's forwarded-message header.
- Add source attribution separately to each copied message or message batch, and include a source link where available. The copy presentation must make the originating source clear even though the native forwarded-message attribution is absent.
- Exact attribution formatting, batching, media handling, and behavior for content that cannot be copied remain implementation-design details to verify against the Bot API's capabilities and limits.

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
