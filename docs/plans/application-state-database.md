# Application-state database and export persistence foundation

**Status:** Steps 1–2 and Steps 3a–3e implemented and developer-validated; Step 4a worker orchestration implemented and developer-validated. Production collection is deferred until the user-scoped source/subscription/message data layer and authorization-aware snapshot query exist.  
**Approved design:** Phase 1 export-persistence migration proposal in telegram-hybrid-ingestion.md

## Scope

Establish a required application-state SQLite database independently from the optional legacy message-history store. The initial slices add the database configuration, versioned migration runner, initial export-persistence schema, and application startup integration. Export-job, delivery-attempt, cleanup-task, worker-lease, fair-claim scheduling, and the initial lease-aware worker orchestration service are implemented as separate slices. Application startup wiring, real phase implementations, commands, archive generation, and Telegram delivery remain separate work. In particular, a production collection handler must not read the legacy message-history store: existing rows lack reliable ownership and stable source/message identity, and automatic backfill is prohibited.

## Step 1 — database foundation

- Default database path: `data/application.db`, configurable through top-level `application_storage.path`.
- Existing optional storage configuration and `data/messages.db` behavior remain unchanged.
- `schema_migrations` records the positive migration version, UTC application timestamp, and SHA-256 checksum of the immutable SQL statement sequence.
- Each migration runs inside `BEGIN IMMEDIATE`; schema changes and the version/checksum record commit atomically. Failed migrations roll back. Applied checksum drift and unknown migration versions fail closed.
- SQLite foreign-key enforcement is enabled and verified during initialization and on every connection opened through `ApplicationDatabase.connect()`.
- Migration SQL executes statement-by-statement rather than through `executescript`, preserving transaction boundaries.
- Migration 1 creates only `export_jobs`, `export_delivery_attempts`, `export_cleanup_tasks`, their approved checks/foreign keys/indexes, and migration metadata.
- No legacy message rows are copied, inferred, renamed, or modified. No PostgreSQL schema is added in this slice.

## Step 2 — application lifecycle integration

- Root `main.py` constructs `ApplicationDatabase` from `config.application_storage.path`.
- The database is initialized after configuration and logging are ready, but before platform services, the scheduler, the command service, the bot, or the optional MCP server are constructed.
- A migration or database initialization failure follows the existing initialization-failure path and prevents the application from starting with missing required persistence.
- The initialized database object is retained on `ChatbriefApp` for injection into future application services/repositories.
- The legacy optional message-history store remains a separate subsystem and is not initialized, closed, or otherwise changed by this integration.
- `ApplicationDatabase.initialize()` uses a scoped SQLite connection and closes it before returning. The database object does not own a persistent connection or pool, so there is no artificial shutdown `close()` method. Future repository connections must be scoped and closed by their owners.

## Tests added

- Startup initializes the application database using the configured path before platform construction.
- Database initialization failure aborts startup before platform services are created.
- Existing migration/configuration tests continue to cover schema creation, idempotency, foreign keys, partial uniqueness, checksum drift, rollback, and path validation.

## Step 2 — local verification

The developer confirmed that the focused lifecycle/migration/configuration tests and the full pytest suite passed after the `pytest.ini` repository-root import-path correction. Ruff lint, Ruff formatting, and Pyright had also passed. Exact pytest counts for this follow-up were not included in the confirmation, so no counts are recorded here.

The developer subsequently reported updating Git with the refreshed graph after Step 3a. A further Graphify refresh is required after Step 3b source changes; the assistant cannot run or verify the local graph CLI.

## Step 3a — export-job repository and atomic state transitions

Implemented and developer-validated. Focused export/storage/config/lifecycle tests: **109 passed**; Ruff lint passed; Pyright **0 errors, 0 warnings, 0 informations**; full suite **612 passed, 7 skipped**, coverage **94.42%**; Ruff format check passed after formatting.

- `ExportRepository.create_job()` creates an opaque internal job UUID and a separate opaque export UUID, assigns the authenticated Telegram user as owner, and starts the job in `queued`.
- The database partial unique index remains the final concurrency guard enforcing one blocking export per user. The repository translates that specific uniqueness conflict into `ActiveExportExistsError`.
- `get_job()` supports owner-scoped reads; `get_active_job()` returns the user's blocking job, including a `ready` job within its availability period.
- `transition_job()` requires the owner ID and uses a short `BEGIN IMMEDIATE` transaction with expected-state compare-and-set. Invalid lifecycle edges are rejected; a stale or wrong-owner transition returns `None`. The generic method permits forward progress/failure only; cancellation, invalidation, and expiry must use cleanup-aware operations in a later slice.
- Mutable fields are allowlisted, JSON metadata is checked before persistence, and terminal timestamps are assigned atomically.
- A job cannot become `ready` unless a successful primary delivery attempt is already recorded, and the persisted primary-delivery timestamp must match that attempt. The delivery-attempt repository is a subsequent slice; this guard intentionally prevents premature `ready` transitions in the meantime.
- Worker claims, lease renewal/generation fencing, cancellation cleanup orchestration, and workers remain out of scope for this slice.

Focused tests cover owner scoping, per-user uniqueness, terminal-state release, allowed/forbidden transitions, stale compare-and-set behavior, metadata validation, and the confirmed-primary-delivery guard.

## Step 3b — delivery-attempt and cleanup-task repositories

Implemented and developer-validated. Focused Step 3b tests: **119 passed**; Ruff lint passed; Ruff format check passed; Pyright **0 errors, 0 warnings, 0 informations**; full suite **622 passed, 7 skipped**, coverage **94.07%**. No migration or schema change was required because migration 1 already defines both tables.

- Added typed delivery-attempt/document-kind models and `ExportDeliveryRepository`.
- `start_attempt()` appends a per-job/per-document attempt number in a short `BEGIN IMMEDIATE` transaction, requires an owner-owned job in `packaging`, and prevents concurrent unresolved attempts. Media attempts require a confirmed successful primary attempt.
- Failed attempts may be retried with a new attempt number. `started`, `succeeded`, and `delivery_unknown` block automatic retries; ambiguous delivery is not retried automatically because it could duplicate a Telegram document.
- `finish_attempt()` resolves a started attempt once, stores only restricted Telegram delivery identifiers, retry metadata, and stable error codes, and updates the job's media outcome for media attempts. The existing `ready` transition now has the persisted successful-primary record it requires.
- Added `ExportCleanupRepository` for owner-checked creation of Telegram-message and opaque-staging deletion tasks, due-task listing for an internal worker, task lookup, and compare-and-set attempt/result updates.
- Cleanup tasks retain their target data when the parent job is deleted (`ON DELETE SET NULL`); they can still be read and completed afterward. Deadline-expired pending tasks remain visible to the cleanup worker so it can mark them abandoned instead of silently losing them.
- Added focused tests for primary/media delivery, owner checks, retries and attempt numbering, unknown outcomes, terminal resolution, cleanup scheduling/retries, and parent-job deletion.
- No worker leases, external Telegram calls, archive/staging filesystem operations, or user-facing commands were added.

## Step 3c — worker claims and lease-generation fencing

Implemented and developer-validated. Ruff lint and format passed; Pyright passed; full suite **627 passed, 7 skipped**, coverage **93.38%**. The existing migration-1 lease columns and lease-expiry index are reused; no schema migration is required.

- `claim_next_job()` atomically selects the earliest due queued/collecting/packaging job whose lease is absent or expired, assigns the worker, sets the expiry, and increments the generation.
- `renew_lease()` and `release_lease()` require the current worker ID, generation, and an unexpired lease. Release can set a future `next_run_at` for backoff.
- `transition_claimed_job()` fences state transitions by worker ID, generation, and live expiry. A stale worker cannot transition a job after expiry or after another worker reclaims it. Transitions to ready or a terminal state clear the lease.
- Lease timestamps must be timezone-aware ISO 8601 values and are normalized to UTC. Worker IDs are opaque, non-empty identifiers; lease durations are bounded to 1–3600 seconds.
- Focused tests cover competing claims, generation increments after expiry, stale-worker rejection, lease renewal/release, scheduled retry eligibility, and invalid lease parameters.
- This slice adds persistence primitives only. It does not start a worker loop, perform external work, or change delivery-attempt writes to require a lease token.

## Step 3d — fair per-user claim scheduling

Implemented in source; local validation is pending. Migration 2 adds nullable `export_jobs.last_claimed_at` and an index for fair claim selection.

- Claims prefer users who have never been served; after that, the least recently claimed eligible user's job is selected.
- `created_at`, owner Telegram user ID, and job ID provide deterministic tie ordering. The existing one-blocking-export-per-user constraint means at most one eligible blocking job currently exists per user; if that constraint changes, per-user queue-head selection must be revisited.
- Claim selection and lease assignment remain in the same `BEGIN IMMEDIATE` transaction. The selected job's `last_claimed_at` is updated atomically with its lease, so fairness survives process restarts and competing workers.
- Reclaiming an expired job counts as serving that user again.
- No priority tiers, external queue, in-memory-only round robin, or additional user profile data are introduced.
- Focused tests exercise rotation across three users and upgrade an existing version-1 database to migration 2.

## Step 3e — delivery-attempt lease fencing

Implemented and developer-validated. Migration 3 adds nullable `worker_id` and `lease_generation` columns to delivery attempts. Focused delivery/storage tests: **19 passed**; full suite: **631 passed, 7 skipped**, coverage **93.40%**; Ruff lint/format passed; Pyright **0 errors, 0 warnings, 0 informations**.

- Starting an attempt requires the caller's current worker ID and lease generation, and the export job must still be in `packaging` with that live lease.
- The attempt persists the exact worker ID and generation that created it.
- Finishing an attempt requires both the current live job lease and an exact match with the worker ID/generation recorded on that attempt. A replacement worker cannot finalize an earlier worker's attempt merely by presenting its newer lease.
- The lease check uses the repository operation's current UTC time, not a caller-supplied historical delivery timestamp.
- Existing attempts from before migration 3 receive NULL fencing fields and are not silently assigned to a worker. They cannot be finalized through the new fenced API; no ownership inference is performed.
- All checks and attempt writes remain inside short `BEGIN IMMEDIATE` transactions.
- Focused tests cover current-lease writes and stale-worker rejection after lease release/reclaim.

## Step 4a — export worker orchestration foundation

Implemented and developer-validated. On 2026-11-02 the developer reported Ruff lint passed, Ruff format reported **102 files already formatted**, Pyright reported **0 errors, 0 warnings, 0 informations**, and pytest collected **652 tests** with **7 skipped** and **93.19% coverage**. The pasted terminal output omitted the final pytest passed count, so it is intentionally not recorded.

- `ExportWorker` claims due jobs and dispatches injected handlers by the claimed state.
- Active work is bounded by configured concurrency; lease heartbeats renew active claims and cancel handlers when fencing is lost.
- Failed/no-op work is rescheduled with backoff; shutdown stops claims, waits for a grace period, then cancels remaining work.
- The worker remains deliberately unwired to application startup because no production phase handler exists yet.

## Next steps

1. Implement the minimal user-scoped source/subscription/message persistence and authorization-aware snapshot query required by export collection, following the approved Telegram hybrid-ingestion direction.
2. Do not read or automatically backfill the legacy message-history store for exports: its rows lack trustworthy owner, stable source identity, and message identity.
3. Once the snapshot source exists, implement the collecting handler with cancellation-safe checkpoints and lease-fenced persistence; then proceed to packaging, Telegram delivery, cleanup, and commands. Keep every worker-owned mutation fenced by the current lease generation.
