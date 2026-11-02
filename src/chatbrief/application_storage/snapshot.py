"""Authorization-aware, cutoff-bounded snapshots of the shared message archive."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import aiosqlite

from .migrations import ApplicationDatabase


class SnapshotError(RuntimeError):
    """Base class for a snapshot that cannot be safely constructed."""


class SnapshotUserNotFoundError(SnapshotError):
    """The requesting Chatbrief user is not registered."""


class SnapshotAuthorizationError(SnapshotError):
    """A selected private source is not currently authorized for the requester."""


class SnapshotStateChangedError(SnapshotError):
    """Current relationship state cannot prove the state at the fixed cutoff."""


@dataclass(frozen=True, slots=True)
class SnapshotSource:
    """Safe source metadata; no Telegram chat identifiers are exposed."""

    id: str
    platform: str
    display_name: str


@dataclass(frozen=True, slots=True)
class SnapshotMessage:
    """Exportable message fields, deliberately excluding sender and transport data."""

    id: str
    source_id: str
    text: str
    source_timestamp: str | None


@dataclass(frozen=True, slots=True)
class SnapshotCoverageGap:
    source_id: str
    missing_from: str
    missing_until: str


@dataclass(frozen=True, slots=True)
class SnapshotOmission:
    category: str
    reason_code: str
    count: int
    explanation: str


@dataclass(frozen=True, slots=True)
class ExportSnapshot:
    cutoff_at: str
    retention_start_at: str
    sources: tuple[SnapshotSource, ...]
    messages: tuple[SnapshotMessage, ...]
    coverage_gaps: tuple[SnapshotCoverageGap, ...]
    omissions: tuple[SnapshotOmission, ...]


def _timestamp(value: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field} must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat()


def _user_id(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("Telegram user ID must be a positive integer")


def _coverage_gaps(
    source_id: str,
    retention_start: datetime,
    cutoff: datetime,
    intervals: list[aiosqlite.Row],
) -> list[SnapshotCoverageGap]:
    """Return uncovered half-open intervals within the retained archive window."""
    gaps: list[SnapshotCoverageGap] = []
    cursor = retention_start

    for interval in intervals:
        start = datetime.fromisoformat(interval["covered_from"])
        end = datetime.fromisoformat(interval["covered_until"])
        if end <= retention_start or start >= cutoff:
            continue
        start = max(start, retention_start)
        end = min(end, cutoff)
        if start > cursor:
            gaps.append(
                SnapshotCoverageGap(source_id, cursor.isoformat(), start.isoformat())
            )
        if end > cursor:
            cursor = end
        if cursor >= cutoff:
            break

    if cursor < cutoff:
        gaps.append(
            SnapshotCoverageGap(source_id, cursor.isoformat(), cutoff.isoformat())
        )
    return gaps


class ExportSnapshotRepository:
    """Build one consistent, authorization-aware view of retained archive data.

    Active subscriptions are the source-selection boundary. Public visibility is
    sufficient for source authorization; private visibility requires an active
    explicit grant. Ongoing subscriptions require available central Bot API
    access; a user's Telethon session is never treated as a substitute.
    """

    def __init__(self, database: ApplicationDatabase) -> None:
        self._database = database

    async def create_snapshot(
        self,
        owner_telegram_user_id: int,
        cutoff_at: str,
        *,
        retention_start_at: str,
    ) -> ExportSnapshot:
        """Read all retained messages for active subscriptions up to the cutoff.

        `retention_start_at` is the lower boundary imposed by the archive's
        rolling-retention policy, not a user-selectable export lookback. The
        caller must calculate it from the configured retention policy.
        """
        _user_id(owner_telegram_user_id)
        cutoff_text = _timestamp(cutoff_at, "cutoff_at")
        retention_text = _timestamp(retention_start_at, "retention_start_at")
        cutoff = datetime.fromisoformat(cutoff_text)
        retention_start = datetime.fromisoformat(retention_text)
        if retention_start > cutoff:
            raise ValueError("retention_start_at must not be after cutoff_at")

        async with await self._database.connect() as connection:
            connection.row_factory = aiosqlite.Row
            await connection.execute("BEGIN")
            async with connection.execute(
                "SELECT 1 FROM users WHERE telegram_user_id = ?",
                (owner_telegram_user_id,),
            ) as cursor:
                user = await cursor.fetchone()
            if user is None:
                raise SnapshotUserNotFoundError("Requesting user is not registered")

            # Relationship rows have no history table. If an existing subscription
            # changed after the request cutoff, its state at that cutoff is unknown.
            async with connection.execute(
                """
                SELECT 1 FROM subscriptions
                WHERE telegram_user_id = ? AND created_at <= ? AND updated_at > ?
                LIMIT 1
                """,
                (owner_telegram_user_id, cutoff_text, cutoff_text),
            ) as cursor:
                changed_subscription = await cursor.fetchone()
            if changed_subscription is not None:
                raise SnapshotStateChangedError(
                    "A subscription changed after the export cutoff"
                )

            async with connection.execute(
                """
                SELECT
                    s.id, s.platform, s.display_name, s.visibility,
                    s.updated_at AS source_updated_at,
                    access.state AS bot_access_state,
                    access.verified_at AS bot_verified_at,
                    access.updated_at AS bot_access_updated_at,
                    auth.state AS authorization_state,
                    auth.granted_at AS authorization_granted_at
                FROM subscriptions AS sub
                JOIN sources AS s ON s.id = sub.source_id
                LEFT JOIN source_access AS access
                    ON access.source_id = s.id AND access.access_method = 'bot_api'
                LEFT JOIN source_authorizations AS auth
                    ON auth.source_id = s.id
                    AND auth.telegram_user_id = sub.telegram_user_id
                WHERE sub.telegram_user_id = ?
                  AND sub.state = 'active'
                  AND sub.created_at <= ?
                  AND sub.updated_at <= ?
                ORDER BY s.display_name COLLATE NOCASE, s.id
                """,
                (owner_telegram_user_id, cutoff_text, cutoff_text),
            ) as cursor:
                source_rows = await cursor.fetchall()

            sources: list[SnapshotSource] = []
            messages: list[SnapshotMessage] = []
            coverage_gaps: list[SnapshotCoverageGap] = []
            omission_counts: dict[tuple[str, str], int] = {}

            def omit(category: str, reason: str) -> None:
                key = (category, reason)
                omission_counts[key] = omission_counts.get(key, 0) + 1

            for row in source_rows:
                source_id = row["id"]
                visibility = row["visibility"]

                # A source metadata update after cutoff makes its historical
                # visibility unknowable because the schema has no change history.
                if row["source_updated_at"] > cutoff_text:
                    raise SnapshotStateChangedError(
                        "A subscribed source changed after the export cutoff"
                    )
                if visibility == "unknown":
                    omit("messages", "not_exportable")
                    continue
                if visibility == "private":
                    if (
                        row["authorization_state"] != "active"
                        or row["authorization_granted_at"] is None
                        or row["authorization_granted_at"] > cutoff_text
                    ):
                        raise SnapshotAuthorizationError(
                            "A private source is not authorized for this user"
                        )
                elif visibility != "public":
                    omit("messages", "not_exportable")
                    continue

                # Active subscriptions are only valid with central Bot API access.
                # Telethon is reserved for explicitly requested one-time backfills.
                if (
                    row["bot_access_state"] != "available"
                    or row["bot_verified_at"] is None
                    or row["bot_verified_at"] > cutoff_text
                    or row["bot_access_updated_at"] > cutoff_text
                ):
                    omit("messages", "unavailable")
                    continue

                sources.append(
                    SnapshotSource(
                        id=source_id,
                        platform=row["platform"],
                        display_name=row["display_name"],
                    )
                )

                async with connection.execute(
                    """
                    SELECT id, source_id, text, source_timestamp
                    FROM messages
                    WHERE source_id = ?
                      AND deleted_at IS NULL
                      AND COALESCE(source_timestamp, collected_at) >= ?
                      AND collected_at <= ?
                      AND (source_timestamp IS NULL OR source_timestamp <= ?)
                    ORDER BY
                        CASE WHEN source_timestamp IS NULL THEN 1 ELSE 0 END,
                        source_timestamp, collected_at, id
                    """,
                    (source_id, retention_text, cutoff_text, cutoff_text),
                ) as cursor:
                    message_rows = await cursor.fetchall()
                messages.extend(
                    SnapshotMessage(
                        id=message["id"],
                        source_id=message["source_id"],
                        text=message["text"],
                        source_timestamp=message["source_timestamp"],
                    )
                    for message in message_rows
                )

                async with connection.execute(
                    """
                    SELECT covered_from, covered_until
                    FROM source_collection_coverage
                    WHERE source_id = ? AND ingestion_method = 'bot_api'
                    ORDER BY covered_from
                    """,
                    (source_id,),
                ) as cursor:
                    coverage_rows = await cursor.fetchall()
                coverage_gaps.extend(
                    _coverage_gaps(
                        source_id, retention_start, cutoff, coverage_rows
                    )
                )

            if coverage_gaps:
                key = ("messages", "unavailable")
                omission_counts[key] = omission_counts.get(key, 0) + len(coverage_gaps)

            omissions = tuple(
                SnapshotOmission(
                    category=category,
                    reason_code=reason,
                    count=count,
                    explanation=(
                        "Some retained message history has no confirmed collection "
                        "coverage."
                        if reason == "unavailable"
                        else "A subscribed source could not be safely included."
                    ),
                )
                for (category, reason), count in sorted(omission_counts.items())
            )
            return ExportSnapshot(
                cutoff_at=cutoff_text,
                retention_start_at=retention_text,
                sources=tuple(sources),
                messages=tuple(messages),
                coverage_gaps=tuple(coverage_gaps),
                omissions=omissions,
            )
