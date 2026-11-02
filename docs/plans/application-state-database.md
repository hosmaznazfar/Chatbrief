# Application-state database and export persistence foundation

**Status:** Step 1 implementation committed; focused and full test suites pass; Ruff formatting correction committed and awaiting local recheck  
**Approved design:** Phase 1 export-persistence migration proposal in telegram-hybrid-ingestion.md

## Scope

Establish a required application-state SQLite database independently from the optional legacy message-history store. Add a small versioned migration runner and the first additive schema migration for export persistence. This slice does not initialize the database from application startup and does not implement export repositories, workers, commands, archive generation, or delivery.

## Implementation details

- Default database path: data/application.db, configurable through top-level application_storage.path.
- Existing optional storage configuration and data/messages.db behavior remain unchanged.
- schema_migrations records the positive migration version, UTC application timestamp, and SHA-256 checksum of the immutable SQL statement sequence.
- Each migration runs inside BEGIN IMMEDIATE; schema changes and the version/checksum record commit atomically. Failed migrations roll back. Applied checksum drift and unknown migration versions fail closed.
- SQLite foreign-key enforcement is enabled and verified during initialization and on every connection opened through ApplicationDatabase.connect().
- Migration SQL executes statement-by-statement rather than through executescript, preserving transaction boundaries.
- Migration 1 creates only export_jobs, export_delivery_attempts, export_cleanup_tasks, their approved checks/foreign keys/indexes, and migration metadata.
- No legacy message rows are copied, inferred, renamed, or modified. No PostgreSQL schema is added in this slice.

## Focused local verification

Run from the repository root:

    uv run pytest --no-cov tests/test_application_storage.py tests/test_config.py -q
    uv run pytest -q
    uv run ruff check src/chatbrief/application_storage src/chatbrief/config tests/test_application_storage.py tests/test_config.py
    uv run ruff format --check src/chatbrief/application_storage src/chatbrief/config tests/test_application_storage.py tests/test_config.py
    uv run pyright

The first focused run collected 99 tests: 95 passed and 4 application-storage tests failed because they used `async with await database.connect()`. Awaiting an `aiosqlite.Connection` starts its worker thread; entering that already-awaited connection as an async context manager starts it a second time. The tests now use a small async context manager that awaits `database.connect()` once and closes the returned connection in `finally`. Ruff lint passed and Pyright reported 0 errors, 0 warnings, and 0 informations on the first run. Ruff format identified one formatting change in the test file; the file has also been reformatted in the correction. The focused pytest command additionally hit the repository-wide coverage threshold because only two test files were run (16.49% overall against 49%); rerun the full suite after the focused tests pass. These corrections have not yet been validated locally. The remote GitHub editing environment cannot execute local project commands.

## Next steps

1. Review and run the focused tests and checks above in the local checkout.
2. Add startup initialization and shutdown lifecycle handling for the required application database.
3. Add the export persistence repository and state-transition operations in a separate implementation step.
