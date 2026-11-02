"""Tests for bounded, lease-aware export worker orchestration."""

import asyncio
import logging

import pytest
import pytest_asyncio

from chatbrief.application_storage import (
    ApplicationDatabase,
    ExportJobState,
    ExportRepository,
)
from chatbrief.application_storage.worker import ExportWorker


@pytest_asyncio.fixture
async def export_repository(tmp_path):
    database = ApplicationDatabase(str(tmp_path / "application.db"))
    await database.initialize()
    return ExportRepository(database)


async def _create_jobs(repository, owners=(101, 202, 303)):
    jobs = []
    for owner in owners:
        jobs.append(await repository.create_job(owner, "2026-11-02T00:00:00Z"))
    return jobs


@pytest.mark.asyncio
async def test_worker_dispatches_claimed_phase_and_releases_lease(export_repository):
    job = (await _create_jobs(export_repository, (101,)))[0]
    processed = asyncio.Event()

    async def collect(claimed):
        assert claimed.id == job.id
        assert claimed.lease_owner == worker.worker_id
        result = await export_repository.transition_claimed_job(
            claimed.id,
            worker.worker_id,
            claimed.lease_generation,
            [ExportJobState.QUEUED],
            ExportJobState.COLLECTING,
        )
        assert result is not None
        processed.set()

    worker = ExportWorker(
        export_repository,
        {ExportJobState.QUEUED: collect},
        logging.getLogger("test.export.worker"),
        poll_interval_seconds=0.05,
    )
    running = asyncio.create_task(worker.run())
    await asyncio.wait_for(processed.wait(), timeout=2)
    worker.stop()
    await asyncio.wait_for(running, timeout=2)

    current = await export_repository.get_job(job.id)
    assert current is not None
    assert current.state is ExportJobState.COLLECTING
    assert current.lease_owner is None
    assert current.lease_expires_at is None


@pytest.mark.asyncio
async def test_worker_never_exceeds_configured_concurrency(export_repository):
    jobs = await _create_jobs(export_repository)
    both_started = asyncio.Event()
    release_handlers = asyncio.Event()
    active = 0
    maximum_active = 0
    handled = 0

    async def process(_job):
        nonlocal active, maximum_active, handled
        active += 1
        handled += 1
        maximum_active = max(maximum_active, active)
        if active == 2:
            both_started.set()
        try:
            await release_handlers.wait()
        finally:
            active -= 1

    worker = ExportWorker(
        export_repository,
        {ExportJobState.QUEUED: process},
        logging.getLogger("test.export.worker"),
        max_concurrency=2,
        poll_interval_seconds=0.05,
    )
    running = asyncio.create_task(worker.run())
    await asyncio.wait_for(both_started.wait(), timeout=2)
    assert worker.active_count == 2
    assert handled == 2
    release_handlers.set()
    worker.stop()
    await asyncio.wait_for(running, timeout=2)

    assert maximum_active == 2
    assert handled == 2
    remaining = [await export_repository.get_job(job.id) for job in jobs]
    assert sum(item.lease_owner is not None for item in remaining if item) == 0


@pytest.mark.asyncio
async def test_worker_renews_lease_for_long_running_handler(export_repository):
    job = (await _create_jobs(export_repository, (101,)))[0]
    processed = asyncio.Event()

    async def long_handler(claimed):
        await asyncio.sleep(1.2)
        result = await export_repository.transition_claimed_job(
            claimed.id,
            worker.worker_id,
            claimed.lease_generation,
            [ExportJobState.QUEUED],
            ExportJobState.COLLECTING,
        )
        assert result is not None
        processed.set()

    worker = ExportWorker(
        export_repository,
        {ExportJobState.QUEUED: long_handler},
        logging.getLogger("test.export.worker"),
        lease_seconds=1,
        poll_interval_seconds=0.05,
    )
    running = asyncio.create_task(worker.run())
    await asyncio.wait_for(processed.wait(), timeout=3)
    worker.stop()
    await asyncio.wait_for(running, timeout=2)

    current = await export_repository.get_job(job.id)
    assert current is not None
    assert current.state is ExportJobState.COLLECTING
    assert current.lease_owner is None


@pytest.mark.asyncio
async def test_worker_cancels_handler_when_lease_is_lost(export_repository, monkeypatch):
    job = (await _create_jobs(export_repository, (101,)))[0]
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def lose_lease(*_args, **_kwargs):
        return None

    monkeypatch.setattr(export_repository, "renew_lease", lose_lease)

    async def long_handler(_claimed):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    worker = ExportWorker(
        export_repository,
        {ExportJobState.QUEUED: long_handler},
        logging.getLogger("test.export.worker"),
        lease_seconds=1,
        poll_interval_seconds=0.05,
    )
    running = asyncio.create_task(worker.run())
    await asyncio.wait_for(started.wait(), timeout=2)
    await asyncio.wait_for(cancelled.wait(), timeout=2)
    worker.stop()
    await asyncio.wait_for(running, timeout=2)

    current = await export_repository.get_job(job.id)
    assert current is not None
    assert current.state is ExportJobState.QUEUED
    assert current.lease_owner == worker.worker_id


@pytest.mark.asyncio
async def test_stop_waits_for_active_handlers_to_finish(export_repository):
    job = (await _create_jobs(export_repository, (101,)))[0]
    started = asyncio.Event()
    finish = asyncio.Event()

    async def handler(_claimed):
        started.set()
        await finish.wait()

    worker = ExportWorker(
        export_repository,
        {ExportJobState.QUEUED: handler},
        logging.getLogger("test.export.worker"),
        poll_interval_seconds=0.05,
    )
    running = asyncio.create_task(worker.run())
    await asyncio.wait_for(started.wait(), timeout=2)
    worker.stop()
    await asyncio.sleep(0)
    assert not running.done()

    finish.set()
    await asyncio.wait_for(running, timeout=2)
    current = await export_repository.get_job(job.id)
    assert current is not None
    assert current.lease_owner is None


@pytest.mark.asyncio
async def test_worker_schedules_backoff_when_handler_does_not_advance_state(export_repository):
    job = (await _create_jobs(export_repository, (101,)))[0]
    processed = asyncio.Event()

    async def no_op(_claimed):
        processed.set()

    worker = ExportWorker(
        export_repository,
        {ExportJobState.QUEUED: no_op},
        logging.getLogger("test.export.worker"),
        poll_interval_seconds=0.05,
        retry_delay_seconds=60,
    )
    running = asyncio.create_task(worker.run())
    await asyncio.wait_for(processed.wait(), timeout=2)
    await asyncio.sleep(0.05)
    worker.stop()
    await asyncio.wait_for(running, timeout=2)

    current = await export_repository.get_job(job.id)
    assert current is not None
    assert current.state is ExportJobState.QUEUED
    assert current.lease_owner is None
    assert current.next_run_at is not None
    assert current.next_run_at > current.updated_at


@pytest.mark.asyncio
async def test_shutdown_cancels_handler_after_grace_and_releases_lease(export_repository):
    job = (await _create_jobs(export_repository, (101,)))[0]
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def handler(_claimed):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    worker = ExportWorker(
        export_repository,
        {ExportJobState.QUEUED: handler},
        logging.getLogger("test.export.worker"),
        poll_interval_seconds=0.05,
        shutdown_grace_seconds=0.05,
    )
    running = asyncio.create_task(worker.run())
    await asyncio.wait_for(started.wait(), timeout=2)
    worker.stop()
    await asyncio.wait_for(running, timeout=2)

    assert cancelled.is_set()
    current = await export_repository.get_job(job.id)
    assert current is not None
    assert current.state is ExportJobState.QUEUED
    assert current.lease_owner is None


@pytest.mark.parametrize(
    ("options", "message"),
    [
        ({"worker_id": ""}, "worker_id"),
        ({"max_concurrency": 0}, "max_concurrency"),
        ({"max_concurrency": 33}, "max_concurrency"),
        ({"lease_seconds": 0}, "lease_seconds"),
        ({"poll_interval_seconds": 0}, "poll_interval_seconds"),
        ({"retry_delay_seconds": 0}, "retry_delay_seconds"),
        ({"shutdown_grace_seconds": 0}, "shutdown_grace_seconds"),
    ],
)
@pytest.mark.asyncio\nasync def test_worker_rejects_invalid_configuration(export_repository, options, message):
    with pytest.raises(ValueError, match=message):
        ExportWorker(
            export_repository,
            {},
            logging.getLogger("test.export.worker"),
            **options,
        )
