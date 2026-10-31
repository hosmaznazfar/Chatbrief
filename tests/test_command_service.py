"""Tests for the platform-neutral command service."""

# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import chatbrief.commands.service
from chatbrief.commands.models import CommandStatus
from chatbrief.commands.service import CommandService


@pytest.fixture
def english_config(sample_config):
    """sample_config with output_language set to English."""
    sample_config.settings.output_language = "English"
    return sample_config


def _make_command_service(config, logger, source=None, sender=None, scheduler=None):
    """Create a command service with injected platform-neutral dependencies."""
    return CommandService(
        config,
        logger,
        source if source is not None else MagicMock(),
        sender if sender is not None else MagicMock(),
        scheduler,
    )


@pytest.mark.unit
def test_is_authorized(sample_config, mock_logger):
    """CommandService authorizes the configured target user."""
    sample_config.settings.target_user_id = 123

    service = _make_command_service(sample_config, mock_logger)

    assert service.is_authorized(123)
    assert not service.is_authorized(456)


@pytest.mark.unit
def test_unauthorized_command_returns_unauthorized_result(sample_config, mock_logger):
    """Unauthorized users receive an unauthorized command result."""
    sample_config.settings.target_user_id = 123

    service = _make_command_service(sample_config, mock_logger)

    result = service.status(456)

    assert result.status is CommandStatus.UNAUTHORIZED
    assert result.message == ""

    mock_logger.warning.assert_called_once_with(
        "Unauthorized command attempt from user %s",
        456,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_digest_success(english_config, mock_logger):
    """digest returns a successful result when generation succeeds."""
    english_config.settings.target_user_id = 123

    source = MagicMock()
    sender = MagicMock()
    service = _make_command_service(english_config, mock_logger, source=source, sender=sender)
    generate = AsyncMock(return_value=True)

    with patch.object(
        chatbrief.commands.service,
        "generate_and_send_digest",
        new=generate,
    ):
        result = await service.digest(123)

    generate.assert_awaited_once_with(
        config=english_config,
        logger=mock_logger,
        source=source,
        sender=sender,
        hours=24,
        user_id=123,
    )
    assert result.status is CommandStatus.SUCCESS
    assert result.message == service._ui["digest_done"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_digest_failure(english_config, mock_logger):
    """digest returns an error result when generation fails."""
    english_config.settings.target_user_id = 123

    service = _make_command_service(english_config, mock_logger)

    with patch.object(
        chatbrief.commands.service,
        "generate_and_send_digest",
        new=AsyncMock(return_value=False),
    ):
        result = await service.digest(123)

    assert result.status is CommandStatus.ERROR
    assert result.message == service._ui["digest_error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_digest_exception(english_config, mock_logger):
    """digest returns an error result when generation raises."""
    english_config.settings.target_user_id = 123

    service = _make_command_service(english_config, mock_logger)

    with patch.object(
        chatbrief.commands.service,
        "generate_and_send_digest",
        new=AsyncMock(side_effect=RuntimeError("digest failed")),
    ):
        result = await service.digest(123)

    assert result.status is CommandStatus.ERROR
    assert result.message == service._ui["digest_exception"]

    mock_logger.error.assert_called_once()
    call_args = mock_logger.error.call_args

    assert call_args.args[0] == "Error generating digest: %s"
    assert str(call_args.args[1]) == "digest failed"
    assert call_args.kwargs["exc_info"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_digest_rate_limited(english_config, mock_logger):
    """Rapid successive digest commands are rate limited."""
    english_config.settings.target_user_id = 123

    service = _make_command_service(english_config, mock_logger)

    with patch.object(
        chatbrief.commands.service,
        "generate_and_send_digest",
        new=AsyncMock(return_value=True),
    ):
        first = await service.digest(123)
        second = await service.digest(123)

    assert first.status is CommandStatus.SUCCESS
    assert second.status is CommandStatus.RATE_LIMITED
    assert second.message == service._ui["rate_limited"]


@pytest.mark.unit
def test_status_returns_success(english_config, mock_logger):
    """status returns the configured application status."""
    english_config.settings.target_user_id = 123

    service = _make_command_service(english_config, mock_logger)

    result = service.status(123)

    assert result.status is CommandStatus.SUCCESS
    assert "Chatbrief Status" in result.message
    assert "Provider" in result.message
    assert "Model" in result.message


@pytest.mark.unit
def test_status_includes_scheduler_next_run(english_config, mock_logger):
    """The application service adds the scheduler's next run to status output."""
    english_config.settings.target_user_id = 123
    scheduler = MagicMock()
    scheduler.get_next_run_time.return_value = "2026-09-07 08:00:00 UTC"
    service = _make_command_service(english_config, mock_logger, scheduler=scheduler)

    result = service.status(123)

    assert "2026-09-07 08:00:00 UTC" in result.message
    scheduler.get_next_run_time.assert_called_once_with()


@pytest.mark.unit
def test_help_returns_success(english_config, mock_logger):
    """help returns localized help text."""
    english_config.settings.target_user_id = 123

    service = _make_command_service(english_config, mock_logger)

    result = service.help(123)

    assert result.status is CommandStatus.SUCCESS
    assert "Commands:" in result.message
    assert "Automatic mode:" in result.message
    assert "Features:" in result.message


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cleanup_success(english_config, mock_logger):
    """cleanup returns success when old digests are removed."""
    english_config.settings.target_user_id = 123

    service = _make_command_service(english_config, mock_logger)

    mock_sender = MagicMock()
    mock_sender.cleanup_old_digests = AsyncMock(return_value=True)
    service.sender = mock_sender

    result = await service.cleanup(123)

    assert result.status is CommandStatus.SUCCESS
    assert result.message == service._ui["cleanup_done"]
    mock_sender.cleanup_old_digests.assert_awaited_once_with(123)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cleanup_failure(english_config, mock_logger):
    """cleanup returns an error result when cleanup is unsuccessful."""
    english_config.settings.target_user_id = 123

    service = _make_command_service(english_config, mock_logger)

    mock_sender = MagicMock()
    mock_sender.cleanup_old_digests = AsyncMock(return_value=False)
    service.sender = mock_sender

    result = await service.cleanup(123)

    assert result.status is CommandStatus.ERROR
    assert result.message == service._ui["cleanup_partial"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cleanup_rate_limited(english_config, mock_logger):
    """Rapid successive cleanup commands are rate limited."""
    english_config.settings.target_user_id = 123

    service = _make_command_service(english_config, mock_logger)

    mock_sender = MagicMock()
    mock_sender.cleanup_old_digests = AsyncMock(return_value=True)
    service.sender = mock_sender

    first = await service.cleanup(123)
    second = await service.cleanup(123)

    assert first.status is CommandStatus.SUCCESS
    assert second.status is CommandStatus.RATE_LIMITED
    assert second.message == service._ui["rate_limited"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rate_limit_resets_after_cooldown(english_config, mock_logger):
    """A command is allowed again after the rate-limit cooldown."""
    english_config.settings.target_user_id = 123

    service = _make_command_service(english_config, mock_logger)

    with (
        patch.object(
            chatbrief.commands.service,
            "generate_and_send_digest",
            new=AsyncMock(return_value=True),
        ),
        patch.object(
            chatbrief.commands.service.time,
            "monotonic",
            side_effect=[0.0, 10.0, 31.0],
        ),
    ):
        first = await service.digest(123)
        second = await service.digest(123)
        third = await service.digest(123)

    assert first.status is CommandStatus.SUCCESS
    assert second.status is CommandStatus.RATE_LIMITED
    assert third.status is CommandStatus.SUCCESS
