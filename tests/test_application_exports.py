"""Tests for durable export-job persistence and state transitions."""

import pytest
import pytest_asyncio

from chatbrief.application_storage import ApplicationDatabase
from chatbrief.application_storage.exports import (
    ActiveExportExistsError,
    ExportJobState,
    ExportRepository,
    InvalidExportTransitionError,
)


@pytest_asyncio.fixture
async def export_repository(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()
    return ExportRepository(database)


@pytest.mark.asyncio
async def test_create_and_read_export_job_is_scoped_to_its_owner(export_repository):
    job = await export_repository.create_job(
        12345,
        "2026-11-02T00:00:00+00:00",
        created_at="2026-11-02T01:00:00+00:00",
    )

    assert job.state is ExportJobState.QUEUED
    assert job.owner_telegram_user_id == 12345
    assert job.id != job.export_id
    assert await export_repository.get_job(job.id) == job
    assert await export_repository.get_job(job.id, owner_telegram_user_id=12345) == job
    assert await export_repository.get_job(job.id, owner_telegram_user_id=99999) is None
    unauthorized_transition = await export_repository.transition_job(
        job.id,
        99999,
        [ExportJobState.QUEUED],
        ExportJobState.COLLECTING,
    )
    assert unauthorized_transition is None
    assert await export_repository.get_active_job(12345) == job


@pytest.mark.asyncio
async def test_only_one_blocking_export_per_user(export_repository):
    first = await export_repository.create_job(12345, "2026-11-02T00:00:00Z")

    with pytest.raises(ActiveExportExistsError):
        await export_repository.create_job(12345, "2026-11-02T00:00:00Z")

    second_user_job = await export_repository.create_job(67890, "2026-11-02T00:00:00Z")
    assert second_user_job.owner_telegram_user_id == 67890

    failed = await export_repository.transition_job(
        first.id,
        12345,
        [ExportJobState.QUEUED],
        ExportJobState.FAILED,
        updated_at="2026-11-02T01:00:00Z",
    )
    assert failed is not None
    assert failed.terminal_at == "2026-11-02T01:00:00Z"

    replacement = await export_repository.create_job(12345, "2026-11-02T02:00:00Z")
    assert replacement.state is ExportJobState.QUEUED


@pytest.mark.asyncio
async def test_transition_is_compare_and_set_and_updates_metadata(export_repository):
    job = await export_repository.create_job(12345, "2026-11-02T00:00:00Z")

    collecting = await export_repository.transition_job(
        job.id,
        12345,
        [ExportJobState.QUEUED],
        ExportJobState.COLLECTING,
        updated_at="2026-11-02T01:00:00Z",
    )
    assert collecting is not None
    assert collecting.state is ExportJobState.COLLECTING

    stale_transition = await export_repository.transition_job(
        job.id,
        12345,
        [ExportJobState.QUEUED],
        ExportJobState.FAILED,
        updated_at="2026-11-02T01:01:00Z",
    )
    assert stale_transition is None
    assert await export_repository.get_job(job.id) == collecting

    packaging = await export_repository.transition_job(
        job.id,
        12345,
        [ExportJobState.COLLECTING],
        ExportJobState.PACKAGING,
        updates={"staging_key": "opaque-stage-key"},
    )
    assert packaging is not None
    assert packaging.staging_key == "opaque-stage-key"


@pytest.mark.asyncio
async def test_transition_rejects_skipping_required_lifecycle_states(export_repository):
    job = await export_repository.create_job(12345, "2026-11-02T00:00:00Z")

    with pytest.raises(InvalidExportTransitionError):
        await export_repository.transition_job(
            job.id,
            12345,
            [ExportJobState.QUEUED],
            ExportJobState.READY,
        )


@pytest.mark.asyncio
async def test_ready_transition_requires_confirmed_primary_attempt(export_repository):
    job = await export_repository.create_job(12345, "2026-11-02T00:00:00Z")
    await export_repository.transition_job(
        job.id, 12345, [ExportJobState.QUEUED], ExportJobState.COLLECTING
    )
    await export_repository.transition_job(
        job.id, 12345, [ExportJobState.COLLECTING], ExportJobState.PACKAGING
    )

    with pytest.raises(ValueError, match="confirmed primary delivery attempt"):
        await export_repository.transition_job(
            job.id,
            12345,
            [ExportJobState.PACKAGING],
            ExportJobState.READY,
            updates={
                "primary_delivered_at": "2026-11-02T02:00:00Z",
                "expires_at": "2026-11-03T02:00:00Z",
            },
        )

    unchanged = await export_repository.get_job(job.id)
    assert unchanged is not None
    assert unchanged.state is ExportJobState.PACKAGING


@pytest.mark.asyncio
async def test_transition_rejects_unknown_fields_and_invalid_json(export_repository):
    job = await export_repository.create_job(12345, "2026-11-02T00:00:00Z")

    with pytest.raises(ValueError, match="Unsupported export-job fields"):
        await export_repository.transition_job(
            job.id,
            12345,
            [ExportJobState.QUEUED],
            ExportJobState.COLLECTING,
            updates={"owner_telegram_user_id": "999"},
        )

    with pytest.raises(ValueError, match="valid JSON"):
        await export_repository.transition_job(
            job.id,
            12345,
            [ExportJobState.QUEUED],
            ExportJobState.COLLECTING,
            updates={"report_json": "{invalid"},
        )

    unchanged = await export_repository.get_job(job.id)
    assert unchanged is not None
    assert unchanged.state is ExportJobState.QUEUED


@pytest.mark.asyncio
async def test_terminal_states_release_active_export_constraint(export_repository):
    job = await export_repository.create_job(12345, "2026-11-02T00:00:00Z")

    failed = await export_repository.transition_job(
        job.id,
        12345,
        [ExportJobState.QUEUED],
        ExportJobState.FAILED,
    )
    assert failed is not None
    assert failed.terminal_at is not None
    assert await export_repository.get_active_job(12345) is None

    replacement = await export_repository.create_job(12345, "2026-11-02T01:00:00Z")
    assert replacement.state is ExportJobState.QUEUED


@pytest.mark.asyncio
async def test_owner_id_must_be_positive(export_repository):
    with pytest.raises(ValueError, match="positive integer"):
        await export_repository.create_job(0, "2026-11-02T00:00:00Z")


@pytest.mark.asyncio
async def test_worker_claim_is_atomic_and_assigns_first_lease_generation(export_repository):
    import asyncio

    job = await export_repository.create_job(12345, "2026-11-02T00:00:00Z")
    first, second = await asyncio.gather(
        export_repository.claim_next_job(
            "worker-a", now="2026-11-02T01:00:00Z", lease_seconds=60
        ),
        export_repository.claim_next_job(
            "worker-b", now="2026-11-02T01:00:00Z", lease_seconds=60
        ),
    )

    claims = [claim for claim in (first, second) if claim is not None]
    assert len(claims) == 1
    assert claims[0].id == job.id
    assert claims[0].lease_generation == 1
    assert claims[0].lease_owner in {"worker-a", "worker-b"}
    assert claims[0].lease_expires_at == "2026-11-02T01:01:00+00:00"


@pytest.mark.asyncio
async def test_expired_lease_reclaim_fences_stale_worker(export_repository):
    job = await export_repository.create_job(12345, "2026-11-02T00:00:00Z")
    first_claim = await export_repository.claim_next_job(
        "worker-a", now="2026-11-02T01:00:00Z", lease_seconds=60
    )
    assert first_claim is not None

    reclaimed = await export_repository.claim_next_job(
        "worker-b", now="2026-11-02T01:01:00Z", lease_seconds=60
    )
    assert reclaimed is not None
    assert reclaimed.id == job.id
    assert reclaimed.lease_owner == "worker-b"
    assert reclaimed.lease_generation == first_claim.lease_generation + 1

    assert (
        await export_repository.renew_lease(
            job.id,
            "worker-a",
            first_claim.lease_generation,
            now="2026-11-02T01:01:01Z",
        )
        is None
    )
    assert (
        await export_repository.release_lease(
            job.id,
            "worker-a",
            first_claim.lease_generation,
            now="2026-11-02T01:01:01Z",
        )
        is None
    )
    assert (
        await export_repository.transition_claimed_job(
            job.id,
            "worker-a",
            first_claim.lease_generation,
            [ExportJobState.QUEUED],
            ExportJobState.COLLECTING,
            updated_at="2026-11-02T01:01:01Z",
        )
        is None
    )

    collecting = await export_repository.transition_claimed_job(
        job.id,
        "worker-b",
        reclaimed.lease_generation,
        [ExportJobState.QUEUED],
        ExportJobState.COLLECTING,
        updated_at="2026-11-02T01:01:02Z",
    )
    assert collecting is not None
    assert collecting.state is ExportJobState.COLLECTING
    assert collecting.lease_owner == "worker-b"


@pytest.mark.asyncio
async def test_worker_lease_can_be_renewed_and_released_with_backoff(export_repository):
    job = await export_repository.create_job(12345, "2026-11-02T00:00:00Z")
    claimed = await export_repository.claim_next_job(
        "worker-a", now="2026-11-02T01:00:00Z", lease_seconds=60
    )
    assert claimed is not None

    renewed = await export_repository.renew_lease(
        job.id,
        "worker-a",
        claimed.lease_generation,
        now="2026-11-02T01:00:30Z",
        lease_seconds=120,
    )
    assert renewed is not None
    assert renewed.lease_expires_at == "2026-11-02T01:02:30+00:00"

    released = await export_repository.release_lease(
        job.id,
        "worker-a",
        claimed.lease_generation,
        now="2026-11-02T01:00:40Z",
        next_run_at="2026-11-02T02:00:00Z",
    )
    assert released is not None
    assert released.lease_owner is None
    assert released.lease_expires_at is None
    assert released.next_run_at == "2026-11-02T02:00:00+00:00"
    assert (
        await export_repository.claim_next_job(
            "worker-b", now="2026-11-02T01:59:59Z"
        )
        is None
    )

    next_claim = await export_repository.claim_next_job(
        "worker-b", now="2026-11-02T02:00:00Z"
    )
    assert next_claim is not None
    assert next_claim.lease_generation == claimed.lease_generation + 1


@pytest.mark.asyncio
async def test_worker_lease_rejects_invalid_parameters(export_repository):
    with pytest.raises(ValueError, match="Worker ID"):
        await export_repository.claim_next_job(" ")
    with pytest.raises(ValueError, match="Lease duration"):
        await export_repository.claim_next_job("worker-a", lease_seconds=0)
    with pytest.raises(ValueError, match="timezone"):
        await export_repository.claim_next_job("worker-a", now="2026-11-02T01:00:00")

@pytest.mark.asyncio
async def test_claimed_terminal_transition_releases_lease(export_repository):
    job = await export_repository.create_job(12345, "2026-11-02T00:00:00Z")
    claimed = await export_repository.claim_next_job(
        "worker-a", now="2026-11-02T01:00:00Z"
    )
    assert claimed is not None

    failed = await export_repository.transition_claimed_job(
        job.id,
        "worker-a",
        claimed.lease_generation,
        [ExportJobState.QUEUED],
        ExportJobState.FAILED,
        updated_at="2026-11-02T01:00:10Z",
    )
    assert failed is not None
    assert failed.state is ExportJobState.FAILED
    assert failed.terminal_at == "2026-11-02T01:00:10+00:00"
    assert failed.lease_owner is None
    assert failed.lease_expires_at is None

