"""Factory for creating platform message sources."""

import logging

from src.config.models import Config
from src.platforms.base import MessageSource
from src.platforms.telegram import TelegramMessageSource


def create_message_source(
    config: Config,
    logger: logging.Logger,
) -> MessageSource:
    """Create the configured messaging-platform source."""
    return TelegramMessageSource(config, logger)
