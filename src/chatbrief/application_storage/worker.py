"""Lease-aware orchestration for durable export jobs.

Phase handlers own the work for one persisted job state. They must use the
job's lease owner and generation for every worker-owned repository mutation.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Awaitable, Callable, Mapping
from contextlib import suppress
from datetime import datetime, timedelta, timezone

from chatbrief.application_storage.exports import ExportJob, ExportJobState, ExportRepository

ExportPhaseHandler = Callable[[ExportJob], Awaitable[None]]


class ExportLeaseLostError(RuntimeError):
    """Raised internally when a worker no longer owns a job's live lease."""


class ExportWorker:
    """Claim and dispatch export jobs with bounded concurrency and lease renewal.

    A handler processes one phase for a claimed job. It is responsible for
    advancing the job with `transition_claimed_job()` and for using the
    generation token on delivery-attempt writes. The worker releases the lease
    after the handler returns so a subsequent phase can be claimed.
    """

    def __init__(
        self,
        repository: ExportRepository,
        phase_handlers: Mapping[ExportJobState, ExportPhaseHandler],
        logger: logging.Logger,
        *,
        worker_id: str | None = None,
        max_concurrency: int = 2,
        poll_interval_seconds: float = 1.0,
        lease_seconds: int = 300,
        retry_delay_seconds: int = 30,
        shutdown_grace_seconds: float = 30.0,
    ) -> None:
        if isinstance(max_concurrency, bool) or not isinstance(max_concurrency, int):
            raise ValueError("max_concurrency must be an integer")
        if not 1 <= max_concurrency <= 32:
            raise ValueError("max_concurrency must be between 1 and 32")
        if (
            isinstance(poll_interval_seconds, bool)
            or not isinstance(poll_interval_seconds, (int, float))
            or not 0.05 <= poll_interval_seconds <= 60
        ):
            raise ValueError("poll_interval_seconds must be between 0.05 and 60")
        if (
            isinstance(lease_seconds, bool)
            or not isinstance(lease_seconds, int)
            or not 1 <= lease_seconds <= 3600
        ):
            raise ValueError("lease_seconds must be between 1 and 3600")
        if (
            isinstance(retry_delay_seconds, bool)
            or not isinstance(retry_delay_seconds, int)
            or not 1 <= retry_delay_seconds <= 3600
        ):
            raise ValueError("retry_delay_seconds must be between 1 and 3600")

        if (
            isinstance(shutdown_grace_seconds, bool)
            or not isinstance(shutdown_grace_seconds, (int, float))
            or not 0.01 <= shutdown_grace_seconds <= 3600
        ):
            raise ValueError("shutdown_grace_seconds must be between 0.01 and 3600")
        if worker_id is not None and (
            not isinstance(worker_id, str)
            or not worker_id
            or worker_id != worker_id.strip()
            or len(worker_id) > 128
        ):
            raise ValueError(
                "worker_id must be a non-empty opaque identifier of at most 128 characters"
            )
        normalized_handlers = {
            ExportJobState(state): handler for state, handler in phase_handlers.items()
        }
        if any(not callable(handler) for handler in normalized_handlers.values()):
            raise ValueError("Every phase handler must be callable")

        self.repository = repository
        self.phase_handlers = normalized_handlers
        self.logger = logger
        self.worker_id = str(uuid.uuid4()) if worker_id is None else worker_id
        self.max_concurrency = max_concurrency
        self.poll_interval_seconds = float(poll_interval_seconds)
        self.lease_seconds = lease_seconds
        self.retry_delay_seconds = retry_delay_seconds
        self.shutdown_grace_seconds = float(shutdown_grace_seconds)
        self._stop_event = asyncio.Event()
        self._running = False
        self._active_tasks: set[asyncio.Task[None]] = set()

    @property
    def is_running(self) -> bool:
        """Whether the worker polling loop is currently active."""
        return self._running

    @property
    def active_count(self) -> int:
        """Number of currently tracked job handlers."""
        return len(self._active_tasks)

    def stop(self) -> None:
        """Stop claiming new work; active handlers finish under renewed leases."""
        self._stop_event.set()

    async def run(self) -> None:
        """Poll for jobs until stopped, then wait for active handlers to finish."""
        if self._running:
            raise RuntimeError("Export worker is already running")
        self._running = True
        self._stop_event.clear()
        try:
            while not self._stop_event.is_set():
                self._discard_finished_tasks()
                if len(self._active_tasks) < self.max_concurrency:
                    job = await self.repository.claim_next_job(
                        self.worker_id,
                        lease_seconds=self.lease_seconds,
                    )
                    if job is not None:
                        if self._stop_event.is_set():
                            await self.repository.release_lease(
                                job.id, self.worker_id, job.lease_generation
                            )
                            break
                        task = asyncio.create_task(
                            self._process_job(job),
                            name=f"chatbrief-export-{job.id}",
                        )
                        self._active_tasks.add(task)
                        continue
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self.poll_interval_seconds,
                    )
                except TimeoutError:
                    pass
        finally:
            self._stop_event.set()
            if self._active_tasks:
                _, pending = await asyncio.wait(
                    self._active_tasks,
                    timeout=self.shutdown_grace_seconds,
                )
                for task in pending:
                    task.cancel()
                if pending:
                    await asyncio.gather(*pending, return_exceptions=True)
                completed = self._active_tasks - pending
                if completed:
                    await asyncio.gather(*completed, return_exceptions=True)
            self._active_tasks.clear()
            self._running = False

    def _discard_finished_tasks(self) -> None:
        self._active_tasks = {task for task in self._active_tasks if not task.done()}

    async def _process_job(self, job: ExportJob) -> None:
        handler = self.phase_handlers.get(job.state)
        if handler is None:
            self.logger.warning(
                "No export phase handler registered for state %s; job %s will be retried",
                job.state.value,
                job.id,
            )
            await self._release_for_retry(job)
            return

        try:
            await self._run_with_lease_renewal(job, handler)
        except ExportLeaseLostError:
            self.logger.warning("Export lease lost for job %s; stale handler stopped", job.id)
            return
        except asyncio.CancelledError:
            await self.repository.release_lease(
                job.id,
                self.worker_id,
                job.lease_generation,
            )
            raise
        except Exception:
            self.logger.error(
                "Export phase handler failed for job %s; retry scheduled",
                job.id,
            )
            await self._release_for_retry(job)
            return

        current = await self.repository.get_job(
            job.id,
            owner_telegram_user_id=job.owner_telegram_user_id,
        )
        if current is None or current.state in {
            ExportJobState.READY,
            ExportJobState.CANCELLED,
            ExportJobState.FAILED,
            ExportJobState.INVALIDATED,
            ExportJobState.EXPIRED,
        }:
            return

        # A successful handler should advance the lifecycle. If it did not,
        # back off rather than repeatedly claiming a no-op phase.
        next_run_at = None
        if current.state is job.state:
            next_run_at = self._retry_timestamp()
        await self.repository.release_lease(
            job.id,
            self.worker_id,
            job.lease_generation,
            next_run_at=next_run_at,
        )

    async def _run_with_lease_renewal(
        self,
        job: ExportJob,
        handler: ExportPhaseHandler,
    ) -> None:
        handler_task = asyncio.create_task(handler(job))
        renewal_interval = max(0.1, self.lease_seconds / 3)
        try:
            while True:
                done, _ = await asyncio.wait(
                    {handler_task},
                    timeout=renewal_interval,
                )
                if done:
                    await handler_task
                    return
                renewed = await self.repository.renew_lease(
                    job.id,
                    self.worker_id,
                    job.lease_generation,
                    lease_seconds=self.lease_seconds,
                )
                if renewed is None:
                    handler_task.cancel()
                    with suppress(asyncio.CancelledError):
                        await handler_task
                    raise ExportLeaseLostError(job.id)
        finally:
            if not handler_task.done():
                handler_task.cancel()
                with suppress(asyncio.CancelledError):
                    await handler_task

    async def _release_for_retry(self, job: ExportJob) -> None:
        await self.repository.release_lease(
            job.id,
            self.worker_id,
            job.lease_generation,
            next_run_at=self._retry_timestamp(),
        )

    def _retry_timestamp(self) -> str:
        return (
            datetime.now(timezone.utc) + timedelta(seconds=self.retry_delay_seconds)
        ).isoformat()
