"""Platform-neutral interfaces for message sources."""

from datetime import datetime
from typing import Protocol

from src.config.models import ChannelConfig
from src.message import Message


class MessageSource(Protocol):
    """Interface for collecting messages from a messaging platform."""

    async def connect(self) -> None:
        """Connect to the messaging platform."""
        ...

    async def disconnect(self) -> None:
        """Disconnect from the messaging platform."""
        ...

    async def fetch_messages(
        self,
        hours: int = 24,
    ) -> dict[str, list[Message]]:
        """Fetch messages from all configured channels."""
        ...

    async def fetch_channel_messages(
        self,
        channel_config: ChannelConfig,
        lookback_time: datetime,
    ) -> list[Message]:
        """Fetch messages from a single configured channel."""
        ...


class MessageSender(Protocol):
    """Interface for delivering generated digests."""

    async def cleanup_old_digests(self, user_id: int | None = None) -> bool:
        """Delete previously sent digest messages."""
        ...

    async def send_channel_messages_with_tracking(
        self,
        channel_messages: list[tuple[str, str]],
        summary_message: str | None = None,
        user_id: int | None = None,
    ) -> bool:
        """Send channel messages and optionally a summary message."""
        ...


class Bot(Protocol):
    """Interface for running an interactive messaging bot."""

    async def run(self) -> None:
        """Start the bot and begin handling commands."""
        ...

    async def stop(self) -> None:
        """Stop the bot gracefully."""
        ...
