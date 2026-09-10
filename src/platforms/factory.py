"""Factory for creating platform message sources and senders."""

import logging

from platforms.telegram.telegram_sender import TelegramMessageSender
from src.config.models import Config
from src.platforms.base import Bot, MessageSender, MessageSource
from src.platforms.telegram import TelegramMessageSource
from src.scheduler import DigestScheduler


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


def create_bot(
    config: Config,
    logger: logging.Logger,
    scheduler: DigestScheduler | None = None,
) -> Bot:
    """Create the configured messaging-platform bot."""
    from platforms.telegram.telegram_bot import TelegramBot

    return TelegramBot(config, logger, scheduler)
