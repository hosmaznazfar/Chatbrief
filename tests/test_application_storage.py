"""Tests for the required application-state database and migration runner."""

from contextlib import asynccontextmanager

import aiosqlite
import pytest

from chatbrief.application_storage import ApplicationDatabase, MigrationError
from chatbrief.application_storage.migrations.versions import (
    FAIR_EXPORT_CLAIM_MIGRATION,
    Migration,
)


@asynccontextmanager
async def _connected(database: ApplicationDatabase):
    """Open and reliably close a configured database connection."""
    connection = await database.connect()
    try:
        yield connection
    finally:
        await connection.close()


@pytest.mark.asyncio
async def test_initial_migration_creates_export_schema_and_is_idempotent(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "nested" / "application.db"))

    await database.initialize()
    await database.initialize()

    async with _connected(database) as connection:
        async with connection.execute("SELECT version, checksum FROM schema_migrations") as cursor:
            rows = await cursor.fetchall()
        assert [row[0] for row in rows] == [1, 2]

        async with connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ) as cursor:
            tables = {row[0] for row in await cursor.fetchall()}
        assert {
            "schema_migrations",
            "export_jobs",
            "export_delivery_attempts",
            "export_cleanup_tasks",
        } <= tables

        async with connection.execute("PRAGMA table_info(export_jobs)") as cursor:
            columns = {row[1] for row in await cursor.fetchall()}
        assert "last_claimed_at" in columns


@pytest.mark.asyncio
async def test_foreign_keys_are_enabled_on_every_database_connection(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()

    async with _connected(database) as connection:
        async with connection.execute("PRAGMA foreign_keys") as cursor:
            assert (await cursor.fetchone())[0] == 1


@pytest.mark.asyncio
async def test_foreign_key_constraints_reject_orphaned_delivery_attempts(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()

    async with _connected(database) as connection:
        with pytest.raises(aiosqlite.IntegrityError):
            await connection.execute(
                """INSERT INTO export_delivery_attempts(
                    id, job_id, document_kind, attempt_number, outcome, started_at
                ) VALUES (?, ?, ?, ?, ?, ?)""",
                ("attempt-1", "missing-job", "primary", 1, "started", "now"),
            )


@pytest.mark.asyncio
async def test_partial_unique_index_allows_only_one_blocking_job_per_user(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()

    async with _connected(database) as connection:
        await connection.execute(
            """INSERT INTO export_jobs(
                id, export_id, owner_telegram_user_id, state, cutoff_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("job-1", "export-1", 123, "queued", "now", "now", "now"),
        )
        with pytest.raises(aiosqlite.IntegrityError):
            await connection.execute(
                """INSERT INTO export_jobs(
                    id, export_id, owner_telegram_user_id, state, cutoff_at, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("job-2", "export-2", 123, "collecting", "now", "now", "now"),
            )

        await connection.execute("UPDATE export_jobs SET state = 'failed' WHERE id = 'job-1'")
        await connection.execute(
            """INSERT INTO export_jobs(
                id, export_id, owner_telegram_user_id, state, cutoff_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("job-2", "export-2", 123, "queued", "now", "now", "now"),
        )


@pytest.mark.asyncio
async def test_applied_migration_checksum_drift_is_rejected(tmp_path):
    path = str(tmp_path / "application.db")
    await ApplicationDatabase(path).initialize()
    changed = Migration(version=1, statements=("CREATE TABLE changed (id INTEGER)",))

    with pytest.raises(MigrationError, match="Checksum mismatch"):
        await ApplicationDatabase(
            path, migrations=(changed, FAIR_EXPORT_CLAIM_MIGRATION)
        ).initialize()


@pytest.mark.asyncio
async def test_failed_migration_rolls_back_schema_and_version_record(tmp_path):
    path = str(tmp_path / "application.db")
    migration = Migration(
        version=1,
        statements=(
            "CREATE TABLE should_rollback (id INTEGER)",
            "THIS IS NOT VALID SQL",
        ),
    )

    with pytest.raises(MigrationError, match="Failed to apply"):
        await ApplicationDatabase(path, migrations=(migration,)).initialize()

    async with aiosqlite.connect(path) as connection:
        async with connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'should_rollback'"
        ) as cursor:
            assert await cursor.fetchone() is None
        async with connection.execute("SELECT COUNT(*) FROM schema_migrations") as cursor:
            assert (await cursor.fetchone())[0] == 0
