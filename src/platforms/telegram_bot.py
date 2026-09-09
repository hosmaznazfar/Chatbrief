# """Telegram bot implementation."""

# import logging

# from src.bot_commands import BotCommandHandler
# from src.config.models import Config
# from src.platforms.base import Bot
# from src.scheduler import DigestScheduler


# class TelegramBot(Bot):
#     """Telegram implementation of the bot interface."""

#     def __init__(
#         self,
#         config: Config,
#         logger: logging.Logger,
#         scheduler: DigestScheduler | None = None,
#     ) -> None:
#         """Initialize the Telegram bot."""
#         self._handler = BotCommandHandler(config, logger, scheduler)

#     async def run(self) -> None:
#         """Start the Telegram bot."""
#         self._handler.setup_application()
#         await self._handler.run()

#     async def stop(self) -> None:
#         """Stop the Telegram bot."""
#         await self._handler.stop()
