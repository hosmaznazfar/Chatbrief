# Application-state database and export persistence foundation

**Status:** Steps 1–2 implemented in source; local validation of the startup integration is pending  
**Approved design:** Phase 1 export-persistence migration proposal in telegram-hybrid-ingestion.md

## Scope

Establish a required application-state SQLite database independently from the optional legacy message-history store. The first implementation slices add the database configuration, versioned migration runner, initial export-persistence schema, and application startup integration. Export repositories, workers, commands, archive generation, and delivery remain out of scope.

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

## Local verification

The developer confirmed that Step 1's focused tests, full suite, Ruff lint, Pyright, and formatting checks passed before this lifecycle change. The GitHub editing environment cannot run the developer's local `uv` commands, so Step 2 has **not** been locally validated yet.

Run from the repository root after syncing the branch:

```bash
uv run pytest --no-cov tests/test_application_storage.py tests/test_config.py tests/test_application_lifecycle.py -q
uv run ruff check main.py src/chatbrief/application_storage tests/test_application_storage.py tests/test_application_lifecycle.py
uv run ruff format --check main.py src/chatbrief/application_storage tests/test_application_storage.py tests/test_application_lifecycle.py
uv run pyright
uv run pytest -q
```

Record the actual output here and in the handover. Do not mark Step 2 validated until these checks pass locally.

## Next steps

1. Sync the lifecycle integration and run the focused/static/full checks above.
2. Implement export persistence repositories and atomic job-state operations as a separate slice.
3. Add worker claims/lease-generation fencing only when the repository/state-transition layer is in place.
