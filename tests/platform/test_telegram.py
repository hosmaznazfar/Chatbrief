"""Tests for the Telegram message source."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telethon.errors import ChannelPrivateError, FloodWaitError
from telethon.tl.types import Document, MessageMediaDocument

import src.platforms.telegram
from src.platforms.telegram import TelegramMessageSource

TEST_MESSAGE_TIME = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
TEST_LOOKBACK_TIME = datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc)


def make_source(sample_config, mock_logger):

    with patch.object(src.platforms.telegram, "TelegramClient") as mock_client:
        mock_client.return_value = MagicMock()
        source = TelegramMessageSource(sample_config, mock_logger)

    return source


def test_get_media_type_without_media(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.media = None

    assert source._get_media_type(message) == ""


def test_get_media_type_photo(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.media = MagicMock()
    type(message.media).__name__ = "MessageMediaPhoto"

    assert source._get_media_type(message) == source._ui["media_photo"]


def test_get_media_type_video(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.media = MagicMock()
    type(message.media).__name__ = "MessageMediaVideo"

    assert source._get_media_type(message) == source._ui["media_video"]


def test_get_media_type_voice(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.media = MagicMock()
    type(message.media).__name__ = "MessageMediaVoice"

    assert source._get_media_type(message) == source._ui["media_voice"]


def test_get_media_type_poll(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.media = MagicMock()
    type(message.media).__name__ = "MessageMediaPoll"

    assert source._get_media_type(message) == source._ui["media_poll"]


def test_get_media_type_geo(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.media = MagicMock()
    type(message.media).__name__ = "MessageMediaGeo"

    assert source._get_media_type(message) == source._ui["media_geo"]


def test_get_document_media_type_video(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    document = Document(
        id=1,
        access_hash=1,
        file_reference=b"",
        date=None,
        mime_type="video/mp4",
        size=100,
        dc_id=1,
        attributes=[],
    )
    media = MessageMediaDocument(document=document)

    assert source._get_document_media_type(media) == source._ui["media_video"]


def test_get_document_media_type_audio(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    document = Document(
        id=1,
        access_hash=1,
        file_reference=b"",
        date=None,
        mime_type="audio/mpeg",
        size=100,
        dc_id=1,
        attributes=[],
    )
    media = MessageMediaDocument(document=document)

    assert source._get_document_media_type(media) == source._ui["media_audio"]


def test_get_document_media_type_other(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    document = Document(
        id=1,
        access_hash=1,
        file_reference=b"",
        date=None,
        mime_type="application/pdf",
        size=100,
        dc_id=1,
        attributes=[],
    )
    media = MessageMediaDocument(document=document)

    assert source._get_document_media_type(media) == source._ui["media_document"]


def test_get_document_media_type_non_document(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    media = MagicMock()
    media.document = MagicMock()

    assert source._get_document_media_type(media) == source._ui["media_video"]


@pytest.mark.asyncio
async def test_get_sender_name_first_and_last_name(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    sender = MagicMock()
    sender.first_name = "John"
    sender.last_name = "Doe"

    message = MagicMock()
    message.get_sender = AsyncMock(return_value=sender)

    assert await source._get_sender_name(message) == "John Doe"


@pytest.mark.asyncio
async def test_get_sender_name_first_name_only(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    sender = MagicMock()
    sender.first_name = "John"
    sender.last_name = None

    message = MagicMock()
    message.get_sender = AsyncMock(return_value=sender)

    assert await source._get_sender_name(message) == "John"


@pytest.mark.asyncio
async def test_get_sender_name_title(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    sender = MagicMock(spec=["title"])
    sender.title = "Test Channel"

    message = MagicMock()
    message.get_sender = AsyncMock(return_value=sender)

    assert await source._get_sender_name(message) == "Test Channel"


@pytest.mark.asyncio
async def test_get_sender_name_username(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    sender = MagicMock(spec=["username"])
    sender.username = "testuser"

    message = MagicMock()
    message.get_sender = AsyncMock(return_value=sender)

    assert await source._get_sender_name(message) == "@testuser"


@pytest.mark.asyncio
async def test_get_sender_name_unknown_sender(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.get_sender = AsyncMock(return_value=None)

    assert await source._get_sender_name(message) == "Unknown"


@pytest.mark.asyncio
async def test_get_sender_name_sender_without_name_attributes(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    sender = MagicMock(spec=[])

    message = MagicMock()
    message.get_sender = AsyncMock(return_value=sender)

    assert await source._get_sender_name(message) == "Unknown"


@pytest.mark.asyncio
async def test_get_sender_name_error(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.get_sender = AsyncMock(side_effect=RuntimeError("Telegram error"))

    assert await source._get_sender_name(message) == "Unknown"


@pytest.mark.asyncio
async def test_generate_message_link_public_channel(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    entity = MagicMock()
    entity.username = "testchannel"

    assert await source._generate_message_link(entity, 123) == ("https://t.me/testchannel/123")


@pytest.mark.asyncio
async def test_generate_message_link_private_channel(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    entity = MagicMock()
    entity.username = None
    entity.id = -1001234567890

    assert await source._generate_message_link(entity, 456) == ("https://t.me/c/1234567890/456")


@pytest.mark.asyncio
async def test_generate_message_link_without_entity_info(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    entity = MagicMock(spec=[])

    assert await source._generate_message_link(entity, 789) == "#"


@pytest.mark.asyncio
async def test_connect_missing_session(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    with patch.object(src.platforms.telegram.os.path, "exists", return_value=False):
        with pytest.raises(RuntimeError, match="Telegram user session not found"):
            await source.connect()


@pytest.mark.asyncio
async def test_connect_unauthorized(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    source.client.connect = AsyncMock()
    source.client.is_user_authorized = AsyncMock(return_value=False)

    with patch.object(src.platforms.telegram.os.path, "exists", return_value=True):
        with pytest.raises(RuntimeError, match="not authorized"):
            await source.connect()


@pytest.mark.asyncio
async def test_connect_success(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    source.client.connect = AsyncMock()
    source.client.is_user_authorized = AsyncMock(return_value=True)
    source.client.get_dialogs = AsyncMock(return_value=[MagicMock(), MagicMock()])

    with patch.object(src.platforms.telegram.os.path, "exists", return_value=True):
        await source.connect()

    source.client.connect.assert_awaited_once()
    source.client.is_user_authorized.assert_awaited_once()
    source.client.get_dialogs.assert_awaited_once()
    mock_logger.info.assert_any_call("Connected to Telegram User API")


@pytest.mark.asyncio
async def test_connect_dialog_cache_failure(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    source.client.connect = AsyncMock()
    source.client.is_user_authorized = AsyncMock(return_value=True)
    source.client.get_dialogs = AsyncMock(side_effect=RuntimeError("dialog cache failed"))

    with patch.object(src.platforms.telegram.os.path, "exists", return_value=True):
        await source.connect()

    source.client.connect.assert_awaited_once()
    source.client.is_user_authorized.assert_awaited_once()
    source.client.get_dialogs.assert_awaited_once()
    mock_logger.warning.assert_called_once_with("Could not cache dialogs: dialog cache failed")


@pytest.mark.asyncio
async def test_disconnect(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    source.client.disconnect = MagicMock()

    await source.disconnect()

    source.client.disconnect.assert_called_once_with()
    mock_logger.info.assert_called_with("Disconnected from Telegram")


@pytest.mark.asyncio
async def test_fetch_messages_channel_private_error(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    source.fetch_channel_messages = AsyncMock(side_effect=ChannelPrivateError(request=MagicMock()))

    result = await source.fetch_messages(hours=24)

    assert result == {
        "Test Channel": [],
        "Private Group": [],
    }

    mock_logger.warning.assert_called()


@pytest.mark.asyncio
async def test_fetch_messages_flood_wait_retry(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    expected_messages = [MagicMock()]
    source.fetch_channel_messages = AsyncMock(
        side_effect=[
            FloodWaitError(request=MagicMock(), capture=2),
            expected_messages,
            expected_messages,
        ]
    )

    with patch.object(
        src.platforms.telegram.asyncio, "sleep", new_callable=AsyncMock
    ) as mock_sleep:
        result = await source.fetch_messages(hours=24)

    assert result == {
        "Test Channel": expected_messages,
        "Private Group": expected_messages,
    }
    mock_sleep.assert_awaited_once_with(2)
    assert source.fetch_channel_messages.await_count == 3


@pytest.mark.asyncio
async def test_fetch_messages_flood_wait_retry_failure(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    source.fetch_channel_messages = AsyncMock(
        side_effect=FloodWaitError(request=MagicMock(), capture=2)
    )

    with patch.object(src.platforms.telegram.asyncio, "sleep", new_callable=AsyncMock):
        result = await source.fetch_messages(hours=24)

    assert result == {
        "Test Channel": [],
        "Private Group": [],
    }
    assert mock_logger.error.call_count == 2


@pytest.mark.asyncio
async def test_fetch_messages_entity_not_found(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    source.fetch_channel_messages = AsyncMock(
        side_effect=ValueError("Could not find the input entity")
    )

    result = await source.fetch_messages(hours=24)

    assert result == {
        "Test Channel": [],
        "Private Group": [],
    }
    assert mock_logger.error.call_count == 2


@pytest.mark.asyncio
async def test_fetch_messages_other_value_error(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    source.fetch_channel_messages = AsyncMock(side_effect=ValueError("Some other error"))

    result = await source.fetch_messages(hours=24)

    assert result == {
        "Test Channel": [],
        "Private Group": [],
    }
    assert mock_logger.error.call_count == 2


@pytest.mark.asyncio
async def test_fetch_messages_unexpected_error(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    source.fetch_channel_messages = AsyncMock(side_effect=RuntimeError("unexpected error"))

    result = await source.fetch_messages(hours=24)

    assert result == {
        "Test Channel": [],
        "Private Group": [],
    }
    assert mock_logger.error.call_count == 2


@pytest.mark.asyncio
async def test_fetch_channel_messages_error(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    source.client.get_entity = AsyncMock(side_effect=RuntimeError("Telegram error"))

    with pytest.raises(RuntimeError, match="Telegram error"):
        await source.fetch_channel_messages(
            sample_config.channels[0],
            TEST_MESSAGE_TIME,
        )

    mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_channel_messages_private_entity(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.date = TEST_MESSAGE_TIME
    message.text = "Private message"
    message.media = None
    message.id = 456
    message.get_sender = AsyncMock(return_value=MagicMock())

    entity = MagicMock(spec=["id"])
    entity.id = -1001234567890

    source.client.get_entity = AsyncMock(return_value=entity)

    async def iter_messages(*args, **kwargs):
        yield message

    with patch.object(source.client, "iter_messages", side_effect=iter_messages):
        result = await source.fetch_channel_messages(
            sample_config.channels[1],
            TEST_LOOKBACK_TIME,
        )

    assert len(result) == 1
    assert result[0].link == "https://t.me/c/1234567890/456"


def test_get_media_type_audio(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.media = MagicMock()
    type(message.media).__name__ = "MessageMediaAudio"

    assert source._get_media_type(message) == source._ui["media_voice"]


def test_get_media_type_location(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.media = MagicMock()
    type(message.media).__name__ = "MessageMediaLocation"

    assert source._get_media_type(message) == source._ui["media_geo"]


def test_get_media_type_other(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    message = MagicMock()
    message.media = MagicMock()
    type(message.media).__name__ = "MessageMediaOther"

    assert source._get_media_type(message) == source._ui["media_other"]


@pytest.mark.asyncio
async def test_generate_message_link_error(sample_config, mock_logger):
    source = make_source(sample_config, mock_logger)

    entity = MagicMock()
    type(entity).username = property(lambda self: (_ for _ in ()).throw(RuntimeError("error")))

    assert await source._generate_message_link(entity, 123) == "#"
