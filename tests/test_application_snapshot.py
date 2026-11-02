"""Tests for authorization-aware, cutoff-bounded export snapshots."""

import pytest
import pytest_asyncio

from chatbrief.application_storage import (
    AccessMethod,
    AccessState,
    ApplicationDatabase,
    ArchiveContentRepository,
    ArchiveRepository,
    AuthorizationState,
    CollectionMethod,
    ExportSnapshotRepository,
    MessageMediaType,
    SnapshotAuthorizationError,
    SnapshotStateChangedError,
    SnapshotUserNotFoundError,
    SourceType,
    SourceVisibility,
    SubscriptionState,
)


CUTOFF = "2026-11-02T12:00:00Z"
RETENTION_START = "2026-10-19T12:00:00Z"
BEFORE_CUTOFF = "2026-11-01T12:00:00Z"


@pytest_asyncio.fixture
async def snapshot_context(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()
    archive = ArchiveRepository(database)
    content = ArchiveContentRepository(database)
    await archive.ensure_user(100)
    await archive.ensure_user(200)
    return database, archive, content, ExportSnapshotRepository(database)


async def add_source(
    archive,
    *,
    chat_id="-100100",
    visibility=SourceVisibility.PUBLIC,
    owner=100,
    access_state=AccessState.AVAILABLE,
    access_method=AccessMethod.BOT_API,
):
    source = await archive.upsert_source(
        chat_id,
        "Example source",
        SourceType.CHANNEL,
        visibility,
        updated_at=BEFORE_CUTOFF,
    )
    await archive.set_access(
        source.id,
        access_method,
        access_state,
        owner_telegram_user_id=owner if access_method is AccessMethod.TELETHON else None,
        verified_at=BEFORE_CUTOFF if access_state is AccessState.AVAILABLE else None,
        updated_at=BEFORE_CUTOFF,
    )
    await archive.upsert_subscription(
        100, source.id, SubscriptionState.ACTIVE, changed_at=BEFORE_CUTOFF
    )
    return source


@pytest.mark.asyncio
async def test_snapshot_includes_only_retained_non_deleted_messages_before_cutoff(
    snapshot_context,
):
    _, archive, content, snapshots = snapshot_context
    source = await add_source(archive)

    included = await content.upsert_message(
        source.id,
        "telegram-1",
        "Retained body",
        collected_at="2026-10-20T10:00:00Z",
        source_timestamp="2026-10-20T09:00:00Z",
        sender_label="Private sender name",
        link="https://t.me/private/1",
    )
    await content.upsert_message(
        source.id,
        "telegram-2",
        "Arrived after cutoff",
        collected_at="2026-11-02T12:01:00Z",
    )
    await content.upsert_message(
        source.id,
        "telegram-3",
        "Future source timestamp",
        collected_at="2026-11-02T11:00:00Z",
        source_timestamp="2026-11-02T12:01:00Z",
    )
    deleted = await content.upsert_message(
        source.id,
        "telegram-4",
        "Deleted body",
        collected_at="2026-10-21T10:00:00Z",
    )
    await content.mark_message_deleted(
        source.id, "telegram-4", deleted_at="2026-10-22T10:00:00Z"
    )
    await content.record_coverage(
        source.id,
        CollectionMethod.BOT_API,
        RETENTION_START,
        CUTOFF,
    )

    snapshot = await snapshots.create_snapshot(
        100, CUTOFF, retention_start_at=RETENTION_START
    )

    assert [message.id for message in snapshot.messages] == [included.id]
    assert snapshot.messages[0].text == "Retained body"
    assert not hasattr(snapshot.messages[0], "sender_label")
    assert not hasattr(snapshot.messages[0], "link")
    assert not hasattr(snapshot.messages[0], "platform_message_id")
    assert snapshot.sources[0].id == source.id
    assert not hasattr(snapshot.sources[0], "platform_chat_id")
    assert snapshot.coverage_gaps == ()
    assert snapshot.omissions == ()
    assert deleted.id != included.id


@pytest.mark.asyncio
async def test_private_source_requires_active_explicit_grant(snapshot_context):
    _, archive, _, snapshots = snapshot_context
    source = await add_source(archive, visibility=SourceVisibility.PRIVATE)

    with pytest.raises(SnapshotAuthorizationError):
        await snapshots.create_snapshot(
            100, CUTOFF, retention_start_at=RETENTION_START
        )

    await archive.set_authorization(
        source.id,
        100,
        AuthorizationState.ACTIVE,
        granted_by_telegram_user_id=100,
        changed_at=BEFORE_CUTOFF,
    )
    snapshot = await snapshots.create_snapshot(
        100, CUTOFF, retention_start_at=RETENTION_START
    )
    assert [item.id for item in snapshot.sources] == [source.id]

    await archive.set_authorization(
        source.id,
        100,
        AuthorizationState.REVOKED,
        changed_at="2026-11-02T11:00:00Z",
    )
    with pytest.raises(SnapshotAuthorizationError):
        await snapshots.create_snapshot(
            100, CUTOFF, retention_start_at=RETENTION_START
        )


@pytest.mark.asyncio
async def test_private_grant_created_after_cutoff_does_not_authorize_snapshot(
    snapshot_context,
):
    _, archive, _, snapshots = snapshot_context
    source = await add_source(archive, visibility=SourceVisibility.PRIVATE)
    await archive.set_authorization(
        source.id,
        100,
        AuthorizationState.ACTIVE,
        granted_by_telegram_user_id=100,
        changed_at="2026-11-02T12:01:00Z",
    )

    with pytest.raises(SnapshotAuthorizationError):
        await snapshots.create_snapshot(
            100, CUTOFF, retention_start_at=RETENTION_START
        )


@pytest.mark.asyncio
async def test_unknown_visibility_is_excluded_and_reported(snapshot_context):
    _, archive, content, snapshots = snapshot_context
    source = await add_source(archive, visibility=SourceVisibility.UNKNOWN)
    await content.upsert_message(
        source.id, "1", "Must not leak", collected_at="2026-10-20T10:00:00Z"
    )

    snapshot = await snapshots.create_snapshot(
        100, CUTOFF, retention_start_at=RETENTION_START
    )

    assert snapshot.sources == ()
    assert snapshot.messages == ()
    assert [(item.category, item.reason_code, item.count) for item in snapshot.omissions] == [
        ("messages", "not_exportable", 1)
    ]


@pytest.mark.asyncio
async def test_telethon_access_does_not_satisfy_active_subscription(snapshot_context):
    _, archive, content, snapshots = snapshot_context
    source = await archive.upsert_source(
        "-100200",
        "Telethon-only source",
        SourceType.CHANNEL,
        SourceVisibility.PUBLIC,
        updated_at=BEFORE_CUTOFF,
    )
    await archive.set_access(
        source.id,
        AccessMethod.TELETHON,
        AccessState.AVAILABLE,
        owner_telegram_user_id=100,
        verified_at=BEFORE_CUTOFF,
        updated_at=BEFORE_CUTOFF,
    )
    await archive.upsert_subscription(
        100, source.id, SubscriptionState.ACTIVE, changed_at=BEFORE_CUTOFF
    )
    await content.upsert_message(
        source.id, "1", "Not eligible", collected_at="2026-10-20T10:00:00Z"
    )

    snapshot = await snapshots.create_snapshot(
        100, CUTOFF, retention_start_at=RETENTION_START
    )

    assert snapshot.sources == ()
    assert snapshot.messages == ()
    assert [(item.reason_code, item.count) for item in snapshot.omissions] == [
        ("unavailable", 1)
    ]


@pytest.mark.asyncio
async def test_another_users_telethon_access_never_counts_as_requester_access(
    snapshot_context,
):
    _, archive, _, snapshots = snapshot_context
    source = await archive.upsert_source(
        "-100300",
        "Other user's source",
        SourceType.CHANNEL,
        SourceVisibility.PUBLIC,
        updated_at=BEFORE_CUTOFF,
    )
    await archive.set_access(
        source.id,
        AccessMethod.TELETHON,
        AccessState.AVAILABLE,
        owner_telegram_user_id=200,
        verified_at=BEFORE_CUTOFF,
        updated_at=BEFORE_CUTOFF,
    )
    await archive.upsert_subscription(
        100, source.id, SubscriptionState.ACTIVE, changed_at=BEFORE_CUTOFF
    )

    snapshot = await snapshots.create_snapshot(
        100, CUTOFF, retention_start_at=RETENTION_START
    )

    assert snapshot.sources == ()
    assert snapshot.omissions[0].reason_code == "unavailable"


@pytest.mark.asyncio
async def test_coverage_gaps_are_reported_and_telethon_coverage_is_not_counted(
    snapshot_context,
):
    _, archive, content, snapshots = snapshot_context
    source = await add_source(archive)
    await content.record_coverage(
        source.id,
        CollectionMethod.TELETHON,
        RETENTION_START,
        CUTOFF,
    )
    await content.record_coverage(
        source.id,
        CollectionMethod.BOT_API,
        "2026-10-20T00:00:00Z",
        "2026-10-25T00:00:00Z",
    )
    await content.record_coverage(
        source.id,
        CollectionMethod.BOT_API,
        "2026-10-27T00:00:00Z",
        CUTOFF,
    )

    snapshot = await snapshots.create_snapshot(
        100, CUTOFF, retention_start_at=RETENTION_START
    )

    assert len(snapshot.coverage_gaps) == 2
    assert snapshot.coverage_gaps[0].missing_from == RETENTION_START.replace(
        "Z", "+00:00"
    )
    assert snapshot.coverage_gaps[0].missing_until == "2026-10-20T00:00:00+00:00"
    assert snapshot.coverage_gaps[1].missing_from == "2026-10-25T00:00:00+00:00"
    assert snapshot.coverage_gaps[1].missing_until == "2026-10-27T00:00:00+00:00"
    assert snapshot.omissions[0].reason_code == "unavailable"
    assert snapshot.omissions[0].count == 2


@pytest.mark.asyncio
async def test_snapshot_scope_is_user_owned_and_only_active_subscriptions(
    snapshot_context,
):
    _, archive, content, snapshots = snapshot_context
    active = await add_source(archive, chat_id="-100401")
    suspended = await archive.upsert_source(
        "-100402",
        "Suspended source",
        SourceType.CHANNEL,
        SourceVisibility.PUBLIC,
        updated_at=BEFORE_CUTOFF,
    )
    await archive.set_access(
        suspended.id,
        AccessMethod.BOT_API,
        AccessState.AVAILABLE,
        verified_at=BEFORE_CUTOFF,
        updated_at=BEFORE_CUTOFF,
    )
    await archive.upsert_subscription(
        100, suspended.id, SubscriptionState.SUSPENDED, changed_at=BEFORE_CUTOFF
    )
    await archive.upsert_subscription(
        200, active.id, SubscriptionState.ACTIVE, changed_at=BEFORE_CUTOFF
    )
    await content.upsert_message(
        active.id, "1", "Active", collected_at="2026-10-20T10:00:00Z"
    )
    await content.record_coverage(
        active.id, CollectionMethod.BOT_API, RETENTION_START, CUTOFF
    )

    snapshot = await snapshots.create_snapshot(
        100, CUTOFF, retention_start_at=RETENTION_START
    )

    assert [item.id for item in snapshot.sources] == [active.id]
    assert [item.text for item in snapshot.messages] == ["Active"]


@pytest.mark.asyncio
async def test_existing_subscription_changed_after_cutoff_fails_closed(snapshot_context):
    _, archive, _, snapshots = snapshot_context
    source = await add_source(archive)
    await archive.upsert_subscription(
        100,
        source.id,
        SubscriptionState.SUSPENDED,
        changed_at="2026-11-02T12:01:00Z",
    )

    with pytest.raises(SnapshotStateChangedError):
        await snapshots.create_snapshot(
            100, CUTOFF, retention_start_at=RETENTION_START
        )


@pytest.mark.asyncio
async def test_snapshot_rejects_unknown_user_and_invalid_time_window(snapshot_context):
    _, _, _, snapshots = snapshot_context

    with pytest.raises(SnapshotUserNotFoundError):
        await snapshots.create_snapshot(
            999, CUTOFF, retention_start_at=RETENTION_START
        )
    with pytest.raises(ValueError, match="must not be after"):
        await snapshots.create_snapshot(
            100,
            CUTOFF,
            retention_start_at="2026-11-03T00:00:00Z",
        )
    with pytest.raises(ValueError, match="timezone"):
        await snapshots.create_snapshot(
            100,
            "2026-11-02T12:00:00",
            retention_start_at=RETENTION_START,
        )
