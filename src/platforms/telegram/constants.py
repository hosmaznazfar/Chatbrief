"""Telegram-specific constants."""

import re

CHANNEL_URL_RE = re.compile(r"^https://t\.me/(?:c/\d+|[^/]{2,})$")
