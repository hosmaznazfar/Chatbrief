from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.scheduler import DigestScheduler


def make_scheduler(sample_config, mock_logger):
    scheduler = DigestScheduler(sample_config, mock_logger)

    mock_scheduler = MagicMock()
    scheduler.scheduler = mock_scheduler

    return scheduler, mock_scheduler


def test_init(sample_config, mock_logger):
    scheduler, _ = make_scheduler(sample_config, mock_logger)

    assert scheduler.config is sample_config
    assert scheduler.logger is mock_logger
    assert scheduler.is_running is False


def test_parse_schedule_time(sample_config, mock_logger):
    sample_config.settings.schedule_time = "14:30"

    scheduler, _ = make_scheduler(sample_config, mock_logger)

    assert scheduler._parse_schedule_time() == (14, 30)


def test_parse_schedule_time_invalid(sample_config, mock_logger):
    sample_config.settings.schedule_time = "invalid"

    scheduler, _ = make_scheduler(sample_config, mock_logger)

    assert scheduler._parse_schedule_time() == (8, 0)
    mock_logger.warning.assert_called_once_with(
        "Invalid schedule time 'invalid', using default 08:00"
    )


def test_parse_schedule_time_invalid_format(sample_config, mock_logger):
    sample_config.settings.schedule_time = "14"

    scheduler, _ = make_scheduler(sample_config, mock_logger)

    assert scheduler._parse_schedule_time() == (8, 0)


def test_start(sample_config, mock_logger):
    sample_config.settings.schedule_time = "14:30"

    scheduler, mock_scheduler = make_scheduler(sample_config, mock_logger)

    mock_job = MagicMock()
    mock_job.next_run_time = datetime(2026, 9, 7, 14, 30)
    mock_scheduler.get_job.return_value = mock_job

    scheduler.start()

    mock_scheduler.add_job.assert_called_once()
    mock_scheduler.start.assert_called_once()
    mock_scheduler.get_job.assert_called_once_with("daily_digest")

    assert scheduler.is_running is True

    call_kwargs = mock_scheduler.add_job.call_args.kwargs
    assert call_kwargs["id"] == "daily_digest"
    assert call_kwargs["name"] == "Daily Digest Generation"
    assert call_kwargs["replace_existing"] is True

    mock_logger.info.assert_any_call("✅ Scheduler started")


def test_start_when_already_running(sample_config, mock_logger):
    scheduler, mock_scheduler = make_scheduler(sample_config, mock_logger)
    scheduler.is_running = True

    scheduler.start()

    mock_logger.warning.assert_called_once_with("Scheduler already running")
    mock_scheduler.add_job.assert_not_called()
    mock_scheduler.start.assert_not_called()


def test_start_without_job_after_start(sample_config, mock_logger):
    scheduler, mock_scheduler = make_scheduler(sample_config, mock_logger)
    mock_scheduler.get_job.return_value = None

    scheduler.start()

    assert scheduler.is_running is True
    mock_logger.info.assert_any_call("⏰ Next digest scheduled for: None UTC")


def test_stop_running_scheduler(sample_config, mock_logger):
    scheduler, mock_scheduler = make_scheduler(sample_config, mock_logger)
    scheduler.is_running = True
    mock_scheduler.running = True

    scheduler.stop()

    mock_scheduler.shutdown.assert_called_once()
    assert scheduler.is_running is False
    mock_logger.info.assert_called_once_with("Scheduler stopped")


def test_stop_when_scheduler_not_running(sample_config, mock_logger):
    scheduler, mock_scheduler = make_scheduler(sample_config, mock_logger)
    scheduler.is_running = True
    mock_scheduler.running = False

    scheduler.stop()

    mock_scheduler.shutdown.assert_not_called()
    assert scheduler.is_running is True
    mock_logger.info.assert_not_called()


@pytest.mark.asyncio
async def test_scheduled_digest_job_success(sample_config, mock_logger):
    scheduler, _ = make_scheduler(sample_config, mock_logger)

    with pytest.MonkeyPatch.context() as monkeypatch:
        mock_generate = AsyncMock(return_value=True)
        monkeypatch.setattr("src.scheduler.generate_and_send_digest", mock_generate)

        await scheduler._scheduled_digest_job()

    mock_generate.assert_awaited_once_with(
        config=sample_config,
        logger=mock_logger,
        hours=sample_config.settings.lookback_hours,
    )
    mock_logger.info.assert_any_call("✅ Scheduled digest completed successfully")


@pytest.mark.asyncio
async def test_scheduled_digest_job_failure(sample_config, mock_logger):
    scheduler, _ = make_scheduler(sample_config, mock_logger)

    with pytest.MonkeyPatch.context() as monkeypatch:
        mock_generate = AsyncMock(return_value=False)
        monkeypatch.setattr("src.scheduler.generate_and_send_digest", mock_generate)

        await scheduler._scheduled_digest_job()

    mock_generate.assert_awaited_once()
    mock_logger.error.assert_called_once_with("❌ Scheduled digest failed to send")


@pytest.mark.asyncio
async def test_scheduled_digest_job_exception(sample_config, mock_logger):
    scheduler, _ = make_scheduler(sample_config, mock_logger)

    with pytest.MonkeyPatch.context() as monkeypatch:
        mock_generate = AsyncMock(side_effect=RuntimeError("digest error"))
        monkeypatch.setattr("src.scheduler.generate_and_send_digest", mock_generate)

        await scheduler._scheduled_digest_job()

    mock_generate.assert_awaited_once()
    mock_logger.error.assert_called_once_with(
        "❌ Scheduled digest job failed: digest error",
        exc_info=True,
    )


def test_get_next_run_time_when_not_running(sample_config, mock_logger):
    scheduler, mock_scheduler = make_scheduler(sample_config, mock_logger)

    assert scheduler.get_next_run_time() == "Scheduler not running"
    mock_scheduler.get_job.assert_not_called()


def test_get_next_run_time_with_job(sample_config, mock_logger):
    scheduler, mock_scheduler = make_scheduler(sample_config, mock_logger)
    scheduler.is_running = True

    mock_job = MagicMock()
    mock_job.next_run_time = datetime(2026, 9, 7, 14, 30)
    mock_scheduler.get_job.return_value = mock_job

    result = scheduler.get_next_run_time()

    assert result == "2026-09-07 14:30:00 "


def test_get_next_run_time_without_job(sample_config, mock_logger):
    scheduler, mock_scheduler = make_scheduler(sample_config, mock_logger)
    scheduler.is_running = True
    mock_scheduler.get_job.return_value = None

    assert scheduler.get_next_run_time() == "No job scheduled"


def test_get_next_run_time_job_without_next_run(sample_config, mock_logger):
    scheduler, mock_scheduler = make_scheduler(sample_config, mock_logger)
    scheduler.is_running = True

    mock_job = MagicMock()
    mock_job.next_run_time = None
    mock_scheduler.get_job.return_value = mock_job

    assert scheduler.get_next_run_time() == "No job scheduled"
