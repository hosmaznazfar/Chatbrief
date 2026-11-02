"""Tests for the required application-state database and migration runner."""

from contextlib import asynccontextmanager

import aiosqlite
import pytest

from chatbrief.application_storage import ApplicationDatabase, MigrationError
from chatbrief.application_storage.migrations.versions import (
    DELIVERY_LEASE_FENCING_MIGRATION,
    FAIR_EXPORT_CLAIM_MIGRATION,
    INITIAL_EXPORT_MIGRATION,
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
        async with connection.execute(
            "SELECT version, checksum FROM schema_migrations ORDER BY version"
        ) as cursor:
            rows = await cursor.fetchall()
        assert [row[0] for row in rows] == [1, 2, 3, 4]

        async with connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ) as cursor:
            tables = {row[0] for row in await cursor.fetchall()}
        assert {
            "schema_migrations",
            "export_jobs",
            "export_delivery_attempts",
            "export_cleanup_tasks",
            "users",
            "sources",
            "source_access",
            "source_authorizations",
            "subscriptions",
            "messages",
            "source_collection_coverage",
        } <= tables

        async with connection.execute("PRAGMA table_info(export_jobs)") as cursor:
            columns = {row[1] for row in await cursor.fetchall()}
        assert "last_claimed_at" in columns

        async with connection.execute("PRAGMA table_info(export_delivery_attempts)") as cursor:
            attempt_columns = {row[1] for row in await cursor.fetchall()}
        assert {"worker_id", "lease_generation"} <= attempt_columns


@pytest.mark.asyncio
async def test_fair_claim_migration_upgrades_existing_version_one_database(tmp_path):
    path = str(tmp_path / "application.db")
    await ApplicationDatabase(path, migrations=(INITIAL_EXPORT_MIGRATION,)).initialize()

    await ApplicationDatabase(path).initialize()

    async with _connected(ApplicationDatabase(path)) as connection:
        async with connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ) as cursor:
            assert [row[0] for row in await cursor.fetchall()] == [1, 2, 3, 4]
        async with connection.execute("PRAGMA table_info(export_jobs)") as cursor:
            columns = {row[1] for row in await cursor.fetchall()}
        assert "last_claimed_at" in columns


@pytest.mark.asyncio
async def test_delivery_fencing_migration_upgrades_version_two_database(tmp_path):
    path = str(tmp_path / "application.db")
    await ApplicationDatabase(
        path,
        migrations=(INITIAL_EXPORT_MIGRATION, FAIR_EXPORT_CLAIM_MIGRATION),
    ).initialize()

    await ApplicationDatabase(path).initialize()

    async with _connected(ApplicationDatabase(path)) as connection:
        async with connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ) as cursor:
            assert [row[0] for row in await cursor.fetchall()] == [1, 2, 3, 4]
        async with connection.execute("PRAGMA table_info(export_delivery_attempts)") as cursor:
            columns = {row[1] for row in await cursor.fetchall()}
        assert {"worker_id", "lease_generation"} <= columns


@pytest.mark.asyncio
async def test_shared_archive_migration_creates_identity_and_collection_constraints(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()

    async with _connected(database) as connection:
        await connection.execute(
            "INSERT INTO users(telegram_user_id, created_at) VALUES (?, ?)",
            (1001, "2026-11-02T00:00:00Z"),
        )
        await connection.execute(
            """
            INSERT INTO sources(
                id, platform, platform_chat_id, display_name, source_type,
                visibility, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "source-1", "telegram", "-100123", "Example channel", "channel",
                "public", "now", "now",
            ),
        )
        await connection.execute(
            """
            INSERT INTO source_access(
                id, source_id, access_method, owner_telegram_user_id,
                state, created_at, updated_at
            ) VALUES (?, ?, 'bot_api', NULL, 'available', ?, ?)
            """,
            ("access-1", "source-1", "now", "now"),
        )
        await connection.execute(
            """
            INSERT INTO subscriptions(
                id, telegram_user_id, source_id, state, created_at, updated_at
            ) VALUES (?, ?, ?, 'active', ?, ?)
            """,
            ("subscription-1", 1001, "source-1", "now", "now"),
        )
        await connection.execute(
            """
            INSERT INTO messages(
                id, source_id, platform_message_id, text, has_media,
                collected_at
            ) VALUES (?, ?, ?, ?, 0, ?)
            """,
            ("message-1", "source-1", "42", "hello", "now"),
        )
        await connection.execute(
            """
            INSERT INTO source_collection_coverage(
                id, source_id, ingestion_method, covered_from, covered_until, recorded_at
            ) VALUES (?, ?, 'bot_api', ?, ?, ?)
            """,
            ("coverage-1", "source-1", "2026-11-01T00:00:00Z",
             "2026-11-02T00:00:00Z", "now"),
        )

        with pytest.raises(aiosqlite.IntegrityError):
            await connection.execute(
                """
                INSERT INTO messages(
                    id, source_id, platform_message_id, text, has_media, collected_at
                ) VALUES (?, ?, ?, ?, 0, ?)
                """,
                ("message-2", "source-1", "42", "duplicate", "now"),
            )

        with pytest.raises(aiosqlite.IntegrityError):
            await connection.execute(
                """
                INSERT INTO source_access(
                    id, source_id, access_method, owner_telegram_user_id,
                    state, created_at, updated_at
                ) VALUES (?, ?, 'bot_api', NULL, 'available', ?, ?)
                """,
                ("access-2", "source-1", "now", "now"),
            )

        with pytest.raises(aiosqlite.IntegrityError):
            await connection.execute(
                """
                INSERT INTO subscriptions(
                    id, telegram_user_id, source_id, state, created_at, updated_at
                ) VALUES (?, ?, ?, 'active', ?, ?)
                """,
                ("subscription-2", 1001, "source-1", "now", "now"),
            )


@pytest.mark.asyncio
async def test_shared_archive_migration_rejects_invalid_access_and_media_shapes(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()

    async with _connected(database) as connection:
        await connection.execute(
            "INSERT INTO users(telegram_user_id, created_at) VALUES (?, ?)",
            (1001, "now"),
        )
        await connection.execute(
            """
            INSERT INTO sources(
                id, platform, platform_chat_id, display_name, source_type,
                visibility, created_at, updated_at
            ) VALUES (?, 'telegram', ?, ?, 'channel', 'private', ?, ?)
            """,
            ("source-1", "-100123", "Private channel", "now", "now"),
        )
        with pytest.raises(aiosqlite.IntegrityError):
            await connection.execute(
                """
                INSERT INTO source_access(
                    id, source_id, access_method, owner_telegram_user_id,
                    state, created_at, updated_at
                ) VALUES (?, ?, 'telethon', NULL, 'available', ?, ?)
                """,
                ("invalid-access", "source-1", "now", "now"),
            )
        with pytest.raises(aiosqlite.IntegrityError):
            await connection.execute(
                """
                INSERT INTO messages(
                    id, source_id, platform_message_id, text, has_media,
                    media_type, collected_at
                ) VALUES (?, ?, ?, ?, 1, NULL, ?)
                """,
                ("invalid-message", "source-1", "42", "", "now"),
            )


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
            path,
            migrations=(changed, FAIR_EXPORT_CLAIM_MIGRATION, DELIVERY_LEASE_FENCING_MIGRATION),
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
