#!/usr/bin/env python3
"""
Chatbref - Automated Multi Platform Digest Generator

Main entry point for the application.
Starts the scheduler and bot command handler.
"""

import asyncio
import logging
import signal
import sys
from contextlib import suppress

from mcp.server import MCPServer

from src.bot_commands import BotCommandHandler
from src.config.loader import load_config
from src.config.models import Config
from src.mcp_server import build_server
from src.scheduler import DigestScheduler
from src.utils import setup_logging


class TelebriefApp:
    """Main application controller."""

    def __init__(self):
        """Initialize the application."""
        self.config: Config | None = None
        self.logger: logging.Logger | None = None
        self.scheduler: DigestScheduler | None = None
        self.bot_handler: BotCommandHandler | None = None
        self.mcp: MCPServer | None = None
        self.mcp_task: asyncio.Task[None] | None = None
        self.shutdown_event = asyncio.Event()

    def _require_initialized(
        self,
    ) -> tuple[
        Config,
        logging.Logger,
        DigestScheduler,
        BotCommandHandler,
    ]:
        """Return initialized application components."""
        if (
            self.config is None
            or self.logger is None
            or self.scheduler is None
            or self.bot_handler is None
        ):
            raise RuntimeError("Application has not been initialized")

        return (
            self.config,
            self.logger,
            self.scheduler,
            self.bot_handler,
        )

    async def initialize(self):
        """Load configuration and set up components."""
        try:
            # Load configuration
            print("Loading configuration...")
            self.config = load_config()

            # Set up logging
            self.logger = setup_logging(self.config.log_level)
            self.logger.info("=" * 70)
            self.logger.info("🚀 TELEBRIEF STARTING")
            self.logger.info("=" * 70)

            # Display configuration
            self.logger.info(f"Configured channels: {len(self.config.channels)}")
            for ch in self.config.channels:
                self.logger.info(f"  • {ch.name} ({ch.id})")

            self.logger.info(
                f"Schedule: Daily at {self.config.settings.schedule_time} {self.config.settings.timezone}"
            )
            self.logger.info(f"Target user: {self.config.settings.target_user_id}")
            self.logger.info(
                f"AI provider: {self.config.settings.ai_provider}, model: {self.config.settings.ai_model}"
            )

            # Initialize scheduler
            self.logger.info("Initializing scheduler...")
            self.scheduler = DigestScheduler(self.config, self.logger)

            # Initialize bot command handler
            self.logger.info("Initializing bot command handler...")
            self.bot_handler = BotCommandHandler(self.config, self.logger, self.scheduler)
            self.bot_handler.setup_application()

            # Initialize MCP server (optional)
            if self.config.mcp.enabled:
                self.logger.info("Initializing MCP server...")
                self.mcp = build_server(self.config, self.logger)

            self.logger.info("✅ Initialization complete")
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

    async def run(self):
        """Run the application."""
        config, logger, scheduler, bot_handler = self._require_initialized()

        # Start scheduler
        logger.info("Starting scheduler...")
        scheduler.start()

        logger.info("Starting bot command handler...")
        await bot_handler.run()

        if self.mcp:
            mcp_cfg = config.mcp
            logger.info(
                f"Starting MCP server on http://{mcp_cfg.host}:{mcp_cfg.port}{mcp_cfg.path}"
            )
            self.mcp_task = asyncio.create_task(
                self.mcp.run_streamable_http_async(
                    host=mcp_cfg.host,
                    port=mcp_cfg.port,
                    streamable_http_path=mcp_cfg.path,
                )
            )

        logger.info("=" * 70)
        logger.info("✅ TELEBRIEF IS RUNNING")
        logger.info("=" * 70)
        logger.info("Scheduler: Active")
        logger.info(f"Next digest: {scheduler.get_next_run_time()}")
        logger.info("Bot commands: Active")
        if self.mcp_task:
            mcp_cfg = config.mcp
            logger.info(f"MCP server: http://{mcp_cfg.host}:{mcp_cfg.port}{mcp_cfg.path}")
        logger.info("")
        logger.info("Available commands in Telegram:")
        logger.info("  /digest - Generate digest instantly")
        logger.info("  /status - Show status")
        logger.info("  /help - Show help")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 70)

        await self.shutdown_event.wait()

    async def shutdown(self):
        """Graceful shutdown."""
        config, logger, scheduler, bot_handler = self._require_initialized()

        logger.info("=" * 70)
        logger.info("🛑 SHUTTING DOWN TELEBRIEF")
        logger.info("=" * 70)

        # Stop scheduler
        if scheduler:
            logger.info("Stopping scheduler...")
            scheduler.stop()

        # Stop bot
        if bot_handler:
            logger.info("Stopping bot...")
            await bot_handler.stop()

        # Stop MCP server
        # ponytail: cancelling the task makes uvicorn log a CancelledError traceback on
        # the way out — cosmetic, right after the line below. Build uvicorn.Server here
        # and flip should_exit instead if that log noise ever matters.
        if self.mcp_task:
            logger.info("Stopping MCP server...")
            self.mcp_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.mcp_task

        logger.info("✅ Shutdown complete")
        logger.info("=" * 70)

        # Signal that shutdown is complete
        self.shutdown_event.set()


async def main():
    """Main entry point."""
    app = TelebriefApp()

    # Initialize
    if not await app.initialize():
        sys.exit(1)

    assert app.logger is not None
    logger = app.logger

    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(app.shutdown()))

    try:
        # Run application
        await app.run()

    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

    finally:
        # Ensure clean shutdown
        if not app.shutdown_event.is_set():
            await app.shutdown()


if __name__ == "__main__":
    print(
        """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ████████╗███████╗██╗     ███████╗██████╗ ██████╗     ║
║   ╚══██╔══╝██╔════╝██║     ██╔════╝██╔══██╗██╔══██╗    ║
║      ██║   █████╗  ██║     █████╗  ██████╔╝██████╔╝    ║
║      ██║   ██╔══╝  ██║     ██╔══╝  ██╔══██╗██╔══██╗    ║
║      ██║   ███████╗███████╗███████╗██████╔╝██║  ██║    ║
║      ╚═╝   ╚══════╝╚══════╝╚══════╝╚═════╝ ╚═╝  ╚═╝    ║
║                                                          ║
║         Automated Telegram Digest Generator             ║
║                   Powered by AI                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
