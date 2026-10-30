"""Tests for platform component construction."""

from unittest.mock import MagicMock

import pytest

from chatbrief.config.models import Platform
from chatbrief.platforms import builder as platform_builder
from chatbrief.platforms.builder import PlatformBuilder


@pytest.mark.unit
def test_create_services_uses_telegram_adapters(sample_config, mock_logger, monkeypatch):
    source = MagicMock()
    sender = MagicMock()
    source_factory = MagicMock(return_value=source)
    sender_factory = MagicMock(return_value=sender)
    monkeypatch.setattr(platform_builder, "TelegramMessageSource", source_factory)
    monkeypatch.setattr(platform_builder, "TelegramMessageSender", sender_factory)

    result = PlatformBuilder(sample_config, mock_logger).create_services()

    assert result == (source, sender)
    source_factory.assert_called_once_with(sample_config, mock_logger)
    sender_factory.assert_called_once_with(sample_config, mock_logger)


@pytest.mark.unit
def test_create_services_rejects_unimplemented_bale(sample_config, mock_logger):
    sample_config.platform = Platform.BALE

    with pytest.raises(NotImplementedError, match="Bale"):
        PlatformBuilder(sample_config, mock_logger).create_services()


@pytest.mark.unit
def test_create_bot_injects_command_service_and_sets_up_application(
    sample_config, mock_logger, monkeypatch
):
    bot = MagicMock()
    bot_factory = MagicMock(return_value=bot)
    monkeypatch.setattr(platform_builder, "TelegramBot", bot_factory)
    command_service = MagicMock()

    result = PlatformBuilder(sample_config, mock_logger).create_bot(command_service)

    assert result is bot
    bot_factory.assert_called_once_with(
        config=sample_config,
        logger=mock_logger,
        command_service=command_service,
    )
    bot.setup_application.assert_called_once_with()


@pytest.mark.unit
def test_create_bot_rejects_unimplemented_bale(sample_config, mock_logger):
    sample_config.platform = Platform.BALE

    with pytest.raises(NotImplementedError, match="Bale"):
        PlatformBuilder(sample_config, mock_logger).create_bot(MagicMock())
