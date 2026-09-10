"""Build platform-specific application components."""

import logging

from src.commands.service import CommandService
from src.config.models import Config, Platform
from src.platforms.base import Bot, MessageSender, MessageSource
from src.platforms.telegram.telegram_bot import TelegramBot
from src.platforms.telegram.telegram_sender import TelegramMessageSender
from src.platforms.telegram.telegram_source import TelegramMessageSource
from src.scheduler import DigestScheduler


class PlatformBuilder:
    """Build the concrete messaging-platform components."""

    def __init__(
        self,
        config: Config,
        logger: logging.Logger,
    ) -> None:
        """Initialize the platform builder."""
        self.config = config
        self.logger = logger

    def create_services(self) -> tuple[MessageSource, MessageSender]:
        """Create the message source and sender for the configured platform."""
        if self.config.platform is Platform.TELEGRAM:
            return (
                TelegramMessageSource(self.config, self.logger),
                TelegramMessageSender(self.config, self.logger),
            )

        if self.config.platform is Platform.BALE:
            raise NotImplementedError("Bale platform is configured but not implemented yet.")

        raise ValueError(f"Unsupported platform: {self.config.platform}")

    def create_bot(
        self,
        scheduler: DigestScheduler,
        command_service: CommandService,
    ) -> Bot:
        """Create the bot for the configured platform."""
        if self.config.platform is Platform.TELEGRAM:
            bot = TelegramBot(
                config=self.config,
                logger=self.logger,
                scheduler=scheduler,
                command_service=command_service,
            )
            bot.setup_application()
            return bot

        if self.config.platform is Platform.BALE:
            raise NotImplementedError("Bale platform is configured but not implemented yet.")

        raise ValueError(f"Unsupported platform: {self.config.platform}")
