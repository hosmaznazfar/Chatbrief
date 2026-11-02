"""Durable export-job persistence and atomic lifecycle transitions."""

from __future__ import annotations

import json
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import AsyncIterator, Mapping, Sequence

import aiosqlite

from .migrations import ApplicationDatabase


class ExportJobState(StrEnum):
    """Persisted export-job lifecycle states."""

    QUEUED = "queued"
    COLLECTING = "collecting"
    PACKAGING = "packaging"
    READY = "ready"
    CANCELLED = "cancelled"
    FAILED = "failed"
    INVALIDATED = "invalidated"
    EXPIRED = "expired"


class ExportMediaOutcome(StrEnum):
    """Outcome of the optional media companion delivery."""

    SENT = "sent"
    OMITTED = "omitted"
    FAILED = "failed"
    DELIVERY_UNKNOWN = "delivery_unknown"


class ActiveExportExistsError(RuntimeError):
    """Raised when a user already owns an export that blocks a new request."""


class InvalidExportTransitionError(ValueError):
    """Raised when a requested export state transition is not permitted."""


@dataclass(frozen=True, slots=True)
class ExportJob:
    """Application-internal representation of a persisted export job."""

    id: str
    export_id: str
    owner_telegram_user_id: int
    state: ExportJobState
    media_outcome: ExportMediaOutcome | None
    cutoff_at: str
    created_at: str
    updated_at: str
    primary_delivered_at: str | None
    expires_at: str | None
    terminal_at: str | None
    lease_owner: str | None
    lease_expires_at: str | None
    lease_generation: int
    next_run_at: str | None
    staging_key: str | None
    report_json: str | None
    media_manifest_json: str | None
    last_error_code: str | None


_ACTIVE_STATES = (
    ExportJobState.QUEUED,
    ExportJobState.COLLECTING,
    ExportJobState.PACKAGING,
    ExportJobState.READY,
)
_TERMINAL_STATES = {
    ExportJobState.CANCELLED,
    ExportJobState.FAILED,
    ExportJobState.INVALIDATED,
    ExportJobState.EXPIRED,
}
_ALLOWED_TRANSITIONS = {
    ExportJobState.QUEUED: {
        ExportJobState.COLLECTING,
        ExportJobState.CANCELLED,
        ExportJobState.FAILED,
        ExportJobState.INVALIDATED,
    },
    ExportJobState.COLLECTING: {
        ExportJobState.PACKAGING,
        ExportJobState.CANCELLED,
        ExportJobState.FAILED,
        ExportJobState.INVALIDATED,
    },
    ExportJobState.PACKAGING: {
        ExportJobState.READY,
        ExportJobState.CANCELLED,
        ExportJobState.FAILED,
        ExportJobState.INVALIDATED,
    },
    ExportJobState.READY: {
        ExportJobState.CANCELLED,
        ExportJobState.INVALIDATED,
        ExportJobState.EXPIRED,
    },
    ExportJobState.CANCELLED: set(),
    ExportJobState.FAILED: set(),
    ExportJobState.INVALIDATED: set(),
    ExportJobState.EXPIRED: set(),
}
_MUTABLE_FIELDS = {
    "media_outcome",
    "primary_delivered_at",
    "expires_at",
    "next_run_at",
    "staging_key",
    "report_json",
    "media_manifest_json",
    "last_error_code",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _job_from_row(row: aiosqlite.Row) -> ExportJob:
    media_outcome = row["media_outcome"]
    return ExportJob(
        id=row["id"],
        export_id=row["export_id"],
        owner_telegram_user_id=row["owner_telegram_user_id"],
        state=ExportJobState(row["state"]),
        media_outcome=ExportMediaOutcome(media_outcome) if media_outcome else None,
        cutoff_at=row["cutoff_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        primary_delivered_at=row["primary_delivered_at"],
        expires_at=row["expires_at"],
        terminal_at=row["terminal_at"],
        lease_owner=row["lease_owner"],
        lease_expires_at=row["lease_expires_at"],
        lease_generation=row["lease_generation"],
        next_run_at=row["next_run_at"],
        staging_key=row["staging_key"],
        report_json=row["report_json"],
        media_manifest_json=row["media_manifest_json"],
        last_error_code=row["last_error_code"],
    )


class ExportRepository:
    """Persist export jobs without coupling them to optional message history."""

    def __init__(self, database: ApplicationDatabase) -> None:
        self._database = database

    @asynccontextmanager
    async def _connection(self) -> AsyncIterator[aiosqlite.Connection]:
        connection = await self._database.connect()
        connection.row_factory = aiosqlite.Row
        try:
            yield connection
        finally:
            await connection.close()

    @staticmethod
    def _validate_owner(owner_telegram_user_id: int) -> None:
        if (
            isinstance(owner_telegram_user_id, bool)
            or not isinstance(owner_telegram_user_id, int)
            or owner_telegram_user_id <= 0
        ):
            raise ValueError("Telegram user ID must be a positive integer")

    async def create_job(
        self,
        owner_telegram_user_id: int,
        cutoff_at: str,
        *,
        created_at: str | None = None,
    ) -> ExportJob:
        """Create a queued export; the partial unique index arbitrates races."""
        self._validate_owner(owner_telegram_user_id)
        if not isinstance(cutoff_at, str) or not cutoff_at:
            raise ValueError("Export cutoff timestamp must be non-empty")

        timestamp = created_at or _utc_now()
        job_id = str(uuid.uuid4())
        export_id = str(uuid.uuid4())

        async with self._connection() as connection:
            try:
                await connection.execute("BEGIN IMMEDIATE")
                await connection.execute(
                    """
                    INSERT INTO export_jobs(
                        id, export_id, owner_telegram_user_id, state,
                        cutoff_at, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job_id,
                        export_id,
                        owner_telegram_user_id,
                        ExportJobState.QUEUED.value,
                        cutoff_at,
                        timestamp,
                        timestamp,
                    ),
                )
                async with connection.execute(
                    "SELECT * FROM export_jobs WHERE id = ? AND owner_telegram_user_id = ?",
                    (job_id, owner_telegram_user_id),
                ) as cursor:
                    row = await cursor.fetchone()
                await connection.commit()
            except aiosqlite.IntegrityError as error:
                await connection.rollback()
                if (
                    "uq_export_jobs_one_blocking_per_user" in str(error)
                    or "export_jobs.owner_telegram_user_id" in str(error)
                ):
                    raise ActiveExportExistsError(
                        "User already has an active export"
                    ) from error
                raise
            except Exception:
                await connection.rollback()
                raise

        if row is None:
            raise RuntimeError("Created export job could not be read back")
        return _job_from_row(row)

    async def get_job(
        self,
        job_id: str,
        *,
        owner_telegram_user_id: int | None = None,
    ) -> ExportJob | None:
        """Read a job, optionally enforcing its owning Telegram user."""
        query = "SELECT * FROM export_jobs WHERE id = ?"
        parameters: tuple[object, ...] = (job_id,)
        if owner_telegram_user_id is not None:
            self._validate_owner(owner_telegram_user_id)
            query += " AND owner_telegram_user_id = ?"
            parameters += (owner_telegram_user_id,)

        async with self._connection() as connection:
            async with connection.execute(query, parameters) as cursor:
                row = await cursor.fetchone()
        return _job_from_row(row) if row is not None else None

    async def get_active_job(self, owner_telegram_user_id: int) -> ExportJob | None:
        """Return the user's single blocking export, if one exists."""
        self._validate_owner(owner_telegram_user_id)
        placeholders = ", ".join("?" for _ in _ACTIVE_STATES)
        query = (
            f"SELECT * FROM export_jobs WHERE owner_telegram_user_id = ? "
            f"AND state IN ({placeholders}) ORDER BY created_at DESC LIMIT 1"
        )
        parameters = (owner_telegram_user_id, *(state.value for state in _ACTIVE_STATES))
        async with self._connection() as connection:
            async with connection.execute(query, parameters) as cursor:
                row = await cursor.fetchone()
        return _job_from_row(row) if row is not None else None

    async def transition_job(
        self,
        job_id: str,
        owner_telegram_user_id: int,
        expected_states: Sequence[ExportJobState],
        new_state: ExportJobState,
        *,
        updated_at: str | None = None,
        updates: Mapping[str, str | None] | None = None,
    ) -> ExportJob | None:
        """Atomically transition a job only if its current state is expected.

        Returns None when another operation has already changed the state. This
        compare-and-set operation prevents cancellation and completion from both
        winning a race. Worker lease-generation fencing is a separate later step.
        """
        self._validate_owner(owner_telegram_user_id)
        expected = tuple(dict.fromkeys(ExportJobState(state) for state in expected_states))
        if not expected:
            raise ValueError("At least one expected state is required")
        target = ExportJobState(new_state)
        if any(target not in _ALLOWED_TRANSITIONS[state] for state in expected):
            raise InvalidExportTransitionError(
                f"Transition from {', '.join(state.value for state in expected)} "
                f"to {target.value} is not permitted"
            )

        changes = dict(updates or {})
        unknown_fields = set(changes) - _MUTABLE_FIELDS
        if unknown_fields:
            raise ValueError(f"Unsupported export-job fields: {sorted(unknown_fields)}")
        if "media_outcome" in changes and changes["media_outcome"] is not None:
            changes["media_outcome"] = ExportMediaOutcome(
                changes["media_outcome"]
            ).value
        for json_field in ("report_json", "media_manifest_json"):
            if json_field in changes and changes[json_field] is not None:
                try:
                    json.loads(changes[json_field])
                except (TypeError, json.JSONDecodeError) as error:
                    raise ValueError(f"{json_field} must contain valid JSON") from error

        timestamp = updated_at or _utc_now()
        placeholders = ", ".join("?" for _ in expected)

        async with self._connection() as connection:
            try:
                await connection.execute("BEGIN IMMEDIATE")
                async with connection.execute(
                    "SELECT * FROM export_jobs WHERE id = ? AND owner_telegram_user_id = ?",
                    (job_id, owner_telegram_user_id),
                ) as cursor:
                    current = await cursor.fetchone()
                if current is None or ExportJobState(current["state"]) not in expected:
                    await connection.rollback()
                    return None

                if target is ExportJobState.READY:
                    async with connection.execute(
                        """
                        SELECT finished_at FROM export_delivery_attempts
                        WHERE job_id = ? AND document_kind = 'primary'
                          AND outcome = 'succeeded'
                        ORDER BY attempt_number DESC LIMIT 1
                        """,
                        (job_id,),
                    ) as cursor:
                        successful_attempt = await cursor.fetchone()
                    if successful_attempt is None:
                        raise ValueError(
                            "A ready export requires a confirmed primary delivery attempt"
                        )
                    delivered_at = successful_attempt["finished_at"]
                    expires_at = changes.get("expires_at", current["expires_at"])
                    if not delivered_at or not expires_at:
                        raise ValueError(
                            "A ready export requires primary delivery and expiry timestamps"
                        )
                    if (
                        "primary_delivered_at" in changes
                        and changes["primary_delivered_at"] != delivered_at
                    ):
                        raise ValueError(
                            "Primary delivery timestamp must match the confirmed attempt"
                        )
                    changes["primary_delivered_at"] = delivered_at

                assignments = ["state = ?", "updated_at = ?"]
                parameters: list[object] = [target.value, timestamp]
                for field_name, value in changes.items():
                    assignments.append(f"{field_name} = ?")
                    parameters.append(value)
                if target in _TERMINAL_STATES:
                    assignments.append("terminal_at = COALESCE(terminal_at, ?)")
                    parameters.append(timestamp)
                else:
                    assignments.append("terminal_at = NULL")
                parameters.extend(
                    (job_id, owner_telegram_user_id, *(state.value for state in expected))
                )

                result = await connection.execute(
                    f"""
                    UPDATE export_jobs
                    SET {", ".join(assignments)}
                    WHERE id = ? AND owner_telegram_user_id = ? AND state IN ({placeholders})
                    """,
                    parameters,
                )
                if result.rowcount != 1:
                    await connection.rollback()
                    return None
                async with connection.execute(
                    "SELECT * FROM export_jobs WHERE id = ?", (job_id,)
                ) as cursor:
                    updated = await cursor.fetchone()
                await connection.commit()
            except Exception:
                await connection.rollback()
                raise

        if updated is None:
            raise RuntimeError("Updated export job could not be read back")
        return _job_from_row(updated)
