"""Factory for creating platform message sources and senders."""

import logging

from chatbrief.config.models import Config
from chatbrief.platforms.base import Bot, MessageSender, MessageSource
from chatbrief.platforms.telegram.telegram_sender import TelegramMessageSender
from chatbrief.platforms.telegram.telegram_source import TelegramMessageSource
from chatbrief.scheduler import DigestScheduler


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
    from chatbrief.platforms.telegram.telegram_bot import TelegramBot

    return TelegramBot(config, logger, scheduler)
