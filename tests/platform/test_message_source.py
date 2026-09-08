"""Tests for the platform-neutral message source contract."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import src.platforms.telegram
from src.message import Message
from src.platforms.telegram import TelegramMessageSource

TEST_MESSAGE_TIME = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
TEST_LOOKBACK_TIME = datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc)


async def async_messages(messages):
    """Yield messages through an async iterator."""
    for message in messages:
        yield message


@pytest.fixture
def message_source(sample_config, mock_logger):
    """Create a Telegram message source with a mocked Telegram client."""
    with patch.object(src.platforms.telegram, "TelegramClient") as mock_client:
        mock_client.return_value = MagicMock()
        source = TelegramMessageSource(sample_config, mock_logger)

    return source


@pytest.mark.asyncio
async def test_fetch_messages_success(message_source):
    message_source.fetch_channel_messages = AsyncMock(return_value=[])

    result = await message_source.fetch_messages(hours=24)

    assert isinstance(result, dict)
    assert all(isinstance(messages, list) for messages in result.values())


@pytest.mark.asyncio
async def test_fetch_channel_messages_text(message_source, sample_config):
    message = MagicMock()
    message.id = 1
    message.text = "Hello world"
    message.date = TEST_MESSAGE_TIME
    message.sender_id = 123
    message.media = None
    message.get_sender = AsyncMock(return_value=MagicMock())

    message_source.client.get_entity = AsyncMock(return_value=MagicMock())
    message_source.client.iter_messages = MagicMock(
        return_value=async_messages([message]),
    )

    with patch.object(
        message_source,
        "_get_sender_name",
        return_value="Test User",
    ):
        result = await message_source.fetch_channel_messages(
            sample_config.channels[0],
            TEST_LOOKBACK_TIME,
        )

    assert len(result) == 1
    assert isinstance(result[0], Message)
    assert result[0].text == "Hello world"
    assert result[0].channel_name == "Test Channel"
    assert result[0].has_media is False
    assert result[0].media_type == ""


@pytest.mark.asyncio
async def test_fetch_channel_messages_media_only(message_source, sample_config):
    message = MagicMock()
    message.id = 1
    message.text = ""
    message.date = TEST_MESSAGE_TIME
    message.sender_id = 123
    message.media = MagicMock()
    message.get_sender = AsyncMock(return_value=MagicMock())

    message_source.client.get_entity = AsyncMock(return_value=MagicMock())
    message_source.client.iter_messages = MagicMock(
        return_value=async_messages([message]),
    )

    with (
        patch.object(
            message_source,
            "_get_sender_name",
            return_value="Test User",
        ),
        patch.object(
            message_source,
            "_get_media_type",
            return_value="Фото",
        ),
    ):
        result = await message_source.fetch_channel_messages(
            sample_config.channels[0],
            TEST_LOOKBACK_TIME,
        )

    assert len(result) == 1
    assert isinstance(result[0], Message)
    assert result[0].has_media is True
    assert result[0].media_type == "Фото"


@pytest.mark.asyncio
async def test_fetch_channel_messages_empty_without_media(message_source, sample_config):
    message = MagicMock()
    message.id = 1
    message.text = ""
    message.date = TEST_MESSAGE_TIME
    message.sender_id = 123
    message.media = None
    message.get_sender = AsyncMock(return_value=MagicMock())

    message_source.client.get_entity = AsyncMock(return_value=MagicMock())
    message_source.client.iter_messages = MagicMock(
        return_value=async_messages([message]),
    )

    result = await message_source.fetch_channel_messages(
        sample_config.channels[0],
        TEST_LOOKBACK_TIME,
    )

    assert result == []


@pytest.mark.asyncio
async def test_fetch_channel_messages_stops_at_lookback(message_source, sample_config):
    message = MagicMock()
    message.id = 1
    message.message = "Old message"
    message.date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    message.sender_id = 123
    message.media = None

    message_source.client.get_entity = AsyncMock(return_value=MagicMock())
    message_source.client.iter_messages = MagicMock(
        return_value=async_messages([message]),
    )

    result = await message_source.fetch_channel_messages(
        sample_config.channels[0],
        datetime(2025, 1, 1, tzinfo=timezone.utc),
    )

    assert result == []


@pytest.mark.asyncio
async def test_fetch_channel_messages_sorts_messages(message_source, sample_config):
    older = MagicMock()
    older.id = 1
    older.text = "older"
    older.date = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    older.sender_id = 123
    older.media = None
    older.get_sender = AsyncMock(return_value=MagicMock())

    newer = MagicMock()
    newer.id = 2
    newer.text = "newer"
    newer.date = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    newer.sender_id = 123
    newer.media = None
    newer.get_sender = AsyncMock(return_value=MagicMock())

    message_source.client.get_entity = AsyncMock(return_value=MagicMock())
    message_source.client.iter_messages = MagicMock(
        return_value=async_messages([newer, older]),
    )

    result = await message_source.fetch_channel_messages(
        sample_config.channels[0],
        datetime(2025, 1, 1, tzinfo=timezone.utc),
    )

    assert [message.text for message in result] == ["older", "newer"]
