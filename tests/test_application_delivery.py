"""Tests for durable export delivery attempts and cleanup tasks."""

import pytest
import pytest_asyncio

from chatbrief.application_storage import (
    ApplicationDatabase,
    CleanupTaskState,
    DeliveryAttemptOutcome,
    DeliveryDocumentKind,
    ExportCleanupRepository,
    ExportDeliveryRepository,
    ExportJobState,
    ExportRepository,
)


@pytest_asyncio.fixture
async def export_repositories(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()
    return (
        database,
        ExportRepository(database),
        ExportDeliveryRepository(database),
        ExportCleanupRepository(database),
    )


async def _packaging_job(jobs: ExportRepository, owner: int = 12345):
    job = await jobs.create_job(owner, "2026-11-02T00:00:00Z")
    collecting = await jobs.transition_job(
        job.id, owner, [ExportJobState.QUEUED], ExportJobState.COLLECTING
    )
    assert collecting is not None
    packaging = await jobs.transition_job(
        job.id, owner, [ExportJobState.COLLECTING], ExportJobState.PACKAGING
    )
    assert packaging is not None
    return packaging


@pytest.mark.asyncio
async def test_primary_delivery_attempt_can_be_confirmed_and_job_becomes_ready(
    export_repositories,
):
    _, jobs, deliveries, _ = export_repositories
    job = await _packaging_job(jobs)

    attempt = await deliveries.start_attempt(
        job.id,
        12345,
        DeliveryDocumentKind.PRIMARY,
        started_at="2026-11-02T01:00:00Z",
    )
    assert attempt is not None
    assert attempt.attempt_number == 1
    assert attempt.outcome is DeliveryAttemptOutcome.STARTED

    succeeded = await deliveries.finish_attempt(
        attempt.id,
        12345,
        DeliveryAttemptOutcome.SUCCEEDED,
        finished_at="2026-11-02T01:01:00Z",
        telegram_chat_id=12345,
        telegram_message_id=987,
        telegram_file_id="opaque-telegram-file-id",
    )
    assert succeeded is not None
    assert succeeded.outcome is DeliveryAttemptOutcome.SUCCEEDED
    assert succeeded.telegram_message_id == 987

    ready = await jobs.transition_job(
        job.id,
        12345,
        [ExportJobState.PACKAGING],
        ExportJobState.READY,
        updates={"expires_at": "2026-11-03T01:01:00Z"},
    )
    assert ready is not None
    assert ready.state is ExportJobState.READY
    assert ready.primary_delivered_at == "2026-11-02T01:01:00Z"


@pytest.mark.asyncio
async def test_delivery_attempts_are_owner_scoped(export_repositories):
    _, jobs, deliveries, _ = export_repositories
    job = await _packaging_job(jobs)
    assert (
        await deliveries.start_attempt(
            job.id, 99999, DeliveryDocumentKind.PRIMARY
        )
        is None
    )
    attempt = await deliveries.start_attempt(
        job.id, 12345, DeliveryDocumentKind.PRIMARY
    )
    assert attempt is not None
    assert (
        await deliveries.finish_attempt(
            attempt.id, 99999, DeliveryAttemptOutcome.FAILED
        )
        is None
    )
    assert await deliveries.list_attempts(job.id, 99999) is None
    assert await deliveries.list_attempts(job.id, 12345) == (attempt,)


@pytest.mark.asyncio
async def test_failed_delivery_can_retry_with_a_new_attempt_number(export_repositories):
    _, jobs, deliveries, _ = export_repositories
    job = await _packaging_job(jobs)
    first = await deliveries.start_attempt(job.id, 12345, DeliveryDocumentKind.PRIMARY)
    assert first is not None

    failed = await deliveries.finish_attempt(
        first.id,
        12345,
        DeliveryAttemptOutcome.FAILED,
        finished_at="2026-11-02T01:00:00Z",
        error_code="telegram_rate_limited",
        retry_after_seconds=30,
        retry_after_at="2026-11-02T01:00:30Z",
    )
    assert failed is not None
    assert failed.retry_after_seconds == 30

    second = await deliveries.start_attempt(job.id, 12345, DeliveryDocumentKind.PRIMARY)
    assert second is not None
    assert second.attempt_number == 2
    attempts = await deliveries.list_attempts(job.id, 12345)
    assert attempts is not None
    assert len(attempts) == 2


@pytest.mark.asyncio
async def test_started_or_delivery_unknown_attempt_cannot_be_retried(export_repositories):
    _, jobs, deliveries, _ = export_repositories
    job = await _packaging_job(jobs)
    started = await deliveries.start_attempt(job.id, 12345, DeliveryDocumentKind.PRIMARY)
    assert started is not None
    with pytest.raises(ValueError, match="previous delivery attempt"):
        await deliveries.start_attempt(job.id, 12345, DeliveryDocumentKind.PRIMARY)

    unknown = await deliveries.finish_attempt(
        started.id, 12345, DeliveryAttemptOutcome.DELIVERY_UNKNOWN
    )
    assert unknown is not None
    with pytest.raises(ValueError, match="previous delivery attempt"):
        await deliveries.start_attempt(job.id, 12345, DeliveryDocumentKind.PRIMARY)


@pytest.mark.asyncio
async def test_attempt_cannot_be_finished_twice_or_with_started_outcome(export_repositories):
    _, jobs, deliveries, _ = export_repositories
    job = await _packaging_job(jobs)
    attempt = await deliveries.start_attempt(job.id, 12345, DeliveryDocumentKind.PRIMARY)
    assert attempt is not None

    with pytest.raises(ValueError, match="final outcome"):
        await deliveries.finish_attempt(
            attempt.id, 12345, DeliveryAttemptOutcome.STARTED
        )

    failed = await deliveries.finish_attempt(
        attempt.id, 12345, DeliveryAttemptOutcome.FAILED
    )
    assert failed is not None
    assert (
        await deliveries.finish_attempt(
            attempt.id, 12345, DeliveryAttemptOutcome.SUCCEEDED
        )
        is None
    )


@pytest.mark.asyncio
async def test_media_attempt_requires_primary_success_and_updates_job_outcome(
    export_repositories,
):
    _, jobs, deliveries, _ = export_repositories
    job = await _packaging_job(jobs)

    with pytest.raises(ValueError, match="confirmed primary"):
        await deliveries.start_attempt(job.id, 12345, DeliveryDocumentKind.MEDIA)

    primary = await deliveries.start_attempt(
        job.id, 12345, DeliveryDocumentKind.PRIMARY
    )
    assert primary is not None
    assert await deliveries.finish_attempt(
        primary.id, 12345, DeliveryAttemptOutcome.SUCCEEDED
    )

    media = await deliveries.start_attempt(job.id, 12345, DeliveryDocumentKind.MEDIA)
    assert media is not None
    sent = await deliveries.finish_attempt(
        media.id, 12345, DeliveryAttemptOutcome.SUCCEEDED
    )
    assert sent is not None
    refreshed = await jobs.get_job(job.id, owner_telegram_user_id=12345)
    assert refreshed is not None
    assert refreshed.media_outcome is not None
    assert refreshed.media_outcome.value == "sent"


@pytest.mark.asyncio
async def test_cleanup_tasks_cover_telegram_and_staging_resources(export_repositories):
    _, jobs, _, cleanup = export_repositories
    job = await _packaging_job(jobs)

    telegram_task = await cleanup.create_telegram_message_task(
        job.id, 12345, -100123, 987, next_attempt_at="2026-11-02T02:00:00Z"
    )
    staging_task = await cleanup.create_staging_task(
        job.id,
        12345,
        "opaque-staging-key",
        next_attempt_at="2026-11-02T02:00:00Z",
    )
    assert telegram_task is not None
    assert staging_task is not None
    assert telegram_task.telegram_chat_id == -100123
    assert telegram_task.telegram_message_id == 987
    assert staging_task.staging_key == "opaque-staging-key"
    assert staging_task.telegram_chat_id is None

    due = await cleanup.list_due_tasks("2026-11-02T02:00:00Z")
    assert {task.id for task in due} == {telegram_task.id, staging_task.id}


@pytest.mark.asyncio
async def test_cleanup_task_retry_and_terminal_update_are_compare_and_set(
    export_repositories,
):
    _, jobs, _, cleanup = export_repositories
    job = await _packaging_job(jobs)
    task = await cleanup.create_staging_task(job.id, 12345, "stage-key")
    assert task is not None

    retry = await cleanup.record_attempt(
        task.id,
        CleanupTaskState.PENDING,
        next_attempt_at="2026-11-02T03:00:00Z",
        error_code="temporary_io_error",
        updated_at="2026-11-02T02:00:00Z",
    )
    assert retry is not None
    assert retry.attempt_count == 1
    assert retry.last_error_code == "temporary_io_error"
    assert retry.next_attempt_at == "2026-11-02T03:00:00Z"

    done = await cleanup.record_attempt(
        task.id,
        CleanupTaskState.SUCCEEDED,
        updated_at="2026-11-02T03:01:00Z",
    )
    assert done is not None
    assert done.state is CleanupTaskState.SUCCEEDED
    assert done.attempt_count == 2
    assert await cleanup.record_attempt(task.id, CleanupTaskState.SUCCEEDED) is None


@pytest.mark.asyncio
async def test_cleanup_task_survives_job_deletion_and_can_be_completed(
    export_repositories,
):
    database, jobs, _, cleanup = export_repositories
    job = await _packaging_job(jobs)
    task = await cleanup.create_staging_task(job.id, 12345, "stage-key")
    assert task is not None

    connection = await database.connect()
    try:
        await connection.execute("DELETE FROM export_jobs WHERE id = ?", (job.id,))
        await connection.commit()
    finally:
        await connection.close()

    orphaned = await cleanup.get_task(task.id)
    assert orphaned is not None
    assert orphaned.job_id is None
    completed = await cleanup.record_attempt(task.id, CleanupTaskState.SUCCEEDED)
    assert completed is not None
    assert completed.state is CleanupTaskState.SUCCEEDED


@pytest.mark.asyncio
async def test_cleanup_tasks_are_created_only_for_owned_jobs(export_repositories):
    _, jobs, _, cleanup = export_repositories
    job = await _packaging_job(jobs)
    assert (
        await cleanup.create_staging_task(job.id, 99999, "stage-key")
        is None
    )
    with pytest.raises(ValueError, match="non-empty"):
        await cleanup.create_staging_task(job.id, 12345, "")
    with pytest.raises(ValueError, match="limit"):
        await cleanup.list_due_tasks("2026-11-02T00:00:00Z", limit=0)
