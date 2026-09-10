#!/usr/bin/env python3
"""
Chatbrief - Automated Multi-Platform Digest Generator.

Main entry point and composition root for the application.
"""

import asyncio
import logging
import signal
import sys
from contextlib import suppress
from typing import Any

from src.commands.service import CommandService
from src.config.loader import load_config
from src.config.models import Config, Platform
from src.mcp_server import build_server
from src.platforms.base import Bot, MessageSender, MessageSource
from src.platforms.builder import PlatformBuilder
from src.platforms.telegram.telegram_bot import TelegramBot
from src.platforms.telegram.telegram_sender import TelegramMessageSender
from src.platforms.telegram.telegram_source import TelegramMessageSource
from src.scheduler import DigestScheduler
from src.utils import setup_logging


class ChatbriefApp:
    """Main application controller and composition root."""

    def __init__(self) -> None:
        """Initialize the application."""
        self.config: Config | None = None
        self.logger: logging.Logger | None = None

        self.source: MessageSource | None = None
        self.sender: MessageSender | None = None
        self.bot: Bot | None = None

        self.scheduler: DigestScheduler | None = None
        self.command_service: CommandService | None = None

        # MCPServer's type is not imported here because Pyright cannot
        # resolve the external mcp.server module in the current environment.
        self.mcp: Any = None
        self.mcp_task: asyncio.Task[None] | None = None

        self.shutdown_event = asyncio.Event()

    def _require_initialized(
        self,
    ) -> tuple[
        Config,
        logging.Logger,
        MessageSource,
        MessageSender,
        Bot,
        DigestScheduler,
    ]:
        """Return initialized application components."""
        config = self.config
        logger = self.logger
        source = self.source
        sender = self.sender
        bot = self.bot
        scheduler = self.scheduler

        if (
            config is None
            or logger is None
            or source is None
            or sender is None
            or bot is None
            or scheduler is None
        ):
            raise RuntimeError("Application has not been initialized")

        return (
            config,
            logger,
            source,
            sender,
            bot,
            scheduler,
        )

    async def initialize(self) -> bool:
        """Load configuration and set up all application components."""
        try:
            # Load configuration.
            print("Loading configuration...")
            config = load_config()
            self.config = config

            # Set up logging.
            logger = setup_logging(config.log_level)
            self.logger = logger

            logger.info("=" * 70)
            logger.info("🚀 CHATBRIEF STARTING")
            logger.info("=" * 70)

            # Display configuration.
            logger.info("Platform: %s", config.platform.value)
            logger.info(
                "Configured channels: %d",
                len(config.channels),
            )

            for channel in config.channels:
                logger.info(
                    "  • %s (%s)",
                    channel.name,
                    channel.id,
                )

            logger.info(
                "Schedule: Daily at %s %s",
                config.settings.schedule_time,
                config.settings.timezone,
            )
            logger.info(
                "Target user: %s",
                config.settings.target_user_id,
            )
            logger.info(
                "AI provider: %s, model: %s",
                config.settings.ai_provider,
                config.settings.ai_model,
            )

            # ---------------------------------------------------------
            # Platform layer
            # ---------------------------------------------------------
            #
            # The composition root is the only place that decides
            # which concrete platform implementation to use.
            #
            # Everything below this point works with the platform-neutral
            # MessageSource / MessageSender / Bot interfaces.
            logger.info(
                "Initializing %s platform...",
                config.platform.value,
            )

            platform_builder = PlatformBuilder(
                config=config,
                logger=logger,
            )

            source, sender = platform_builder.create_services()

            self.source = source
            self.sender = sender

            # ---------------------------------------------------------
            # Application services
            # ---------------------------------------------------------

            logger.info("Initializing scheduler...")

            scheduler = DigestScheduler(
                config=config,
                logger=logger,
                source=source,
                sender=sender,
            )

            self.scheduler = scheduler

            logger.info("Initializing command service...")

            command_service = CommandService(
                config=config,
                logger=logger,
                source=source,
                sender=sender,
                scheduler=scheduler,
            )

            self.command_service = command_service

            # ---------------------------------------------------------
            # Platform bot
            # ---------------------------------------------------------
            #
            # The bot receives the already-created application service.
            # The Telegram adapter translates Telegram commands into
            # calls to CommandService.
            logger.info("Initializing bot...")

            bot = platform_builder.create_bot(
                scheduler=scheduler,
                command_service=command_service,
            )

            self.bot = bot

            # ---------------------------------------------------------
            # Optional MCP server
            # ---------------------------------------------------------

            if config.mcp.enabled:
                logger.info("Initializing MCP server...")

                self.mcp = build_server(
                    config,
                    logger,
                )

            logger.info("✅ Initialization complete")
            return True

        except FileNotFoundError as e:
            print(f"❌ Configuration error: {e}")
            print("\nPlease ensure:")
            print("1. config.yaml exists and is properly configured")
            print("2. .env file exists with required API credentials")
            print("\nSee .env.example and SPECIFICATION.md for details.")
            return False

        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            return False

        except Exception as e:
            print(f"❌ Initialization failed: {e}")

            import traceback

            traceback.print_exc()
            return False

    async def run(self) -> None:
        """Run the application."""
        (
            config,
            logger,
            _source,
            _sender,
            bot,
            scheduler,
        ) = self._require_initialized()

        # Start scheduler.
        logger.info("Starting scheduler...")
        scheduler.start()

        # Start platform bot.
        logger.info(
            "Starting %s bot...",
            config.platform.value,
        )
        await bot.run()

        # Start MCP server if enabled.
        if self.mcp is not None:
            mcp_cfg = config.mcp

            logger.info(
                "Starting MCP server on http://%s:%d%s",
                mcp_cfg.host,
                mcp_cfg.port,
                mcp_cfg.path,
            )

            self.mcp_task = asyncio.create_task(
                self.mcp.run_streamable_http_async(
                    host=mcp_cfg.host,
                    port=mcp_cfg.port,
                    streamable_http_path=mcp_cfg.path,
                )
            )

        logger.info("=" * 70)
        logger.info("✅ CHATBRIEF IS RUNNING")
        logger.info("=" * 70)
        logger.info(
            "Platform: %s",
            config.platform.value,
        )
        logger.info("Scheduler: Active")
        logger.info(
            "Next digest: %s",
            scheduler.get_next_run_time(),
        )
        logger.info("Bot: Active")

        if self.mcp_task is not None:
            mcp_cfg = config.mcp

            logger.info(
                "MCP server: http://%s:%d%s",
                mcp_cfg.host,
                mcp_cfg.port,
                mcp_cfg.path,
            )

        logger.info("")
        logger.info("Available commands:")
        logger.info("  /digest - Generate digest instantly")
        logger.info("  /status - Show status")
        logger.info("  /help - Show help")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 70)

        await self.shutdown_event.wait()

    async def shutdown(self) -> None:
        """Gracefully shut down the application."""
        if self.config is None or self.logger is None or self.scheduler is None or self.bot is None:
            return

        logger = self.logger

        logger.info("=" * 70)
        logger.info("🛑 SHUTTING DOWN CHATBRIEF")
        logger.info("=" * 70)

        # Stop scheduler.
        logger.info("Stopping scheduler...")
        self.scheduler.stop()

        # Stop bot.
        logger.info("Stopping bot...")
        await self.bot.stop()

        # Disconnect message source.
        if self.source is not None:
            logger.info("Disconnecting message source...")
            await self.source.disconnect()

        # Stop MCP server.
        #
        # Cancelling the task may cause uvicorn to emit a cosmetic
        # CancelledError traceback during shutdown.
        if self.mcp_task is not None:
            logger.info("Stopping MCP server...")
            self.mcp_task.cancel()

            with suppress(asyncio.CancelledError):
                await self.mcp_task

        logger.info("✅ Shutdown complete")
        logger.info("=" * 70)

        self.shutdown_event.set()


async def main() -> None:
    """Main entry point."""
    app = ChatbriefApp()

    # Initialize application.
    if not await app.initialize():
        sys.exit(1)

    assert app.logger is not None
    logger = app.logger

    # Set up signal handlers for graceful shutdown.
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(app.shutdown()),
        )

    try:
        await app.run()

    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.error(
            "Fatal error: %s",
            e,
            exc_info=True,
        )
        sys.exit(1)

    finally:
        if not app.shutdown_event.is_set():
            await app.shutdown()


if __name__ == "__main__":
    print(
        """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║    ██████╗██╗  ██╗ █████╗ ████████╗██████╗ ██████╗       ║
║   ██╔════╝██║  ██║██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗      ║
║   ██║     ███████║███████║   ██║   ██████╔╝██████╔╝      ║
║   ██║     ██╔══██║██╔══██║   ██║   ██╔══██╗██╔══██╗      ║
║   ╚██████╗██║  ██║██║  ██║   ██║   ██║  ██║██║  ██║      ║
║    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝      ║
║                                                          ║
║              Intelligent Chat Automation                 ║
║                     Powered by AI                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
