# Application-state database and export persistence foundation

**Status:** Steps 1–2 implemented and developer-validated; Step 3a export-job repository implemented, local validation pending  
**Approved design:** Phase 1 export-persistence migration proposal in telegram-hybrid-ingestion.md

## Scope

Establish a required application-state SQLite database independently from the optional legacy message-history store. The initial slices add the database configuration, versioned migration runner, initial export-persistence schema, and application startup integration. Export-job persistence is now being implemented separately from delivery attempts, workers, commands, archive generation, and Telegram delivery.

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

The developer ran `./pj graph sync`; Graphify reported that no code-graph topology changes were detected. The developer reviewed/updated the graph and pushed commit `ab53ac1`. That graph revision describes the source before the Step 3a changes below and must be refreshed after those changes are complete.

## Step 3a — export-job repository and atomic state transitions

Implemented in source; local validation is pending.

- `ExportRepository.create_job()` creates an opaque internal job UUID and a separate opaque export UUID, assigns the authenticated Telegram user as owner, and starts the job in `queued`.
- The database partial unique index remains the final concurrency guard enforcing one blocking export per user. The repository translates that specific uniqueness conflict into `ActiveExportExistsError`.
- `get_job()` supports owner-scoped reads; `get_active_job()` returns the user's blocking job, including a `ready` job within its availability period.
- `transition_job()` uses a short `BEGIN IMMEDIATE` transaction and expected-state compare-and-set. Invalid lifecycle edges are rejected; a stale competing transition returns `None`.
- Mutable fields are allowlisted, JSON metadata is checked before persistence, and terminal timestamps are assigned atomically.
- A job cannot become `ready` unless a successful primary delivery attempt is already recorded, and the persisted primary-delivery timestamp must match that attempt. The delivery-attempt repository is a subsequent slice; this guard intentionally prevents premature `ready` transitions in the meantime.
- Worker claims, lease renewal/generation fencing, delivery-attempt APIs, cleanup-task APIs, cancellation cleanup orchestration, and workers remain out of scope for this slice.

Focused tests were added for owner scoping, per-user uniqueness, terminal-state release, allowed/forbidden transitions, stale compare-and-set behavior, metadata validation, and the confirmed-primary-delivery guard.

## Next steps

1. Run focused export repository, application storage, configuration, and lifecycle tests plus Ruff, formatting, and Pyright locally.
2. Review the repository implementation and add delivery-attempt/cleanup-task persistence APIs.
3. Add worker claims and lease-generation fencing after the job and attempt repository operations are established.
