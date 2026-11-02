"""Transactional SQLite migration runner for required application state."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import aiosqlite

from .versions import MIGRATIONS, Migration


class MigrationError(RuntimeError):
    """Raised when application database migrations cannot be trusted or applied."""


def _restrict_database_permissions(path: str) -> None:
    """Restrict the database file to its owning user on POSIX systems."""
    if os.name == "posix":
        os.chmod(path, 0o600)


class ApplicationDatabase:
    """Own the required SQLite application database and apply versioned migrations."""

    def __init__(self, path: str, migrations: Sequence[Migration] = MIGRATIONS) -> None:
        if not isinstance(path, str) or not path.strip():
            raise ValueError("Application database path must be a non-empty string")
        self.path = path
        self._migrations = tuple(migrations)
        versions = [migration.version for migration in self._migrations]
        if any(version < 1 for version in versions) or versions != sorted(set(versions)):
            raise ValueError("Migration versions must be unique, positive, and ordered")

    @staticmethod
    def _checksum(migration: Migration) -> str:
        payload = "\n-- statement --\n".join(
            statement.strip() for statement in migration.statements
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    async def initialize(self) -> None:
        """Create the database directory and apply every unapplied migration."""
        Path(self.path).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        async with aiosqlite.connect(self.path) as connection:
            _restrict_database_permissions(self.path)
            await connection.execute("PRAGMA foreign_keys = ON")
            async with connection.execute("PRAGMA foreign_keys") as cursor:
                row = await cursor.fetchone()
            if row is None or row[0] != 1:
                raise MigrationError("SQLite foreign-key enforcement could not be enabled")

            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY CHECK (version > 0),
                    applied_at TEXT NOT NULL,
                    checksum TEXT NOT NULL
                )
                """
            )
            await connection.commit()

            applied: dict[int, str] = {}
            async with connection.execute(
                "SELECT version, checksum FROM schema_migrations ORDER BY version"
            ) as cursor:
                async for version, checksum in cursor:
                    applied[int(version)] = str(checksum)

            known_versions = {migration.version for migration in self._migrations}
            unknown = set(applied) - known_versions
            if unknown:
                raise MigrationError(
                    f"Database contains unknown migration versions: {sorted(unknown)}"
                )

            for migration in self._migrations:
                checksum = self._checksum(migration)
                existing = applied.get(migration.version)
                if existing is not None:
                    if existing != checksum:
                        raise MigrationError(
                            f"Checksum mismatch for applied migration {migration.version}"
                        )
                    continue

                try:
                    await connection.execute("BEGIN IMMEDIATE")
                    for statement in migration.statements:
                        await connection.execute(statement)
                    await connection.execute(
                        """
                        INSERT INTO schema_migrations(version, applied_at, checksum)
                        VALUES (?, ?, ?)
                        """,
                        (
                            migration.version,
                            datetime.now(timezone.utc).isoformat(),
                            checksum,
                        ),
                    )
                    await connection.commit()
                except Exception as error:
                    await connection.rollback()
                    raise MigrationError(
                        f"Failed to apply migration {migration.version}"
                    ) from error

    async def connect(self) -> aiosqlite.Connection:
        """Open a configured connection with foreign-key enforcement enabled."""
        connection = await aiosqlite.connect(self.path)
        _restrict_database_permissions(self.path)
        await connection.execute("PRAGMA foreign_keys = ON")
        async with connection.execute("PRAGMA foreign_keys") as cursor:
            row = await cursor.fetchone()
        if row is None or row[0] != 1:
            await connection.close()
            raise MigrationError("SQLite foreign-key enforcement could not be enabled")
        return connection
