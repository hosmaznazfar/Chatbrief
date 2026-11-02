"""Typed persistence for shared archive identities and source relationships."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import AsyncIterator

import aiosqlite

from .migrations import ApplicationDatabase


class SourceType(StrEnum):
    CHANNEL = "channel"
    GROUP = "group"
    SUPERGROUP = "supergroup"


class SourceVisibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    UNKNOWN = "unknown"


class AccessMethod(StrEnum):
    BOT_API = "bot_api"
    TELETHON = "telethon"


class AccessState(StrEnum):
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    INACCESSIBLE = "inaccessible"
    REVOKED = "revoked"


class AuthorizationState(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"


class SubscriptionState(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ENDED = "ended"


@dataclass(frozen=True, slots=True)
class ArchiveUser:
    telegram_user_id: int
    created_at: str


@dataclass(frozen=True, slots=True)
class ArchiveSource:
    id: str
    platform: str
    platform_chat_id: str
    display_name: str
    source_type: SourceType
    visibility: SourceVisibility
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class SourceAccess:
    id: str
    source_id: str
    access_method: AccessMethod
    owner_telegram_user_id: int | None
    state: AccessState
    verified_at: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class SourceAuthorization:
    source_id: str
    telegram_user_id: int
    granted_by_telegram_user_id: int | None
    state: AuthorizationState
    granted_at: str
    revoked_at: str | None


@dataclass(frozen=True, slots=True)
class ArchiveSubscription:
    id: str
    telegram_user_id: int
    source_id: str
    state: SubscriptionState
    created_at: str
    updated_at: str
    ended_at: str | None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _timestamp(value: str | None, field: str) -> str:
    result = value if value is not None else _now()
    if not isinstance(result, str) or not result:
        raise ValueError(f"{field} must be a non-empty timestamp")
    try:
        parsed = datetime.fromisoformat(result.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field} must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc).isoformat()


def _user_id(value: int, field: str = "Telegram user ID") -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")


def _nonempty(value: str, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty string")


def _user(row: aiosqlite.Row) -> ArchiveUser:
    return ArchiveUser(row["telegram_user_id"], row["created_at"])


def _source(row: aiosqlite.Row) -> ArchiveSource:
    return ArchiveSource(
        row["id"], row["platform"], row["platform_chat_id"], row["display_name"],
        SourceType(row["source_type"]), SourceVisibility(row["visibility"]),
        row["created_at"], row["updated_at"],
    )


def _access(row: aiosqlite.Row) -> SourceAccess:
    return SourceAccess(
        row["id"], row["source_id"], AccessMethod(row["access_method"]),
        row["owner_telegram_user_id"], AccessState(row["state"]), row["verified_at"],
        row["created_at"], row["updated_at"],
    )


def _authorization(row: aiosqlite.Row) -> SourceAuthorization:
    return SourceAuthorization(
        row["source_id"], row["telegram_user_id"], row["granted_by_telegram_user_id"],
        AuthorizationState(row["state"]), row["granted_at"], row["revoked_at"],
    )


def _subscription(row: aiosqlite.Row) -> ArchiveSubscription:
    return ArchiveSubscription(
        row["id"], row["telegram_user_id"], row["source_id"],
        SubscriptionState(row["state"]), row["created_at"], row["updated_at"],
        row["ended_at"],
    )


class ArchiveRepository:
    """Persist identity and source relationships in the required application DB.

    These methods deliberately do not equate subscriptions with authorization
    or technical access. Export eligibility is evaluated by a separate,
    authorization-aware snapshot operation.
    """

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

    async def ensure_user(
        self, telegram_user_id: int, *, created_at: str | None = None
    ) -> ArchiveUser:
        _user_id(telegram_user_id)
        timestamp = _timestamp(created_at, "created_at")
        async with self._connection() as connection:
            await connection.execute(
                "INSERT INTO users(telegram_user_id, created_at) VALUES (?, ?) "
                "ON CONFLICT(telegram_user_id) DO NOTHING",
                (telegram_user_id, timestamp),
            )
            async with connection.execute(
                "SELECT * FROM users WHERE telegram_user_id = ?", (telegram_user_id,)
            ) as cursor:
                row = await cursor.fetchone()
        if row is None:
            raise RuntimeError("User could not be read after insertion")
        return _user(row)

    async def get_user(self, telegram_user_id: int) -> ArchiveUser | None:
        _user_id(telegram_user_id)
        async with self._connection() as connection:
            async with connection.execute(
                "SELECT * FROM users WHERE telegram_user_id = ?", (telegram_user_id,)
            ) as cursor:
                row = await cursor.fetchone()
        return _user(row) if row is not None else None

    async def upsert_source(
        self,
        platform_chat_id: str,
        display_name: str,
        source_type: SourceType,
        visibility: SourceVisibility,
        *,
        source_id: str | None = None,
        platform: str = "telegram",
        updated_at: str | None = None,
    ) -> ArchiveSource:
        _nonempty(platform_chat_id, "platform_chat_id")
        _nonempty(display_name, "display_name")
        if platform != "telegram":
            raise ValueError("Only the Telegram source platform is currently supported")
        kind = SourceType(source_type)
        visible = SourceVisibility(visibility)
        timestamp = _timestamp(updated_at, "updated_at")
        identifier = source_id or str(uuid.uuid4())
        _nonempty(identifier, "source_id")
        async with self._connection() as connection:
            await connection.execute("BEGIN IMMEDIATE")
            try:
                async with connection.execute(
                    "SELECT id, created_at FROM sources "
                    "WHERE platform = ? AND platform_chat_id = ?",
                    (platform, platform_chat_id),
                ) as cursor:
                    existing = await cursor.fetchone()
                if existing is None:
                    await connection.execute(
                        """
                        INSERT INTO sources(
                            id, platform, platform_chat_id, display_name, source_type,
                            visibility, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (identifier, platform, platform_chat_id, display_name,
                         kind.value, visible.value, timestamp, timestamp),
                    )
                    identifier_to_read = identifier
                else:
                    identifier_to_read = existing["id"]
                    if source_id is not None and source_id != identifier_to_read:
                        raise ValueError("Source identity cannot be replaced")
                    await connection.execute(
                        """
                        UPDATE sources SET display_name = ?, source_type = ?,
                            visibility = ?, updated_at = ?
                        WHERE id = ?
                        """,
                        (display_name, kind.value, visible.value, timestamp, identifier_to_read),
                    )
                async with connection.execute(
                    "SELECT * FROM sources WHERE id = ?", (identifier_to_read,)
                ) as cursor:
                    row = await cursor.fetchone()
                await connection.commit()
            except Exception:
                await connection.rollback()
                raise
        if row is None:
            raise RuntimeError("Source could not be read after upsert")
        return _source(row)

    async def get_source(self, source_id: str) -> ArchiveSource | None:
        _nonempty(source_id, "source_id")
        async with self._connection() as connection:
            async with connection.execute(
                "SELECT * FROM sources WHERE id = ?", (source_id,)
            ) as cursor:
                row = await cursor.fetchone()
        return _source(row) if row is not None else None

    async def set_access(
        self,
        source_id: str,
        access_method: AccessMethod,
        state: AccessState,
        *,
        owner_telegram_user_id: int | None = None,
        verified_at: str | None = None,
        updated_at: str | None = None,
    ) -> SourceAccess:
        _nonempty(source_id, "source_id")
        method, status = AccessMethod(access_method), AccessState(state)
        if method is AccessMethod.BOT_API and owner_telegram_user_id is not None:
            raise ValueError("Bot API access must not have a user owner")
        if method is AccessMethod.TELETHON:
            if owner_telegram_user_id is None:
                raise ValueError("Telethon access requires its owning user")
            _user_id(owner_telegram_user_id)
        timestamp = _timestamp(updated_at, "updated_at")
        verified = _timestamp(verified_at, "verified_at") if verified_at is not None else None
        async with self._connection() as connection:
            await connection.execute("BEGIN IMMEDIATE")
            try:
                async with connection.execute(
                    """
                    SELECT * FROM source_access
                    WHERE source_id = ? AND access_method = ?
                      AND owner_telegram_user_id IS ?
                    """,
                    (source_id, method.value, owner_telegram_user_id),
                ) as cursor:
                    existing = await cursor.fetchone()
                if existing is None:
                    access_id = str(uuid.uuid4())
                    await connection.execute(
                        """
                        INSERT INTO source_access(
                            id, source_id, access_method, owner_telegram_user_id,
                            state, verified_at, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (access_id, source_id, method.value, owner_telegram_user_id,
                         status.value, verified, timestamp, timestamp),
                    )
                else:
                    access_id = existing["id"]
                    await connection.execute(
                        """
                        UPDATE source_access SET state = ?, verified_at = COALESCE(?, verified_at),
                            updated_at = ?
                        WHERE id = ?
                        """,
                        (status.value, verified, timestamp, access_id),
                    )
                async with connection.execute(
                    "SELECT * FROM source_access WHERE id = ?", (access_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                await connection.commit()
            except Exception:
                await connection.rollback()
                raise
        if row is None:
            raise RuntimeError("Source access could not be read after upsert")
        return _access(row)

    async def set_authorization(
        self,
        source_id: str,
        telegram_user_id: int,
        state: AuthorizationState,
        *,
        granted_by_telegram_user_id: int | None = None,
        changed_at: str | None = None,
    ) -> SourceAuthorization:
        _nonempty(source_id, "source_id")
        _user_id(telegram_user_id)
        if granted_by_telegram_user_id is not None:
            _user_id(granted_by_telegram_user_id, "Grantor Telegram user ID")
        status = AuthorizationState(state)
        timestamp = _timestamp(changed_at, "changed_at")
        revoked_at = timestamp if status is AuthorizationState.REVOKED else None
        async with self._connection() as connection:
            await connection.execute("BEGIN IMMEDIATE")
            try:
                async with connection.execute(
                    "SELECT * FROM source_authorizations "
                    "WHERE source_id = ? AND telegram_user_id = ?",
                    (source_id, telegram_user_id),
                ) as cursor:
                    existing = await cursor.fetchone()
                if existing is None:
                    if status is AuthorizationState.REVOKED:
                        raise ValueError("Cannot revoke an authorization that does not exist")
                    await connection.execute(
                        """
                        INSERT INTO source_authorizations(
                            source_id, telegram_user_id, granted_by_telegram_user_id,
                            state, granted_at, revoked_at
                        ) VALUES (?, ?, ?, ?, ?, NULL)
                        """,
                        (
                            source_id,
                            telegram_user_id,
                            granted_by_telegram_user_id,
                            status.value,
                            timestamp,
                        ),
                    )
                else:
                    await connection.execute(
                        """
                        UPDATE source_authorizations
                        SET granted_by_telegram_user_id = CASE
                                WHEN ? = 'active' THEN ?
                                ELSE granted_by_telegram_user_id
                            END,
                            state = ?,
                            granted_at = CASE WHEN ? = 'active' THEN ? ELSE granted_at END,
                            revoked_at = ?
                        WHERE source_id = ? AND telegram_user_id = ?
                        """,
                        (
                            status.value,
                            granted_by_telegram_user_id,
                            status.value,
                            status.value,
                            timestamp,
                            revoked_at,
                            source_id,
                            telegram_user_id,
                        ),
                    )
                async with connection.execute(
                    """
                    SELECT * FROM source_authorizations
                    WHERE source_id = ? AND telegram_user_id = ?
                    """,
                    (source_id, telegram_user_id),
                ) as cursor:
                    row = await cursor.fetchone()
                await connection.commit()
            except Exception:
                await connection.rollback()
                raise
        if row is None:
            raise RuntimeError("Source authorization could not be read after update")
        return _authorization(row)

    async def get_authorization(
        self, source_id: str, telegram_user_id: int
    ) -> SourceAuthorization | None:
        _nonempty(source_id, "source_id")
        _user_id(telegram_user_id)
        async with self._connection() as connection:
            async with connection.execute(
                """
                SELECT * FROM source_authorizations
                WHERE source_id = ? AND telegram_user_id = ?
                """,
                (source_id, telegram_user_id),
            ) as cursor:
                row = await cursor.fetchone()
        return _authorization(row) if row is not None else None

    async def upsert_subscription(
        self,
        telegram_user_id: int,
        source_id: str,
        state: SubscriptionState,
        *,
        changed_at: str | None = None,
    ) -> ArchiveSubscription:
        _user_id(telegram_user_id)
        _nonempty(source_id, "source_id")
        status = SubscriptionState(state)
        timestamp = _timestamp(changed_at, "changed_at")
        ended_at = timestamp if status is SubscriptionState.ENDED else None
        async with self._connection() as connection:
            await connection.execute("BEGIN IMMEDIATE")
            try:
                async with connection.execute(
                    "SELECT id FROM subscriptions WHERE telegram_user_id = ? AND source_id = ?",
                    (telegram_user_id, source_id),
                ) as cursor:
                    existing = await cursor.fetchone()
                if existing is None:
                    subscription_id = str(uuid.uuid4())
                    await connection.execute(
                        """
                        INSERT INTO subscriptions(
                            id, telegram_user_id, source_id, state,
                            created_at, updated_at, ended_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (subscription_id, telegram_user_id, source_id, status.value,
                         timestamp, timestamp, ended_at),
                    )
                else:
                    subscription_id = existing["id"]
                    await connection.execute(
                        """
                        UPDATE subscriptions SET state = ?, updated_at = ?, ended_at = ?
                        WHERE id = ?
                        """,
                        (status.value, timestamp, ended_at, subscription_id),
                    )
                async with connection.execute(
                    "SELECT * FROM subscriptions WHERE id = ?", (subscription_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                await connection.commit()
            except Exception:
                await connection.rollback()
                raise
        if row is None:
            raise RuntimeError("Subscription could not be read after upsert")
        return _subscription(row)

    async def get_subscription(
        self, telegram_user_id: int, source_id: str
    ) -> ArchiveSubscription | None:
        _user_id(telegram_user_id)
        _nonempty(source_id, "source_id")
        async with self._connection() as connection:
            async with connection.execute(
                "SELECT * FROM subscriptions WHERE telegram_user_id = ? AND source_id = ?",
                (telegram_user_id, source_id),
            ) as cursor:
                row = await cursor.fetchone()
        return _subscription(row) if row is not None else None
