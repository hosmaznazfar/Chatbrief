"""Tests for bot_commands module — language / output_language coverage and rate limiting."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import src.bot_commands
from src.bot_commands import BotCommandHandler
from src.commands.models import CommandResult, CommandStatus
from src.commands.service import CommandService


@pytest.fixture
def english_config(sample_config):
    """sample_config with output_language set to English."""
    sample_config.settings.output_language = "English"
    return sample_config


def _make_update(user_id: int):
    """Return a minimal mock Update with an authorized user."""
    update = MagicMock()
    update.effective_user.id = user_id
    update.message.reply_text = AsyncMock()
    return update


def _make_command_service() -> MagicMock:
    """Return a mocked command service for Telegram adapter tests."""
    service = MagicMock(spec=CommandService)
    service.check_access.return_value = None
    service.digest = AsyncMock()
    service.cleanup = AsyncMock()
    service.status = MagicMock()
    service.help = MagicMock()
    return service


# ---------------------------------------------------------------------------
# setup_bot_menu
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_setup_bot_menu_uses_output_language(english_config, mock_logger):
    """setup_bot_menu command descriptions respect output_language."""
    handler = BotCommandHandler(english_config, mock_logger)
    mock_app = MagicMock()
    mock_app.bot.set_my_commands = AsyncMock()
    handler.app = mock_app

    await handler.setup_bot_menu()

    commands = mock_app.bot.set_my_commands.call_args[0][0]
    descriptions = [cmd.description for cmd in commands]
    joined = " ".join(descriptions)

    assert "Start the bot" in descriptions
    assert "Generate digest for 24 hours" in descriptions
    assert "Delete old digests" in descriptions
    # No Russian
    assert "Начать" not in joined
    assert "Сгенерировать" not in joined


# ---------------------------------------------------------------------------
# handle_digest
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_digest_processing_message_uses_output_language(
    english_config,
    mock_logger,
):
    """handle_digest sends an English processing message."""
    service = _make_command_service()
    service.digest.return_value = CommandResult(
        status=CommandStatus.SUCCESS,
        message="Digest generated successfully.",
    )

    handler = BotCommandHandler(
        english_config,
        mock_logger,
        command_service=service,
    )
    update = _make_update(123456789)

    await handler.handle_digest(update, MagicMock())

    assert (
        update.message.reply_text.await_args_list[0].args[0] == (handler._ui["generating_digest"])
    )

    service.check_access.assert_called_once_with(123456789)
    service.digest.assert_awaited_once_with(
        123456789,
        access_checked=True,
    )


@pytest.mark.asyncio
async def test_handle_digest_success_message_uses_output_language(english_config):
    """Digest handler sends the service success message."""
    service = _make_command_service()
    service.digest.return_value = CommandResult(
        status=CommandStatus.SUCCESS,
        message="Digest generated successfully.",
    )

    handler = BotCommandHandler(
        english_config,
        MagicMock(),
        command_service=service,
    )

    update = _make_update(123)

    await handler.handle_digest(update, MagicMock())

    assert (
        update.message.reply_text.await_args_list[0].args[0] == (handler._ui["generating_digest"])
    )
    assert update.message.reply_text.await_args_list[1].args[0] == (
        "Digest generated successfully."
    )

    service.check_access.assert_called_once_with(123)
    service.digest.assert_awaited_once_with(
        123,
        access_checked=True,
    )


@pytest.mark.asyncio
async def test_handle_digest_error_message_uses_output_language(english_config):
    """Digest handler sends the service error message."""
    service = _make_command_service()
    service.digest.return_value = CommandResult(
        status=CommandStatus.ERROR,
        message="Failed to generate digest.",
    )

    handler = BotCommandHandler(
        english_config,
        MagicMock(),
        command_service=service,
    )

    update = _make_update(123)

    await handler.handle_digest(update, MagicMock())

    assert (
        update.message.reply_text.await_args_list[0].args[0] == (handler._ui["generating_digest"])
    )
    assert update.message.reply_text.await_args_list[1].args[0] == ("Failed to generate digest.")

    service.digest.assert_awaited_once_with(
        123,
        access_checked=True,
    )


# ---------------------------------------------------------------------------
# handle_cleanup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_cleanup_messages_use_output_language(english_config):
    """Cleanup handler sends processing and service result messages."""
    service = _make_command_service()
    service.cleanup.return_value = CommandResult(
        status=CommandStatus.SUCCESS,
        message="Cleanup completed.",
    )

    handler = BotCommandHandler(
        english_config,
        MagicMock(),
        command_service=service,
    )

    update = _make_update(123)

    await handler.handle_cleanup(update, MagicMock())

    assert update.message.reply_text.await_args_list[0].args[0] == (handler._ui["cleaning_up"])
    assert update.message.reply_text.await_args_list[1].args[0] == ("Cleanup completed.")

    service.check_access.assert_called_once_with(123)
    service.cleanup.assert_awaited_once_with(
        123,
        access_checked=True,
    )


# ---------------------------------------------------------------------------
# handle_status
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_status_uses_output_language(english_config, mock_logger):
    """handle_status status message respects output_language."""
    handler = BotCommandHandler(english_config, mock_logger)
    update = _make_update(123456789)

    await handler.handle_status(update, MagicMock())

    status_text = update.message.reply_text.call_args[0][0]
    assert "Telebrief Status" in status_text
    assert "Provider" in status_text
    assert "Model" in status_text
    assert "Enabled" in status_text or "Disabled" in status_text
    # No Russian
    assert "Статус Telebrief" not in status_text
    assert "Провайдер" not in status_text
    assert "Включена" not in status_text


# ---------------------------------------------------------------------------
# handle_help
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_help_uses_output_language(english_config, mock_logger):
    """handle_help text respects output_language."""
    handler = BotCommandHandler(english_config, mock_logger)
    update = _make_update(123456789)

    await handler.handle_help(update, MagicMock())

    help_text = update.message.reply_text.call_args[0][0]
    assert "Commands:" in help_text
    assert "Automatic mode:" in help_text
    assert "Features:" in help_text
    # No Russian structural labels
    assert "Команды:" not in help_text
    assert "Автоматический режим:" not in help_text
    assert "Возможности:" not in help_text


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_digest_rate_limited(english_config):
    """Digest handler replies when the command service rate limits the user."""
    service = _make_command_service()
    service.check_access.return_value = CommandResult(
        status=CommandStatus.RATE_LIMITED,
        message="Please wait before trying again.",
    )

    handler = BotCommandHandler(
        english_config,
        MagicMock(),
        command_service=service,
    )

    update = _make_update(123)

    await handler.handle_digest(update, MagicMock())

    update.message.reply_text.assert_awaited_once_with("Please wait before trying again.")

    service.digest.assert_not_awaited()


@pytest.mark.asyncio
async def test_handle_cleanup_rate_limited(english_config):
    """Cleanup handler replies when the command service rate limits the user."""
    service = _make_command_service()
    service.check_access.return_value = CommandResult(
        status=CommandStatus.RATE_LIMITED,
        message="Please wait before trying again.",
    )

    handler = BotCommandHandler(
        english_config,
        MagicMock(),
        command_service=service,
    )

    update = _make_update(123)

    await handler.handle_cleanup(update, MagicMock())

    update.message.reply_text.assert_awaited_once_with("Please wait before trying again.")

    service.cleanup.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rate_limit_message_uses_configured_language(
    sample_config,
    mock_logger,
):
    """Rate limit message is sent in the configured language."""
    service = _make_command_service()
    service.check_access.return_value = CommandResult(
        status=CommandStatus.RATE_LIMITED,
        message="Пожалуйста, подождите перед повторной попыткой.",
    )

    handler = BotCommandHandler(
        sample_config,
        mock_logger,
        command_service=service,
    )
    update = _make_update(123456789)

    await handler.handle_digest(update, MagicMock())

    update.message.reply_text.assert_awaited_once_with(
        "Пожалуйста, подождите перед повторной попыткой."
    )

    service.digest.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_status_not_rate_limited(english_config, mock_logger):
    """/status is not rate limited — can be called rapidly."""
    handler = BotCommandHandler(english_config, mock_logger)
    update = _make_update(123456789)

    await handler.handle_status(update, MagicMock())
    update.message.reply_text.reset_mock()
    await handler.handle_status(update, MagicMock())

    # Second call should still get the status message, not a rate limit
    texts = [call[0][0] for call in update.message.reply_text.call_args_list]
    assert any("Telebrief Status" in t for t in texts)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_help_not_rate_limited(english_config, mock_logger):
    """/help is not rate limited — can be called rapidly."""
    handler = BotCommandHandler(english_config, mock_logger)
    update = _make_update(123456789)

    await handler.handle_help(update, MagicMock())
    update.message.reply_text.reset_mock()
    await handler.handle_help(update, MagicMock())

    # Second call should still get the help message
    texts = [call[0][0] for call in update.message.reply_text.call_args_list]
    assert any("Commands:" in t for t in texts)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cleanup_rate_limited(
    english_config,
    mock_logger,
):
    """Cleanup handler replies when the command service rate limits the user."""
    service = _make_command_service()
    service.check_access.return_value = CommandResult(
        status=CommandStatus.RATE_LIMITED,
        message="Please wait before trying again.",
    )

    handler = BotCommandHandler(
        english_config,
        mock_logger,
        command_service=service,
    )
    update = _make_update(123456789)

    await handler.handle_cleanup(update, MagicMock())

    update.message.reply_text.assert_awaited_once_with("Please wait before trying again.")

    service.cleanup.assert_not_awaited()


# ---------------------------------------------------------------------------
# Additional branch coverage
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_setup_application(sample_config, mock_logger):
    """setup_application registers all bot command handlers."""
    handler = BotCommandHandler(sample_config, mock_logger)

    mock_app = MagicMock()

    with patch.object(src.bot_commands.Application, "builder") as mock_builder:
        mock_builder.return_value.token.return_value.build.return_value = mock_app

        result = handler.setup_application()

    assert result is mock_app
    assert handler.app is mock_app
    assert mock_app.add_handler.call_count == 5
    mock_logger.info.assert_called_once_with("Bot command handlers registered")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_setup_bot_menu_without_application(sample_config, mock_logger):
    """setup_bot_menu warns when the application is not initialized."""
    handler = BotCommandHandler(sample_config, mock_logger)

    await handler.setup_bot_menu()

    mock_logger.warning.assert_called_once_with(
        "Application not initialized, cannot set up bot menu"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_setup_bot_menu_exception(sample_config, mock_logger):
    """setup_bot_menu logs an error when Telegram rejects the command menu."""
    handler = BotCommandHandler(sample_config, mock_logger)

    mock_app = MagicMock()
    mock_app.bot.set_my_commands = AsyncMock(side_effect=RuntimeError("Telegram error"))
    handler.app = mock_app

    await handler.setup_bot_menu()

    mock_logger.error.assert_called_once_with("Failed to set up bot menu: Telegram error")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_digest_without_user(sample_config, mock_logger):
    """handle_digest returns when the update has no effective user."""
    handler = BotCommandHandler(sample_config, mock_logger)

    update = _make_update(123456789)
    update.effective_user = None

    await handler.handle_digest(update, MagicMock())

    update.message.reply_text.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_digest_without_message(sample_config, mock_logger):
    """handle_digest returns when the update has no message."""
    handler = BotCommandHandler(sample_config, mock_logger)

    update = _make_update(123456789)
    update.message = None

    await handler.handle_digest(update, MagicMock())


@pytest.mark.asyncio
async def test_handle_digest_unauthorized(english_config):
    """Digest handler ignores unauthorized users."""
    service = _make_command_service()
    service.check_access.return_value = CommandResult(
        status=CommandStatus.UNAUTHORIZED,
        message="",
    )

    handler = BotCommandHandler(
        english_config,
        MagicMock(),
        command_service=service,
    )

    update = _make_update(456)

    await handler.handle_digest(update, MagicMock())

    update.message.reply_text.assert_not_awaited()
    service.digest.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_digest_exception(
    sample_config,
    mock_logger,
):
    """handle_digest forwards an error returned by the command service."""
    sample_config.settings.target_user_id = 123

    service = _make_command_service()
    service.digest.return_value = CommandResult(
        status=CommandStatus.ERROR,
        message="An error occurred while generating the digest.",
    )

    handler = BotCommandHandler(
        sample_config,
        mock_logger,
        command_service=service,
    )
    update = _make_update(123)

    await handler.handle_digest(update, MagicMock())

    assert (
        update.message.reply_text.await_args_list[0].args[0] == (handler._ui["generating_digest"])
    )
    assert update.message.reply_text.await_args_list[1].args[0] == (
        "An error occurred while generating the digest."
    )

    service.digest.assert_awaited_once_with(
        123,
        access_checked=True,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_cleanup_without_user(sample_config, mock_logger):
    """handle_cleanup returns when the update has no effective user."""
    handler = BotCommandHandler(sample_config, mock_logger)

    update = _make_update(123456789)
    update.effective_user = None

    await handler.handle_cleanup(update, MagicMock())

    update.message.reply_text.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_cleanup_without_message(sample_config, mock_logger):
    """handle_cleanup returns when the update has no message."""
    handler = BotCommandHandler(sample_config, mock_logger)

    update = _make_update(123456789)
    update.message = None

    await handler.handle_cleanup(update, MagicMock())


@pytest.mark.asyncio
async def test_handle_cleanup_unauthorized(english_config):
    """Cleanup handler ignores unauthorized users."""
    service = _make_command_service()
    service.check_access.return_value = CommandResult(
        status=CommandStatus.UNAUTHORIZED,
        message="",
    )

    handler = BotCommandHandler(
        english_config,
        MagicMock(),
        command_service=service,
    )

    update = _make_update(456)

    await handler.handle_cleanup(update, MagicMock())

    update.message.reply_text.assert_not_awaited()
    service.cleanup.assert_not_awaited()


@pytest.mark.asyncio
async def test_handle_cleanup_failure(english_config):
    """Cleanup handler forwards a cleanup error result."""
    service = _make_command_service()
    service.cleanup.return_value = CommandResult(
        status=CommandStatus.ERROR,
        message="Some digests could not be removed.",
    )

    handler = BotCommandHandler(
        english_config,
        MagicMock(),
        command_service=service,
    )

    update = _make_update(123)

    await handler.handle_cleanup(update, MagicMock())

    assert update.message.reply_text.await_args_list[0].args[0] == (handler._ui["cleaning_up"])
    assert update.message.reply_text.await_args_list[1].args[0] == (
        "Some digests could not be removed."
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_cleanup_exception(
    sample_config,
    mock_logger,
):
    """handle_cleanup forwards an error returned by the command service."""
    sample_config.settings.target_user_id = 123

    service = _make_command_service()
    service.cleanup.return_value = CommandResult(
        status=CommandStatus.ERROR,
        message="An error occurred during cleanup.",
    )

    handler = BotCommandHandler(
        sample_config,
        mock_logger,
        command_service=service,
    )
    update = _make_update(123)

    await handler.handle_cleanup(update, MagicMock())

    assert update.message.reply_text.await_args_list[0].args[0] == (handler._ui["cleaning_up"])
    assert update.message.reply_text.await_args_list[1].args[0] == (
        "An error occurred during cleanup."
    )

    service.cleanup.assert_awaited_once_with(
        123,
        access_checked=True,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_status_without_user(sample_config, mock_logger):
    """handle_status returns when the update has no effective user."""
    handler = BotCommandHandler(sample_config, mock_logger)

    update = _make_update(123456789)
    update.effective_user = None

    await handler.handle_status(update, MagicMock())

    update.message.reply_text.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_status_without_message(sample_config, mock_logger):
    """handle_status returns when the update has no message."""
    handler = BotCommandHandler(sample_config, mock_logger)

    update = _make_update(123456789)
    update.message = None

    await handler.handle_status(update, MagicMock())


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_status_unauthorized(
    sample_config,
    mock_logger,
):
    """handle_status silently ignores unauthorized users."""
    sample_config.settings.target_user_id = 123

    service = _make_command_service()
    service.status.return_value = CommandResult(
        status=CommandStatus.UNAUTHORIZED,
        message="",
    )

    handler = BotCommandHandler(
        sample_config,
        mock_logger,
        command_service=service,
    )
    update = _make_update(456)

    await handler.handle_status(update, MagicMock())

    update.message.reply_text.assert_not_awaited()
    service.status.assert_called_once_with(456)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_status_with_scheduler(sample_config, mock_logger):
    """handle_status includes the scheduler next-run time."""
    sample_config.settings.target_user_id = 123

    scheduler = MagicMock()
    scheduler.get_next_run_time.return_value = "2026-09-07 08:00:00 UTC"

    handler = BotCommandHandler(sample_config, mock_logger, scheduler)
    update = _make_update(123)

    await handler.handle_status(update, MagicMock())

    scheduler.get_next_run_time.assert_called_once()

    status_text = update.message.reply_text.call_args.args[0]

    assert "2026-09-07 08:00:00 UTC" in status_text


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_help_without_user(sample_config, mock_logger):
    """handle_help returns when the update has no effective user."""
    handler = BotCommandHandler(sample_config, mock_logger)

    update = _make_update(123456789)
    update.effective_user = None

    await handler.handle_help(update, MagicMock())

    update.message.reply_text.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_help_without_message(sample_config, mock_logger):
    """handle_help returns when the update has no message."""
    handler = BotCommandHandler(sample_config, mock_logger)

    update = _make_update(123456789)
    update.message = None

    await handler.handle_help(update, MagicMock())


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_help_unauthorized(sample_config, mock_logger):
    """handle_help silently ignores unauthorized users."""
    sample_config.settings.target_user_id = 123

    handler = BotCommandHandler(sample_config, mock_logger)
    update = _make_update(456)

    await handler.handle_help(update, MagicMock())

    update.message.reply_text.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_without_application(sample_config, mock_logger):
    """run initializes the application when needed."""
    handler = BotCommandHandler(sample_config, mock_logger)

    mock_app = MagicMock()
    mock_app.updater = MagicMock()
    mock_app.initialize = AsyncMock()
    mock_app.start = AsyncMock()
    mock_app.updater.start_polling = AsyncMock()

    def setup_application():
        handler.app = mock_app
        return mock_app

    with patch.object(handler, "setup_application", side_effect=setup_application) as mock_setup:
        with patch.object(handler, "setup_bot_menu", new=AsyncMock()):
            await handler.run()

    mock_setup.assert_called_once()
    mock_app.initialize.assert_awaited_once()
    mock_app.start.assert_awaited_once()
    mock_app.updater.start_polling.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_application_initialization_failure(sample_config, mock_logger):
    """run raises when the application has no updater."""
    handler = BotCommandHandler(sample_config, mock_logger)

    mock_app = MagicMock()
    mock_app.updater = None

    with patch.object(handler, "setup_application", return_value=mock_app):
        with pytest.raises(RuntimeError, match="Application failed to initialize"):
            await handler.run()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stop_running_application(sample_config, mock_logger):
    """stop shuts down a running bot application."""
    handler = BotCommandHandler(sample_config, mock_logger)

    mock_app = MagicMock()
    mock_app.updater = MagicMock()
    mock_app.updater.stop = AsyncMock()
    mock_app.stop = AsyncMock()
    mock_app.shutdown = AsyncMock()
    handler.app = mock_app

    await handler.stop()

    mock_app.updater.stop.assert_awaited_once()
    mock_app.stop.assert_awaited_once()
    mock_app.shutdown.assert_awaited_once()
    mock_logger.info.assert_called_once_with("Stopping bot...")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stop_without_application(sample_config, mock_logger):
    """stop does nothing when no application exists."""
    handler = BotCommandHandler(sample_config, mock_logger)

    await handler.stop()

    mock_logger.info.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stop_without_updater(sample_config, mock_logger):
    """stop does nothing when the application has no updater."""
    handler = BotCommandHandler(sample_config, mock_logger)

    mock_app = MagicMock()
    mock_app.updater = None
    handler.app = mock_app

    await handler.stop()

    mock_logger.info.assert_not_called()
