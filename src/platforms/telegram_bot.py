"""
Telegram bot command handlers.
"""

import asyncio
import logging
from typing import Optional

from telegram import BotCommand, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.commands.models import CommandStatus
from src.commands.service import CommandService
from src.config.models import Config
from src.scheduler import DigestScheduler
from src.ui_strings import get_ui_strings


class BotCommandHandler:
    """Telegram adapter for application commands."""

    def __init__(
        self,
        config: Config,
        logger: logging.Logger,
        scheduler: Optional[DigestScheduler] = None,
        command_service: CommandService | None = None,
    ):
        """
        Initialize the Telegram command handler.

        Args:
            config: Application configuration.
            logger: Logger instance.
            scheduler: Scheduler instance.
            command_service: Application command service.
        """
        self.config = config
        self.logger = logger
        self.scheduler = scheduler
        self.command_service = command_service or CommandService(
            config,
            logger,
            scheduler,
        )
        self.app: Optional[Application] = None
        self._ui = get_ui_strings(config.settings.output_language)

    def setup_application(self) -> Application:
        """
        Set up Telegram bot application.

        Returns:
            Configured Application instance.
        """
        self.app = Application.builder().token(self.config.telegram_bot_token).build()

        self.app.add_handler(CommandHandler("digest", self.handle_digest))
        self.app.add_handler(CommandHandler("cleanup", self.handle_cleanup))
        self.app.add_handler(CommandHandler("status", self.handle_status))
        self.app.add_handler(CommandHandler("help", self.handle_help))
        self.app.add_handler(CommandHandler("start", self.handle_help))

        self.logger.info("Bot command handlers registered")
        return self.app

    async def setup_bot_menu(self) -> None:
        """
        Set up the Telegram bot command menu.
        """
        if not self.app:
            self.logger.warning("Application not initialized, cannot set up bot menu")
            return

        commands = [
            BotCommand("start", self._ui["cmd_start_desc"]),
            BotCommand("digest", self._ui["cmd_digest_desc"]),
            BotCommand("cleanup", self._ui["cmd_cleanup_desc"]),
            BotCommand("status", self._ui["cmd_status_desc"]),
            BotCommand("help", self._ui["cmd_help_desc"]),
        ]

        try:
            await self.app.bot.set_my_commands(commands)
            self.logger.info("✅ Bot command menu configured successfully")
        except Exception as e:
            self.logger.error(f"Failed to set up bot menu: {e}")

    async def handle_digest(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Handle /digest command.
        """
        if update.effective_user is None or update.message is None:
            return

        user_id = update.effective_user.id

        access_result = self.command_service.check_access(user_id)
        if access_result is not None:
            if access_result.status is CommandStatus.RATE_LIMITED:
                await update.message.reply_text(access_result.message)
            return

        await update.message.reply_text(self._ui["generating_digest"])

        result = await self.command_service.digest(
            user_id,
            access_checked=True,
        )

        if result.status is CommandStatus.SUCCESS:
            await update.message.reply_text(result.message)
        else:
            await update.message.reply_text(result.message)

    async def handle_cleanup(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Handle /cleanup command.
        """
        if update.effective_user is None or update.message is None:
            return

        user_id = update.effective_user.id

        access_result = self.command_service.check_access(user_id)
        if access_result is not None:
            if access_result.status is CommandStatus.RATE_LIMITED:
                await update.message.reply_text(access_result.message)
            return

        await update.message.reply_text(self._ui["cleaning_up"])

        result = await self.command_service.cleanup(
            user_id,
            access_checked=True,
        )

        await update.message.reply_text(result.message)

    async def handle_status(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Handle /status command.
        """
        if update.effective_user is None or update.message is None:
            return

        result = self.command_service.status(update.effective_user.id)

        if result.status is CommandStatus.UNAUTHORIZED:
            return

        await update.message.reply_text(
            result.message,
            parse_mode="Markdown",
        )

    async def handle_help(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """
        Handle /help and /start commands.
        """
        if update.effective_user is None or update.message is None:
            return

        result = self.command_service.help(update.effective_user.id)

        if result.status is CommandStatus.UNAUTHORIZED:
            return

        await update.message.reply_text(
            result.message,
            parse_mode="Markdown",
        )

    async def run(self) -> None:
        """Run the bot in polling mode."""
        if not self.app:
            self.setup_application()

        if self.app is None or self.app.updater is None:
            raise RuntimeError("Application failed to initialize")

        self.logger.info("Starting bot polling...")
        await self.app.initialize()
        await self.app.start()

        await self.setup_bot_menu()

        await self.app.updater.start_polling()

        self.logger.info("✅ Bot is running and listening for commands")

    async def stop(self) -> None:
        """Stop the bot."""
        if self.app and self.app.updater:
            self.logger.info("Stopping bot...")
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()


async def main() -> None:
    """Test bot commands."""
    from src.config.loader import load_config
    from src.utils import setup_logging

    config = load_config()
    logger = setup_logging(config.log_level)

    handler = BotCommandHandler(config, logger)
    handler.setup_application()

    logger.info("Bot command handler ready. Starting polling...")

    try:
        await handler.run()

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping...")
        await handler.stop()


if __name__ == "__main__":
    asyncio.run(main())
