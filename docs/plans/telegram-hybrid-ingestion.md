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

### 7. Secure linked user sessions

- Treat Telethon session data as account credentials.
- Associate every session with its owning Chatbrief user; never share one user's session with another.
- Encrypt session material at rest and restrict access to the process/components that require it.
- Never log session contents, login codes, passwords, or other authentication secrets.
- Provide disconnect/revocation and session deletion flows.
- Define retention, backup, key management, and recovery behavior before enabling multi-user session storage in production.

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

### Phase 5 — Adapt Telethon as an optional historical integration

- Add an explicit account-linking lifecycle for each Chatbrief user.
- Store each user's Telethon session securely and independently.
- Backfill history from the chats the linked account can access.
- Send backfilled messages through the same normalization, deduplication, and persistence path as Bot API updates.
- Support cancellation, rate limits/flood waits, partial failures, progress, retry/resume, and disconnect/revocation.
- Keep users without linked sessions fully functional through Bot API ingestion.

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
