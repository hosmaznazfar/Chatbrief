"""
Telegram message source using Telethon.
"""

import asyncio
import logging
import os
from collections.abc import Awaitable
from datetime import datetime, timedelta, timezone
from typing import Any, cast

from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, FloodWaitError
from telethon.tl import types as tl_types
from telethon.tl.patched import Message as TelegramMessage

from chatbrief.config.loader import load_config
from chatbrief.config.models import ChannelConfig, Config
from chatbrief.message import Message
from chatbrief.platforms.base import MessageSource
from chatbrief.ui_strings import get_ui_strings
from chatbrief.utils import setup_logging


class TelegramMessageSource(MessageSource):
    """Collects messages from Telegram channels using Telethon."""

    def __init__(self, config: Config, logger: logging.Logger):
        """
        Initialize message collector.

        Args:
            config: Application configuration
            logger: Logger instance.
        """
        self.config = config
        self.logger = logger
        self._ui = get_ui_strings(config.settings.output_language)
        self.client = TelegramClient(
            "sessions/user",
            config.telegram_api_id,
            config.telegram_api_hash,
        )

    async def connect(self) -> None:
        """Connect to Telegram using an existing user session.

        Requires a pre-authenticated session file at sessions/user.session.
        Create one by running:
            uv run python -m chatbrief.platforms.telegram.telegram_source
        """
        session_path = "sessions/user.session"

        if not os.path.exists(session_path):
            raise RuntimeError(
                f"Telegram user session not found at '{session_path}'. "
                "Create one by running: "
                "uv run python -m chatbrief.platforms.telegram.telegram_source"
            )

        await self.client.connect()

        if not await self.client.is_user_authorized():
            raise RuntimeError(
                "Telegram user session exists but is not authorized. "
                "Re-authenticate by running: "
                "uv run python -m chatbrief.platforms.telegram.telegram_source"
            )

        self.logger.info("Connected to Telegram User API")

        # Cache all dialogs to populate entity cache.
        try:
            dialogs = await self.client.get_dialogs()
            self.logger.info(f"Cached {len(dialogs)} dialogs for entity resolution")
        except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            self.logger.warning(f"Could not cache dialogs: {exc}")

    async def disconnect(self) -> None:
        """Disconnect from Telegram."""
        # Telethon's disconnect() is a sync/async hybrid. When called from
        # this async method, the event loop is running and the result is
        # awaitable at runtime.
        disconnect_result = self.client.disconnect()
        await cast(Awaitable[None], cast(object, disconnect_result))

        self.logger.info("Disconnected from Telegram")

    async def fetch_messages(self, hours: int = 24) -> dict[str, list[Message]]:
        """
        Fetch messages from all configured channels.

        Args:
            hours: Number of hours to look back.

        Returns:
            Dictionary mapping channel names to lists of messages.
        """
        self.logger.info(
            f"Fetching messages from {len(self.config.channels)} channels "
            f"(default lookback: {hours}h; individual channels may override)"
        )

        all_messages: dict[str, list[Message]] = {}
        now = datetime.now(timezone.utc)

        for channel_config in self.config.channels:
            channel_hours = (
                hours if channel_config.lookback_hours is None else channel_config.lookback_hours
            )
            lookback_time = now - timedelta(hours=channel_hours)

            try:
                channel_messages = await self.fetch_channel_messages(
                    channel_config,
                    lookback_time,
                )
                all_messages[channel_config.name] = channel_messages

                self.logger.info(f"✓ {channel_config.name}: {len(channel_messages)} messages")

            except ChannelPrivateError:
                self.logger.warning(
                    f"✗ {channel_config.name}: Channel is private or not accessible"
                )
                all_messages[channel_config.name] = []

            except FloodWaitError as exc:
                self.logger.warning(
                    f"✗ {channel_config.name}: Rate limited, need to wait {exc.seconds}s"
                )
                await asyncio.sleep(exc.seconds)

                # Retry once.
                try:
                    channel_messages = await self.fetch_channel_messages(
                        channel_config,
                        lookback_time,
                    )
                    all_messages[channel_config.name] = channel_messages

                except Exception as retry_exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
                    self.logger.error(f"Retry failed for {channel_config.name}: {retry_exc}")
                    all_messages[channel_config.name] = []

            except ValueError as exc:
                # Entity resolution error.
                if "Could not find the input entity" in str(exc):
                    self.logger.error(
                        f"✗ {channel_config.name}: Channel not found. "
                        "Make sure you've joined this channel with your "
                        f"Telegram account and the channel ID "
                        f"({channel_config.id}) is correct."
                    )
                else:
                    self.logger.error(f"✗ {channel_config.name}: {exc}")

                all_messages[channel_config.name] = []

            except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
                self.logger.error(f"✗ {channel_config.name}: Error fetching messages: {exc}")
                all_messages[channel_config.name] = []

        total_messages = sum(len(channel_messages) for channel_messages in all_messages.values())
        self.logger.info(f"Total messages collected: {total_messages}")

        return all_messages

    async def fetch_channel_messages(
        self,
        channel_config: ChannelConfig,
        lookback_time: datetime,
    ) -> list[Message]:
        """
        Fetch messages from a single channel.

        Args:
            channel_config: Channel configuration.
            lookback_time: Earliest message time.

        Returns:
            List of Message objects.
        """
        try:
            messages: list[Message] = []
            max_messages = self.config.settings.max_messages_per_channel

            # Telethon types get_entity() as Entity | list[Entity].
            # A single channel ID should resolve to one entity.
            entity = await self.client.get_entity(channel_config.id)

            if isinstance(entity, list):
                raise TypeError(
                    f"Expected a single Telegram entity for channel {channel_config.id}, got a list"
                )

            async for telegram_message in self.client.iter_messages(
                entity,
                limit=max_messages,
                offset_date=datetime.now(timezone.utc),
            ):
                # Stop if message is older than lookback time.
                if telegram_message.date < lookback_time:
                    break

                # Skip messages without text.
                if not telegram_message.text:
                    # Handle media-only messages.
                    if telegram_message.media:
                        media_type = self._get_media_type(telegram_message)
                        text = f"[{media_type}]"
                    else:
                        continue
                else:
                    text = telegram_message.text
                    media_type = (
                        self._get_media_type(telegram_message) if telegram_message.media else ""
                    )

                # Get sender name.
                sender = await self._get_sender_name(telegram_message)

                # Generate message link.
                link = self._generate_message_link(
                    entity,
                    telegram_message.id,
                )

                messages.append(
                    Message(
                        text=text,
                        sender=sender,
                        timestamp=telegram_message.date,
                        link=link,
                        channel_name=channel_config.name,
                        has_media=telegram_message.media is not None,
                        media_type=media_type or "",
                    )
                )

            messages.sort(key=lambda item: item.timestamp)
            return messages

        except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            self.logger.error(f"Error fetching from {channel_config.name}: {exc}")
            raise

    async def get_channel_url(
        self,
        channel_config: ChannelConfig,
    ) -> str | None:
        """Get the Telegram URL for a configured channel."""
        try:
            entity = await self.client.get_entity(channel_config.id)

            if isinstance(entity, list):
                raise TypeError(
                    f"Expected a single Telegram entity for channel {channel_config.id}, got a list"
                )

            return self._generate_channel_url(entity)

        except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            self.logger.warning(f"Could not generate channel URL for {channel_config.name}: {exc}")
            return None

    def _get_media_type(self, message: TelegramMessage) -> str:
        """
        Determine media type from message.

        Args:
            message: Telegram message.

        Returns:
            Media type string.
        """
        if not message.media:
            return ""

        media_type = type(message.media).__name__
        if "Photo" in media_type:
            label = self._ui["media_photo"]
        elif "Video" in media_type or "Document" in media_type:
            label = (
                self._get_document_media_type(message.media)
                if isinstance(message.media, tl_types.MessageMediaDocument)
                else self._ui["media_video"]
            )
        elif "Voice" in media_type or "Audio" in media_type:
            label = self._ui["media_voice"]
        elif "Poll" in media_type:
            label = self._ui["media_poll"]
        elif "Geo" in media_type or "Location" in media_type:
            label = self._ui["media_geo"]
        else:
            label = self._ui["media_other"]
        return label

    def _get_document_media_type(
        self,
        media: tl_types.MessageMediaDocument,
    ) -> str:
        """Determine media type for a document."""
        if isinstance(media.document, tl_types.Document):
            mime = media.document.mime_type or ""

            if "video" in mime:
                return self._ui["media_video"]

            if "audio" in mime:
                return self._ui["media_audio"]

            return self._ui["media_document"]

        return self._ui["media_video"]

    @staticmethod
    async def _get_sender_name(message: TelegramMessage) -> str:
        """
        Get sender name from message.

        Args:
            message: Telegram message.

        Returns:
            Sender name or "Unknown".
        """
        try:
            sender = await message.get_sender()
            if not sender:
                return "Unknown"

            if isinstance(sender, tl_types.User):
                name = sender.first_name or ""
                if sender.last_name:
                    name += f" {sender.last_name}"
            elif isinstance(sender, (tl_types.Chat, tl_types.Channel)):
                name = sender.title
            else:
                username = getattr(sender, "username", None)
                name = f"@{username}" if username else ""

            return name or "Unknown"
        except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            return "Unknown"

    @staticmethod
    def _generate_message_link(
        entity: Any,
        message_id: int,
    ) -> str:
        """Generate a clickable Telegram link to a message."""
        try:
            channel_url = TelegramMessageSource._generate_channel_url(entity)
            return f"{channel_url}/{message_id}" if channel_url else "#"
        except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            return "#"

    @staticmethod
    def _generate_channel_url(entity: Any) -> str | None:
        """Generate the Telegram URL for a channel entity."""
        username = getattr(entity, "username", None)

        if username:
            return f"https://t.me/{username}"

        channel_id = getattr(entity, "id", None)

        if channel_id is not None:
            channel_id_str = str(channel_id).replace("-100", "")
            return f"https://t.me/c/{channel_id_str}"

        return None


async def main() -> None:
    """Authenticate and test the message collector.

    Run interactively to create sessions/user.session:
        uv run python -m chatbrief.platforms.telegram.telegram_source
    """
    config = load_config()
    logger = setup_logging(config.log_level)

    collector = TelegramMessageSource(config, logger)

    print("Authenticating with Telegram User API...")
    print("You will be prompted for your phone number and a login code.")

    try:
        # Telethon's start() is a sync/async hybrid API. Its static type
        # annotation does not fully represent the runtime behavior when
        # called from an already-running event loop.
        start_result = collector.client.start()
        await cast(
            Awaitable[TelegramClient],
            cast(object, start_result),
        )

        print("Authenticated! Session saved to sessions/user.session")

        channel_messages = await collector.fetch_messages(hours=1)

        for channel_name, messages in channel_messages.items():
            print(f"\n{channel_name}: {len(messages)} messages")

            for message in messages[:3]:
                print(f"  - {message.sender}: {message.text[:50]}...")

    finally:
        await collector.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
