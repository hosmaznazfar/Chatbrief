"""Domain model for a collected message."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """Represents a collected message."""

    text: str
    sender: str
    timestamp: datetime
    link: str
    channel_name: str
    has_media: bool
    media_type: str
