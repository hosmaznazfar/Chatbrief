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
