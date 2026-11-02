"""Durable delivery-attempt and export-cleanup persistence."""

from __future__ import annotations

import re
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import AsyncIterator

import aiosqlite

from .exports import _normalize_lease_timestamp, _validate_lease_generation, _validate_worker_id
from .migrations import ApplicationDatabase


class DeliveryDocumentKind(StrEnum):
    """Kind of export document sent through Telegram."""

    PRIMARY = "primary"
    MEDIA = "media"


class DeliveryAttemptOutcome(StrEnum):
    """Persisted result of one Telegram delivery attempt."""

    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DELIVERY_UNKNOWN = "delivery_unknown"


class CleanupTaskType(StrEnum):
    """External resource that a cleanup task removes."""

    TELEGRAM_MESSAGE_DELETE = "telegram_message_delete"
    STAGING_DELETE = "staging_delete"


class CleanupTaskState(StrEnum):
    """Lifecycle state of a cleanup task."""

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    ABANDONED = "abandoned"


@dataclass(frozen=True, slots=True)
class ExportDeliveryAttempt:
    """One durable delivery attempt, including restricted Telegram identifiers."""

    id: str
    job_id: str
    document_kind: DeliveryDocumentKind
    attempt_number: int
    outcome: DeliveryAttemptOutcome
    started_at: str
    finished_at: str | None
    retry_after_at: str | None
    telegram_chat_id: int | None
    telegram_message_id: int | None
    telegram_file_id: str | None
    error_code: str | None
    retry_after_seconds: int | None


@dataclass(frozen=True, slots=True)
class ExportCleanupTask:
    """Durable instruction to remove an external Telegram or staging resource."""

    id: str
    job_id: str | None
    task_type: CleanupTaskType
    state: CleanupTaskState
    telegram_chat_id: int | None
    telegram_message_id: int | None
    staging_key: str | None
    attempt_count: int
    next_attempt_at: str
    deadline_at: str | None
    last_error_code: str | None
    created_at: str
    updated_at: str


def _validate_error_code(error_code: str | None) -> None:
    if error_code is not None and (
        not isinstance(error_code, str) or re.fullmatch(r"[a-z][a-z0-9_]{0,63}", error_code) is None
    ):
        raise ValueError("Error codes must be lowercase stable identifiers")


def _validate_positive_identifier(value: int | None, field_name: str) -> None:
    if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value <= 0):
        raise ValueError(f"{field_name} must be a positive integer")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _attempt_from_row(row: aiosqlite.Row) -> ExportDeliveryAttempt:
    return ExportDeliveryAttempt(
        id=row["id"],
        job_id=row["job_id"],
        document_kind=DeliveryDocumentKind(row["document_kind"]),
        attempt_number=row["attempt_number"],
        outcome=DeliveryAttemptOutcome(row["outcome"]),
        started_at=row["started_at"],
        finished_at=row["finished_at"],
        retry_after_at=row["retry_after_at"],
        telegram_chat_id=row["telegram_chat_id"],
        telegram_message_id=row["telegram_message_id"],
        telegram_file_id=row["telegram_file_id"],
        error_code=row["error_code"],
        retry_after_seconds=row["retry_after_seconds"],
    )


def _cleanup_from_row(row: aiosqlite.Row) -> ExportCleanupTask:
    return ExportCleanupTask(
        id=row["id"],
        job_id=row["job_id"],
        task_type=CleanupTaskType(row["task_type"]),
        state=CleanupTaskState(row["state"]),
        telegram_chat_id=row["telegram_chat_id"],
        telegram_message_id=row["telegram_message_id"],
        staging_key=row["staging_key"],
        attempt_count=row["attempt_count"],
        next_attempt_at=row["next_attempt_at"],
        deadline_at=row["deadline_at"],
        last_error_code=row["last_error_code"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _validate_delivery_identifiers(
    outcome: DeliveryAttemptOutcome,
    telegram_chat_id: int | None,
    telegram_message_id: int | None,
    telegram_file_id: str | None,
) -> None:
    _validate_positive_identifier(telegram_message_id, "telegram_message_id")
    if telegram_chat_id is not None and (
        isinstance(telegram_chat_id, bool)
        or not isinstance(telegram_chat_id, int)
        or telegram_chat_id == 0
    ):
        raise ValueError("telegram_chat_id must be a non-zero integer")
    if telegram_file_id is not None and (
        not isinstance(telegram_file_id, str) or not telegram_file_id
    ):
        raise ValueError("telegram_file_id must be a non-empty string")
    identifiers_present = any(
        value is not None for value in (telegram_chat_id, telegram_message_id, telegram_file_id)
    )
    if outcome is DeliveryAttemptOutcome.SUCCEEDED:
        if telegram_chat_id is None or telegram_message_id is None:
            raise ValueError("Confirmed Telegram delivery requires chat and message IDs")
    elif identifiers_present:
        raise ValueError("Unconfirmed delivery cannot persist Telegram delivery identifiers")


def _validate_retry_metadata(
    outcome: DeliveryAttemptOutcome,
    retry_after_at: str | None,
    error_code: str | None,
    retry_after_seconds: int | None,
) -> None:
    if retry_after_at is not None and (not isinstance(retry_after_at, str) or not retry_after_at):
        raise ValueError("retry_after_at must be a non-empty timestamp")
    _validate_error_code(error_code)
    if retry_after_seconds is not None and (
        isinstance(retry_after_seconds, bool)
        or not isinstance(retry_after_seconds, int)
        or retry_after_seconds < 0
    ):
        raise ValueError("retry_after_seconds must be a non-negative integer")
    if outcome is DeliveryAttemptOutcome.SUCCEEDED and (
        retry_after_at is not None or retry_after_seconds is not None or error_code is not None
    ):
        raise ValueError("Successful delivery cannot include retry or error metadata")


def _validate_finish_metadata(
    outcome: DeliveryAttemptOutcome,
    finished_at: str | None,
    retry_after_at: str | None,
    telegram_chat_id: int | None,
    telegram_message_id: int | None,
    telegram_file_id: str | None,
    error_code: str | None,
    retry_after_seconds: int | None,
) -> str:
    if outcome is DeliveryAttemptOutcome.STARTED:
        raise ValueError("A delivery attempt must finish with a final outcome")
    timestamp = finished_at or _utc_now()
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("Attempt finish timestamp must be non-empty")
    _validate_retry_metadata(outcome, retry_after_at, error_code, retry_after_seconds)
    _validate_delivery_identifiers(outcome, telegram_chat_id, telegram_message_id, telegram_file_id)
    return timestamp


class ExportDeliveryRepository:
    """Persist owner-scoped delivery attempts without storing message content."""

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

    async def start_attempt(
        self,
        job_id: str,
        owner_telegram_user_id: int,
        document_kind: DeliveryDocumentKind,
        *,
        worker_id: str,
        lease_generation: int,
        started_at: str | None = None,
    ) -> ExportDeliveryAttempt | None:
        """Append a started attempt for a packaging job owned by the caller.

        Failed attempts may be retried. A started attempt blocks another attempt,
        and a successful or delivery-unknown result is deliberately not retried
        automatically because doing so could duplicate a Telegram document.
        """
        self._validate_owner(owner_telegram_user_id)
        _validate_worker_id(worker_id)
        _validate_lease_generation(lease_generation)
        kind = DeliveryDocumentKind(document_kind)
        now = _normalize_lease_timestamp(_utc_now(), "now")
        timestamp = started_at or now
        if not isinstance(timestamp, str) or not timestamp:
            raise ValueError("Attempt start timestamp must be non-empty")
        attempt_id = str(uuid.uuid4())

        async with self._connection() as connection:
            await connection.execute("BEGIN IMMEDIATE")
            try:
                async with connection.execute(
                    """
                    SELECT state FROM export_jobs
                    WHERE id = ? AND owner_telegram_user_id = ?
                      AND lease_owner = ? AND lease_generation = ?
                      AND lease_expires_at > ?
                    """,
                    (job_id, owner_telegram_user_id, worker_id, lease_generation, now),
                ) as cursor:
                    job = await cursor.fetchone()
                if job is None:
                    await connection.rollback()
                    return None
                if job["state"] != "packaging":
                    raise ValueError("Delivery attempts require a packaging export job")

                if kind is DeliveryDocumentKind.MEDIA:
                    async with connection.execute(
                        """
                        SELECT 1 FROM export_delivery_attempts
                        WHERE job_id = ? AND document_kind = 'primary'
                          AND outcome = 'succeeded'
                        LIMIT 1
                        """,
                        (job_id,),
                    ) as cursor:
                        primary_success = await cursor.fetchone()
                    if primary_success is None:
                        raise ValueError("Media delivery requires confirmed primary delivery")

                async with connection.execute(
                    """
                    SELECT attempt_number, outcome
                    FROM export_delivery_attempts
                    WHERE job_id = ? AND document_kind = ?
                    ORDER BY attempt_number DESC LIMIT 1
                    """,
                    (job_id, kind.value),
                ) as cursor:
                    previous = await cursor.fetchone()
                if previous is not None and previous["outcome"] in {
                    DeliveryAttemptOutcome.STARTED.value,
                    DeliveryAttemptOutcome.SUCCEEDED.value,
                    DeliveryAttemptOutcome.DELIVERY_UNKNOWN.value,
                }:
                    raise ValueError(
                        "The previous delivery attempt must be resolved as failed before retry"
                    )
                attempt_number = previous["attempt_number"] + 1 if previous else 1
                await connection.execute(
                    """
                    INSERT INTO export_delivery_attempts(
                        id, job_id, document_kind, attempt_number, outcome, started_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        attempt_id,
                        job_id,
                        kind.value,
                        attempt_number,
                        DeliveryAttemptOutcome.STARTED.value,
                        timestamp,
                    ),
                )
                async with connection.execute(
                    "SELECT * FROM export_delivery_attempts WHERE id = ?",
                    (attempt_id,),
                ) as cursor:
                    row = await cursor.fetchone()
                await connection.commit()
            except Exception:
                await connection.rollback()
                raise

        if row is None:
            raise RuntimeError("Created delivery attempt could not be read back")
        return _attempt_from_row(row)

    async def finish_attempt(
        self,
        attempt_id: str,
        owner_telegram_user_id: int,
        outcome: DeliveryAttemptOutcome,
        *,
        worker_id: str,
        lease_generation: int,
        finished_at: str | None = None,
        retry_after_at: str | None = None,
        telegram_chat_id: int | None = None,
        telegram_message_id: int | None = None,
        telegram_file_id: str | None = None,
        error_code: str | None = None,
        retry_after_seconds: int | None = None,
    ) -> ExportDeliveryAttempt | None:
        """Resolve a started attempt once; return None for wrong owner or stale ID."""
        self._validate_owner(owner_telegram_user_id)
        _validate_worker_id(worker_id)
        _validate_lease_generation(lease_generation)
        final_outcome = DeliveryAttemptOutcome(outcome)
        now = _normalize_lease_timestamp(_utc_now(), "now")

        async with self._connection() as connection:
            await connection.execute("BEGIN IMMEDIATE")
            try:
                async with connection.execute(
                    """
                    SELECT a.* FROM export_delivery_attempts AS a
                    JOIN export_jobs AS j ON j.id = a.job_id
                    WHERE a.id = ? AND j.owner_telegram_user_id = ?
                      AND j.lease_owner = ? AND j.lease_generation = ?
                      AND j.lease_expires_at > ?
                    """,
                    (attempt_id, owner_telegram_user_id, worker_id, lease_generation, now),
                ) as cursor:
                    current = await cursor.fetchone()
                if current is None or current["outcome"] != DeliveryAttemptOutcome.STARTED.value:
                    await connection.rollback()
                    return None

                timestamp = _validate_finish_metadata(
                    final_outcome,
                    finished_at,
                    retry_after_at,
                    telegram_chat_id,
                    telegram_message_id,
                    telegram_file_id,
                    error_code,
                    retry_after_seconds,
                )
                await connection.execute(
                    """
                    UPDATE export_delivery_attempts
                    SET outcome = ?, finished_at = ?, retry_after_at = ?,
                        telegram_chat_id = ?, telegram_message_id = ?,
                        telegram_file_id = ?, error_code = ?, retry_after_seconds = ?
                    WHERE id = ? AND outcome = 'started'
                    """,
                    (
                        final_outcome.value,
                        timestamp,
                        retry_after_at,
                        telegram_chat_id,
                        telegram_message_id,
                        telegram_file_id,
                        error_code,
                        retry_after_seconds,
                        attempt_id,
                    ),
                )
                if current["document_kind"] == DeliveryDocumentKind.MEDIA.value:
                    media_outcome = {
                        DeliveryAttemptOutcome.SUCCEEDED: "sent",
                        DeliveryAttemptOutcome.FAILED: "failed",
                        DeliveryAttemptOutcome.DELIVERY_UNKNOWN: "delivery_unknown",
                    }[final_outcome]
                    await connection.execute(
                        """
                        UPDATE export_jobs SET media_outcome = ?, updated_at = ?
                        WHERE id = ?
                        """,
                        (media_outcome, timestamp, current["job_id"]),
                    )
                async with connection.execute(
                    "SELECT * FROM export_delivery_attempts WHERE id = ?",
                    (attempt_id,),
                ) as cursor:
                    row = await cursor.fetchone()
                await connection.commit()
            except Exception:
                await connection.rollback()
                raise

        return _attempt_from_row(row) if row is not None else None

    async def list_attempts(
        self, job_id: str, owner_telegram_user_id: int
    ) -> tuple[ExportDeliveryAttempt, ...] | None:
        """List attempts only when the supplied owner owns the export job."""
        self._validate_owner(owner_telegram_user_id)
        async with self._connection() as connection:
            async with connection.execute(
                "SELECT 1 FROM export_jobs WHERE id = ? AND owner_telegram_user_id = ?",
                (job_id, owner_telegram_user_id),
            ) as cursor:
                owned = await cursor.fetchone()
            if owned is None:
                return None
            async with connection.execute(
                """
                SELECT * FROM export_delivery_attempts
                WHERE job_id = ? ORDER BY document_kind, attempt_number
                """,
                (job_id,),
            ) as cursor:
                rows = await cursor.fetchall()
        return tuple(_attempt_from_row(row) for row in rows)


class ExportCleanupRepository:
    """Persist cleanup work independently from the lifetime of its export job."""

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

    async def _require_owned_job(
        self,
        connection: aiosqlite.Connection,
        job_id: str,
        owner_telegram_user_id: int,
    ) -> bool:
        async with connection.execute(
            "SELECT 1 FROM export_jobs WHERE id = ? AND owner_telegram_user_id = ?",
            (job_id, owner_telegram_user_id),
        ) as cursor:
            return await cursor.fetchone() is not None

    async def create_telegram_message_task(
        self,
        job_id: str,
        owner_telegram_user_id: int,
        telegram_chat_id: int,
        telegram_message_id: int,
        *,
        next_attempt_at: str | None = None,
        deadline_at: str | None = None,
    ) -> ExportCleanupTask | None:
        """Queue deletion of a Telegram message associated with an owned export."""
        return await self._create_task(
            job_id,
            owner_telegram_user_id,
            CleanupTaskType.TELEGRAM_MESSAGE_DELETE,
            telegram_chat_id=telegram_chat_id,
            telegram_message_id=telegram_message_id,
            next_attempt_at=next_attempt_at,
            deadline_at=deadline_at,
        )

    async def create_staging_task(
        self,
        job_id: str,
        owner_telegram_user_id: int,
        staging_key: str,
        *,
        next_attempt_at: str | None = None,
        deadline_at: str | None = None,
    ) -> ExportCleanupTask | None:
        """Queue deletion of an opaque staging object associated with an owned export."""
        if not isinstance(staging_key, str) or not staging_key:
            raise ValueError("Staging key must be non-empty")
        return await self._create_task(
            job_id,
            owner_telegram_user_id,
            CleanupTaskType.STAGING_DELETE,
            staging_key=staging_key,
            next_attempt_at=next_attempt_at,
            deadline_at=deadline_at,
        )

    async def _create_task(
        self,
        job_id: str,
        owner_telegram_user_id: int,
        task_type: CleanupTaskType,
        *,
        telegram_chat_id: int | None = None,
        telegram_message_id: int | None = None,
        staging_key: str | None = None,
        next_attempt_at: str | None = None,
        deadline_at: str | None = None,
    ) -> ExportCleanupTask | None:
        self._validate_owner(owner_telegram_user_id)
        if task_type is CleanupTaskType.TELEGRAM_MESSAGE_DELETE and (
            telegram_chat_id is None or telegram_message_id is None
        ):
            raise ValueError("Telegram cleanup requires chat and message IDs")
        if task_type is CleanupTaskType.TELEGRAM_MESSAGE_DELETE:
            if (
                isinstance(telegram_chat_id, bool)
                or not isinstance(telegram_chat_id, int)
                or telegram_chat_id == 0
            ):
                raise ValueError("telegram_chat_id must be a non-zero integer")
            _validate_positive_identifier(telegram_message_id, "telegram_message_id")
        timestamp = _utc_now()
        task_id = str(uuid.uuid4())
        due_at = next_attempt_at or timestamp
        if not isinstance(due_at, str) or not due_at:
            raise ValueError("Cleanup next-attempt timestamp must be non-empty")
        if deadline_at is not None and (not isinstance(deadline_at, str) or not deadline_at):
            raise ValueError("Cleanup deadline must be a non-empty timestamp")
        async with self._connection() as connection:
            await connection.execute("BEGIN IMMEDIATE")
            try:
                if not await self._require_owned_job(connection, job_id, owner_telegram_user_id):
                    await connection.rollback()
                    return None
                await connection.execute(
                    """
                    INSERT INTO export_cleanup_tasks(
                        id, job_id, task_type, state, telegram_chat_id,
                        telegram_message_id, staging_key, next_attempt_at,
                        deadline_at, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task_id,
                        job_id,
                        task_type.value,
                        CleanupTaskState.PENDING.value,
                        telegram_chat_id,
                        telegram_message_id,
                        staging_key,
                        due_at,
                        deadline_at,
                        timestamp,
                        timestamp,
                    ),
                )
                async with connection.execute(
                    "SELECT * FROM export_cleanup_tasks WHERE id = ?", (task_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                await connection.commit()
            except Exception:
                await connection.rollback()
                raise
        return _cleanup_from_row(row) if row is not None else None

    async def list_due_tasks(self, now: str, *, limit: int = 100) -> tuple[ExportCleanupTask, ...]:
        """Return due pending tasks for an internal cleanup worker."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise ValueError("Cleanup task limit must be between 1 and 500")
        async with self._connection() as connection:
            async with connection.execute(
                """
                SELECT * FROM export_cleanup_tasks
                WHERE state = 'pending' AND next_attempt_at <= ?
                ORDER BY next_attempt_at, created_at LIMIT ?
                """,
                (now, limit),
            ) as cursor:
                rows = await cursor.fetchall()
        return tuple(_cleanup_from_row(row) for row in rows)

    async def get_task(self, task_id: str) -> ExportCleanupTask | None:
        """Read an internal cleanup task by its opaque identifier."""
        async with self._connection() as connection:
            async with connection.execute(
                "SELECT * FROM export_cleanup_tasks WHERE id = ?", (task_id,)
            ) as cursor:
                row = await cursor.fetchone()
        return _cleanup_from_row(row) if row is not None else None

    async def record_attempt(
        self,
        task_id: str,
        outcome: CleanupTaskState,
        *,
        next_attempt_at: str | None = None,
        error_code: str | None = None,
        updated_at: str | None = None,
    ) -> ExportCleanupTask | None:
        """Record one cleanup attempt and its retry/terminal result.

        Pending means retry; succeeded and abandoned are terminal. The schema
        retains the task even if its parent export job is later deleted.
        """
        target = CleanupTaskState(outcome)
        _validate_error_code(error_code)
        if target is CleanupTaskState.PENDING and not next_attempt_at:
            raise ValueError("A pending cleanup retry requires next_attempt_at")
        if target is not CleanupTaskState.PENDING and next_attempt_at is not None:
            raise ValueError("Terminal cleanup outcomes cannot schedule another retry")
        timestamp = updated_at or _utc_now()
        if not isinstance(timestamp, str) or not timestamp:
            raise ValueError("Cleanup update timestamp must be non-empty")
        if next_attempt_at is not None and (
            not isinstance(next_attempt_at, str) or not next_attempt_at
        ):
            raise ValueError("Cleanup next-attempt timestamp must be non-empty")
        async with self._connection() as connection:
            await connection.execute("BEGIN IMMEDIATE")
            try:
                result = await connection.execute(
                    """
                    UPDATE export_cleanup_tasks
                    SET state = ?, attempt_count = attempt_count + 1,
                        next_attempt_at = COALESCE(?, next_attempt_at),
                        last_error_code = ?, updated_at = ?
                    WHERE id = ? AND state = 'pending'
                    """,
                    (target.value, next_attempt_at, error_code, timestamp, task_id),
                )
                if result.rowcount != 1:
                    await connection.rollback()
                    return None
                async with connection.execute(
                    "SELECT * FROM export_cleanup_tasks WHERE id = ?", (task_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                await connection.commit()
            except Exception:
                await connection.rollback()
                raise
        if row is None:
            raise RuntimeError("Updated cleanup task could not be read back")
        return _cleanup_from_row(row)
