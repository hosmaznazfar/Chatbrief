"""Tests for shared archive identity and source-relationship repositories."""

import aiosqlite
import pytest
import pytest_asyncio

from chatbrief.application_storage import ApplicationDatabase
from chatbrief.application_storage.archive import (
    AccessMethod,
    AccessState,
    ArchiveRepository,
    AuthorizationState,
    SourceType,
    SourceVisibility,
    SubscriptionState,
)


@pytest_asyncio.fixture
async def archive_repository(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()
    return ArchiveRepository(database)


@pytest.mark.asyncio
async def test_user_identity_stores_only_telegram_id_and_is_idempotent(archive_repository):
    first = await archive_repository.ensure_user(
        1234, created_at="2026-11-02T01:00:00Z"
    )
    second = await archive_repository.ensure_user(
        1234, created_at="2026-11-03T01:00:00Z"
    )

    assert first == second
    assert first.telegram_user_id == 1234
    assert first.created_at == "2026-11-02T01:00:00+00:00"
    assert await archive_repository.get_user(9999) is None

    with pytest.raises(ValueError, match="positive integer"):
        await archive_repository.ensure_user(True)


@pytest.mark.asyncio
async def test_source_upsert_preserves_identity_and_original_creation_time(archive_repository):
    first = await archive_repository.upsert_source(
        "-100123",
        "Example channel",
        SourceType.CHANNEL,
        SourceVisibility.PUBLIC,
        source_id="source-stable",
        updated_at="2026-11-02T01:00:00Z",
    )
    updated = await archive_repository.upsert_source(
        "-100123",
        "Renamed channel",
        SourceType.SUPERGROUP,
        SourceVisibility.PRIVATE,
        updated_at="2026-11-02T02:00:00Z",
    )

    assert updated.id == first.id
    assert updated.created_at == first.created_at
    assert updated.display_name == "Renamed channel"
    assert updated.source_type is SourceType.SUPERGROUP
    assert updated.visibility is SourceVisibility.PRIVATE
    assert await archive_repository.get_source(first.id) == updated

    with pytest.raises(ValueError, match="identity cannot be replaced"):
        await archive_repository.upsert_source(
            "-100123",
            "Changed identity",
            SourceType.CHANNEL,
            SourceVisibility.PUBLIC,
            source_id="different-id",
        )


@pytest.mark.asyncio
async def test_access_records_keep_bot_api_shared_and_telethon_user_scoped(
    archive_repository,
):
    await archive_repository.ensure_user(1001)
    await archive_repository.ensure_user(1002)
    source = await archive_repository.upsert_source(
        "-100123",
        "Private channel",
        SourceType.CHANNEL,
        SourceVisibility.PRIVATE,
    )

    bot_access = await archive_repository.set_access(
        source.id, AccessMethod.BOT_API, AccessState.AVAILABLE
    )
    user_access = await archive_repository.set_access(
        source.id,
        AccessMethod.TELETHON,
        AccessState.AVAILABLE,
        owner_telegram_user_id=1001,
        verified_at="2026-11-02T01:00:00Z",
    )
    changed = await archive_repository.set_access(
        source.id,
        AccessMethod.TELETHON,
        AccessState.REVOKED,
        owner_telegram_user_id=1001,
    )

    assert bot_access.owner_telegram_user_id is None
    assert user_access.owner_telegram_user_id == 1001
    assert changed.id == user_access.id
    assert changed.state is AccessState.REVOKED
    assert changed.verified_at == user_access.verified_at
    assert await archive_repository.set_access(
        source.id,
        AccessMethod.TELETHON,
        AccessState.UNKNOWN,
        owner_telegram_user_id=1002,
    ) != changed

    with pytest.raises(ValueError, match="requires its owning user"):
        await archive_repository.set_access(
            source.id, AccessMethod.TELETHON, AccessState.AVAILABLE
        )
    with pytest.raises(ValueError, match="must not have a user owner"):
        await archive_repository.set_access(
            source.id,
            AccessMethod.BOT_API,
            AccessState.AVAILABLE,
            owner_telegram_user_id=1001,
        )


@pytest.mark.asyncio
async def test_authorization_is_explicit_and_revocation_is_persisted(archive_repository):
    await archive_repository.ensure_user(1001)
    await archive_repository.ensure_user(2002)
    source = await archive_repository.upsert_source(
        "-100123",
        "Private channel",
        SourceType.CHANNEL,
        SourceVisibility.PRIVATE,
    )

    grant = await archive_repository.set_authorization(
        source.id,
        1001,
        AuthorizationState.ACTIVE,
        granted_by_telegram_user_id=2002,
        changed_at="2026-11-02T01:00:00Z",
    )
    revoked = await archive_repository.set_authorization(
        source.id,
        1001,
        AuthorizationState.REVOKED,
        granted_by_telegram_user_id=2002,
        changed_at="2026-11-02T02:00:00Z",
    )

    assert grant.state is AuthorizationState.ACTIVE
    assert grant.revoked_at is None
    assert revoked.state is AuthorizationState.REVOKED
    assert revoked.granted_at == grant.granted_at
    assert revoked.granted_by_telegram_user_id == grant.granted_by_telegram_user_id
    assert revoked.revoked_at == "2026-11-02T02:00:00+00:00"
    assert await archive_repository.get_authorization(source.id, 1001) == revoked
    assert await archive_repository.get_authorization(source.id, 2002) is None

    with pytest.raises(ValueError, match="does not exist"):
        await archive_repository.set_authorization(
            source.id, 2002, AuthorizationState.REVOKED
        )


@pytest.mark.asyncio
async def test_subscription_does_not_create_or_imply_authorization(archive_repository):
    await archive_repository.ensure_user(1001)
    source = await archive_repository.upsert_source(
        "-100123",
        "Private channel",
        SourceType.CHANNEL,
        SourceVisibility.PRIVATE,
    )

    subscription = await archive_repository.upsert_subscription(
        1001,
        source.id,
        SubscriptionState.ACTIVE,
        changed_at="2026-11-02T01:00:00Z",
    )

    assert subscription.state is SubscriptionState.ACTIVE
    assert await archive_repository.get_subscription(1001, source.id) == subscription
    assert await archive_repository.get_authorization(source.id, 1001) is None

    suspended = await archive_repository.upsert_subscription(
        1001, source.id, SubscriptionState.SUSPENDED
    )
    ended = await archive_repository.upsert_subscription(
        1001, source.id, SubscriptionState.ENDED
    )
    assert suspended.id == subscription.id
    assert suspended.ended_at is None
    assert ended.id == subscription.id
    assert ended.ended_at is not None
    assert await archive_repository.get_authorization(source.id, 1001) is None


@pytest.mark.asyncio
async def test_foreign_keys_reject_unknown_users_and_sources(archive_repository):
    with pytest.raises(aiosqlite.IntegrityError):
        await archive_repository.set_access(
            "missing-source",
            AccessMethod.BOT_API,
            AccessState.AVAILABLE,
        )

    with pytest.raises(aiosqlite.IntegrityError):
        await archive_repository.set_authorization(
            "missing-source", 9999, AuthorizationState.ACTIVE
        )

    with pytest.raises(Exception):
        await archive_repository.upsert_subscription(
            9999, "missing-source", SubscriptionState.ACTIVE
        )
