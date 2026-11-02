# Application-state database and export persistence foundation

**Status:** Steps 1–2 and Steps 3a–3c implemented and developer-validated; Step 3d fair per-user claim scheduling implemented, local validation pending  
**Approved design:** Phase 1 export-persistence migration proposal in telegram-hybrid-ingestion.md

## Scope

Establish a required application-state SQLite database independently from the optional legacy message-history store. The initial slices add the database configuration, versioned migration runner, initial export-persistence schema, and application startup integration. Export-job, delivery-attempt, cleanup-task, worker-lease, and fair-claim scheduling operations are implemented as separate repository slices. Worker orchestration, commands, archive generation, and Telegram delivery remain out of scope.

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
- `created_at`, owner Telegram user ID, and job ID provide deterministic tie ordering. The existing one-blocking-export-per-user constraint means at most one eligible blocking job currently exists per user; if that constraint changes, per-user queue-head selection must be revisited. The existing one-blocking-export-per-user constraint means at most one eligible blocking job currently exists per user; if that constraint changes, per-user queue-head selection must be revisited.
- Claim selection and lease assignment remain in the same `BEGIN IMMEDIATE` transaction. The selected job's `last_claimed_at` is updated atomically with its lease, so fairness survives process restarts and competing workers.
- Reclaiming an expired job counts as serving that user again.
- No priority tiers, external queue, in-memory-only round robin, or additional user profile data are introduced.
- Focused tests exercise rotation across three users and upgrade an existing version-1 database to migration 2.

## Next steps

1. Developer pulls the fair-scheduling commits and runs focused export/storage/delivery/lifecycle tests, Ruff lint/format, Pyright, and the full suite.
2. Fix any validation issues before adding worker orchestration.
3. Worker orchestration then connects lease-fenced claims to application lifecycle and phase handlers; collection, packaging, Telegram delivery, cleanup execution, bounded concurrency configuration, and graceful shutdown remain separate implementation slices.
