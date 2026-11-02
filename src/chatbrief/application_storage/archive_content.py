"""Persistence for normalized archive messages and known-complete coverage."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import AsyncIterator

import aiosqlite

from .archive import _nonempty, _timestamp
from .migrations import ApplicationDatabase


class MessageMediaType(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    OTHER = "other"
    UNKNOWN = "unknown"


class CollectionMethod(StrEnum):
    BOT_API = "bot_api"
    TELETHON = "telethon"


@dataclass(frozen=True, slots=True)
class ArchiveMessage:
    id: str
    source_id: str
    platform_message_id: str
    text: str
    sender_label: str | None
    source_timestamp: str | None
    link: str | None
    has_media: bool
    media_type: MessageMediaType | None
    collected_at: str
    edited_at: str | None
    deleted_at: str | None


@dataclass(frozen=True, slots=True)
class CollectionCoverage:
    id: str
    source_id: str
    ingestion_method: CollectionMethod
    covered_from: str
    covered_until: str
    recorded_at: str


def _message(row: aiosqlite.Row) -> ArchiveMessage:
    return ArchiveMessage(
        row["id"], row["source_id"], row["platform_message_id"], row["text"],
        row["sender_label"], row["source_timestamp"], row["link"],
        bool(row["has_media"]),
        MessageMediaType(row["media_type"]) if row["media_type"] is not None else None,
        row["collected_at"], row["edited_at"], row["deleted_at"],
    )


def _coverage(row: aiosqlite.Row) -> CollectionCoverage:
    return CollectionCoverage(
        row["id"], row["source_id"], CollectionMethod(row["ingestion_method"]),
        row["covered_from"], row["covered_until"], row["recorded_at"],
    )


def _optional_text(value: str | None, field: str) -> None:
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{field} must be a string or None")


def _interval(value: str, field: str) -> datetime:
    normalized = _timestamp(value, field)
    return datetime.fromisoformat(normalized)


class ArchiveContentRepository:
    """Store source messages and only explicitly established coverage intervals."""

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

    async def upsert_message(
        self,
        source_id: str,
        platform_message_id: str,
        text: str,
        *,
        collected_at: str,
        sender_label: str | None = None,
        source_timestamp: str | None = None,
        link: str | None = None,
        has_media: bool = False,
        media_type: MessageMediaType | None = None,
        edited_at: str | None = None,
    ) -> ArchiveMessage:
        _nonempty(source_id, "source_id")
        _nonempty(platform_message_id, "platform_message_id")
        if not isinstance(text, str):
            raise ValueError("text must be a string")
        _optional_text(sender_label, "sender_label")
        _optional_text(link, "link")
        if not isinstance(has_media, bool):
            raise ValueError("has_media must be a boolean")
        kind = MessageMediaType(media_type) if media_type is not None else None
        if has_media != (kind is not None):
            raise ValueError("has_media and media_type must be supplied consistently")
        collected = _timestamp(collected_at, "collected_at")
        source_time = (
            _timestamp(source_timestamp, "source_timestamp")
            if source_timestamp is not None
            else None
        )
        edited = _timestamp(edited_at, "edited_at") if edited_at is not None else None
        identifier = str(uuid.uuid4())

        async with self._connection() as connection:
            await connection.execute(
                """
                INSERT INTO messages(
                    id, source_id, platform_message_id, text, sender_label,
                    source_timestamp, link, has_media, media_type, collected_at, edited_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, platform_message_id) DO UPDATE SET
                    text = excluded.text,
                    sender_label = excluded.sender_label,
                    source_timestamp = excluded.source_timestamp,
                    link = excluded.link,
                    has_media = excluded.has_media,
                    media_type = excluded.media_type,
                    edited_at = excluded.edited_at
                """,
                (
                    identifier, source_id, platform_message_id, text, sender_label,
                    source_time, link, int(has_media), kind.value if kind else None,
                    collected, edited,
                ),
            )
            async with connection.execute(
                "SELECT * FROM messages WHERE source_id = ? AND platform_message_id = ?",
                (source_id, platform_message_id),
            ) as cursor:
                row = await cursor.fetchone()
        if row is None:
            raise RuntimeError("Message could not be read after upsert")
        return _message(row)

    async def get_message(
        self, source_id: str, platform_message_id: str
    ) -> ArchiveMessage | None:
        _nonempty(source_id, "source_id")
        _nonempty(platform_message_id, "platform_message_id")
        async with self._connection() as connection:
            async with connection.execute(
                """
                SELECT * FROM messages
                WHERE source_id = ? AND platform_message_id = ?
                """,
                (source_id, platform_message_id),
            ) as cursor:
                row = await cursor.fetchone()
        return _message(row) if row is not None else None

    async def mark_message_deleted(
        self,
        source_id: str,
        platform_message_id: str,
        *,
        deleted_at: str,
    ) -> ArchiveMessage | None:
        _nonempty(source_id, "source_id")
        _nonempty(platform_message_id, "platform_message_id")
        timestamp = _timestamp(deleted_at, "deleted_at")
        async with self._connection() as connection:
            await connection.execute(
                """
                UPDATE messages SET deleted_at = COALESCE(deleted_at, ?)
                WHERE source_id = ? AND platform_message_id = ?
                """,
                (timestamp, source_id, platform_message_id),
            )
            async with connection.execute(
                """
                SELECT * FROM messages
                WHERE source_id = ? AND platform_message_id = ?
                """,
                (source_id, platform_message_id),
            ) as cursor:
                row = await cursor.fetchone()
        return _message(row) if row is not None else None

    async def record_coverage(
        self,
        source_id: str,
        ingestion_method: CollectionMethod,
        covered_from: str,
        covered_until: str,
        *,
        recorded_at: str | None = None,
    ) -> tuple[CollectionCoverage, ...]:
        """Insert or coalesce overlapping/adjacent intervals for one source/method.

        Callers are responsible for recording an interval only after establishing
        that every item in it was collected. Message presence alone is not proof.
        """
        _nonempty(source_id, "source_id")
        method = CollectionMethod(ingestion_method)
        start, end = _interval(covered_from, "covered_from"), _interval(
            covered_until, "covered_until"
        )
        if end < start:
            raise ValueError("covered_until must not precede covered_from")
        recorded = _timestamp(recorded_at, "recorded_at")
        async with self._connection() as connection:
            await connection.execute("BEGIN IMMEDIATE")
            try:
                async with connection.execute(
                    """
                    SELECT * FROM source_collection_coverage
                    WHERE source_id = ? AND ingestion_method = ?
                    ORDER BY covered_from
                    """,
                    (source_id, method.value),
                ) as cursor:
                    rows = await cursor.fetchall()

                merge_start, merge_end = start, end
                merged_ids: list[str] = []
                changed = True
                while changed:
                    changed = False
                    for row in rows:
                        if row["id"] in merged_ids:
                            continue
                        row_start = datetime.fromisoformat(row["covered_from"])
                        row_end = datetime.fromisoformat(row["covered_until"])
                        if (
                            row_start <= merge_end + timedelta(microseconds=1)
                            and row_end >= merge_start - timedelta(microseconds=1)
                        ):
                            merge_start = min(merge_start, row_start)
                            merge_end = max(merge_end, row_end)
                            merged_ids.append(row["id"])
                            changed = True

                if merged_ids:
                    keep_id = merged_ids[0]
                    placeholders = ",".join("?" for _ in merged_ids)
                    await connection.execute(
                        f"DELETE FROM source_collection_coverage WHERE id IN ({placeholders})",
                        tuple(merged_ids),
                    )
                else:
                    keep_id = str(uuid.uuid4())

                await connection.execute(
                    """
                    INSERT INTO source_collection_coverage(
                        id, source_id, ingestion_method, covered_from,
                        covered_until, recorded_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        keep_id, source_id, method.value, merge_start.isoformat(),
                        merge_end.isoformat(), recorded,
                    ),
                )
                async with connection.execute(
                    """
                    SELECT * FROM source_collection_coverage
                    WHERE source_id = ? AND ingestion_method = ?
                    ORDER BY covered_from
                    """,
                    (source_id, method.value),
                ) as cursor:
                    result_rows = await cursor.fetchall()
                await connection.commit()
            except Exception:
                await connection.rollback()
                raise
        return tuple(_coverage(row) for row in result_rows)

    async def list_coverage(
        self, source_id: str, ingestion_method: CollectionMethod | None = None
    ) -> tuple[CollectionCoverage, ...]:
        _nonempty(source_id, "source_id")
        query = "SELECT * FROM source_collection_coverage WHERE source_id = ?"
        parameters: tuple[object, ...] = (source_id,)
        if ingestion_method is not None:
            query += " AND ingestion_method = ?"
            parameters += (CollectionMethod(ingestion_method).value,)
        query += " ORDER BY ingestion_method, covered_from"
        async with self._connection() as connection:
            async with connection.execute(query, parameters) as cursor:
                rows = await cursor.fetchall()
        return tuple(_coverage(row) for row in rows)
