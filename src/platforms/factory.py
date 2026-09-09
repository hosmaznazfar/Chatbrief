"""Factory for creating platform message sources and senders."""

import logging

from src.config.models import Config
from src.platforms.base import MessageSender, MessageSource
from src.platforms.telegram import TelegramMessageSource
from src.platforms.telegram_sender import TelegramMessageSender


def create_message_source(
    config: Config,
    logger: logging.Logger,
) -> MessageSource:
    """Create the configured messaging-platform source."""
    return TelegramMessageSource(config, logger)


def create_message_sender(
    config: Config,
    logger: logging.Logger,
) -> MessageSender:
    """Create the configured messaging-platform sender."""
    return TelegramMessageSender(config, logger)


# def create_bot(
#     config: Config,
#     logger: logging.Logger,
#     scheduler: DigestScheduler | None = None,
# ) -> Bot:
#     """Create the configured messaging-platform bot."""
#     return TelegramBot(config, logger, scheduler)
