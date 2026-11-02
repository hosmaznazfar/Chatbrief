"""Tests for shared archive message and collection-coverage persistence."""

import pytest
import pytest_asyncio

from chatbrief.application_storage import ApplicationDatabase
from chatbrief.application_storage.archive import ArchiveRepository, SourceType, SourceVisibility
from chatbrief.application_storage.archive_content import (
    ArchiveContentRepository,
    CollectionMethod,
    MessageMediaType,
)


@pytest_asyncio.fixture
async def content_repository(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()
    source = await ArchiveRepository(database).upsert_source(
        "-100123",
        "Example channel",
        SourceType.CHANNEL,
        SourceVisibility.PUBLIC,
    )
    return ArchiveContentRepository(database), source.id


@pytest.mark.asyncio
async def test_message_upsert_deduplicates_by_source_and_platform_identity(
    content_repository,
):
    repository, source_id = content_repository
    first = await repository.upsert_message(
        source_id,
        "42",
        "Original body",
        collected_at="2026-11-02T01:00:00Z",
        sender_label="Channel admin",
        source_timestamp="2026-11-02T00:30:00Z",
    )
    edited = await repository.upsert_message(
        source_id,
        "42",
        "Edited body",
        collected_at="2026-11-02T02:00:00Z",
        edited_at="2026-11-02T01:30:00Z",
    )

    assert edited.id == first.id
    assert edited.text == "Edited body"
    assert edited.sender_label == "Channel admin"
    assert edited.collected_at == first.collected_at
    assert edited.source_timestamp == first.source_timestamp
    assert edited.edited_at == "2026-11-02T01:30:00+00:00"
    assert await repository.get_message(source_id, "42") == edited


@pytest.mark.asyncio
async def test_media_metadata_must_match_has_media(content_repository):
    repository, source_id = content_repository
    with pytest.raises(ValueError, match="supplied consistently"):
        await repository.upsert_message(
            source_id,
            "42",
            "Caption",
            collected_at="2026-11-02T01:00:00Z",
            has_media=True,
        )

    media = await repository.upsert_message(
        source_id,
        "43",
        "Caption",
        collected_at="2026-11-02T01:00:00Z",
        has_media=True,
        media_type=MessageMediaType.IMAGE,
    )
    assert media.has_media is True
    assert media.media_type is MessageMediaType.IMAGE


@pytest.mark.asyncio
async def test_deletion_is_reliable_and_later_edit_does_not_resurrect_message(
    content_repository,
):
    repository, source_id = content_repository
    message = await repository.upsert_message(
        source_id, "42", "Body", collected_at="2026-11-02T01:00:00Z"
    )
    deleted = await repository.mark_message_deleted(
        source_id, "42", deleted_at="2026-11-02T02:00:00Z"
    )
    assert deleted is not None
    assert deleted.id == message.id
    assert deleted.deleted_at == "2026-11-02T02:00:00+00:00"

    updated = await repository.upsert_message(
        source_id, "42", "Late edit", collected_at="2026-11-02T03:00:00Z"
    )
    assert updated.deleted_at == deleted.deleted_at


@pytest.mark.asyncio
async def test_coverage_merges_only_overlapping_or_adjacent_intervals(
    content_repository,
):
    repository, source_id = content_repository
    first = await repository.record_coverage(
        source_id,
        CollectionMethod.BOT_API,
        "2026-11-02T00:00:00Z",
        "2026-11-02T01:00:00Z",
        recorded_at="2026-11-02T01:01:00Z",
    )
    second = await repository.record_coverage(
        source_id,
        CollectionMethod.BOT_API,
        "2026-11-02T01:00:00Z",
        "2026-11-02T02:00:00Z",
        recorded_at="2026-11-02T02:01:00Z",
    )
    assert len(first) == 1
    assert len(second) == 1
    assert second[0].covered_from == "2026-11-02T00:00:00+00:00"
    assert second[0].covered_until == "2026-11-02T02:00:00+00:00"

    separated = await repository.record_coverage(
        source_id,
        CollectionMethod.BOT_API,
        "2026-11-02T03:00:00Z",
        "2026-11-02T04:00:00Z",
    )
    assert len(separated) == 2
    telethon = await repository.record_coverage(
        source_id,
        CollectionMethod.TELETHON,
        "2026-11-02T00:00:00Z",
        "2026-11-02T04:00:00Z",
    )
    assert len(telethon) == 1
    assert len(await repository.list_coverage(source_id)) == 3
    assert len(await repository.list_coverage(source_id, CollectionMethod.BOT_API)) == 2


@pytest.mark.asyncio
async def test_coverage_rejects_reversed_or_timezone_naive_intervals(content_repository):
    repository, source_id = content_repository
    with pytest.raises(ValueError, match="must not precede"):
        await repository.record_coverage(
            source_id,
            CollectionMethod.BOT_API,
            "2026-11-02T02:00:00Z",
            "2026-11-02T01:00:00Z",
        )
    with pytest.raises(ValueError, match="timezone"):
        await repository.record_coverage(
            source_id,
            CollectionMethod.BOT_API,
            "2026-11-02T00:00:00",
            "2026-11-02T01:00:00Z",
        )
