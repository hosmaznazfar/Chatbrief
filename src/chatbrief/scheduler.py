"""
Scheduler for automated daily digest generation.
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from chatbrief.config.models import Config
from chatbrief.digest.service import generate_and_send_digest
from chatbrief.platforms.base import MessageSender, MessageSource


class DigestScheduler:
    """Schedules daily digest generation."""

    def __init__(
            self,
            config: Config,
            logger: logging.Logger,
            source: MessageSource,
            sender: MessageSender,
    ):
        """
        Initialize scheduler.

        Args:
            config: Application configuration
            logger: Logger instance
            source: Message source used to collect messages
            sender: Message sender used to deliver digests
        """
        self.config = config
        self.logger = logger
        self.source = source
        self.sender = sender
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        """Start the scheduler."""
        if self.is_running:
            self.logger.warning("Scheduler already running")
            return

        hour, minute = self._parse_schedule_time()

        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone=self.config.settings.timezone,
        )

        self.scheduler.add_job(
            func=self._scheduled_digest_job,
            trigger=trigger,
            id="daily_digest",
            name="Daily Digest Generation",
            replace_existing=True,
        )

        self.scheduler.start()
        self.is_running = True

        job = self.scheduler.get_job("daily_digest")
        next_run = job.next_run_time if job else None
        self.logger.info("✅ Scheduler started")
        self.logger.info(
            f"⏰ Next digest scheduled for: {next_run} {self.config.settings.timezone}"
        )

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            self.logger.info("Scheduler stopped")

    async def _scheduled_digest_job(self):
        """Scheduled job that runs daily."""
        self.logger.info("=" * 60)
        self.logger.info("📅 SCHEDULED DIGEST JOB STARTED")
        self.logger.info("=" * 60)

        try:
            success = await generate_and_send_digest(
                config=self.config,
                logger=self.logger,
                source=self.source,
                sender=self.sender,
                hours=self.config.settings.lookback_hours,
            )

            if success:
                self.logger.info("✅ Scheduled digest completed successfully")
            else:
                self.logger.error("❌ Scheduled digest failed to send")

        except Exception as e:
            self.logger.error(
                f"❌ Scheduled digest job failed: {e}",
                exc_info=True,
            )

    def _parse_schedule_time(self) -> tuple[int, int]:
        """
        Parse schedule time from config.

        Returns:
            Tuple of (hour, minute)
        """
        time_str = self.config.settings.schedule_time
        try:
            hour, minute = map(int, time_str.split(":"))
            return hour, minute
        except ValueError:
            self.logger.warning("Invalid schedule time %r, using default 08:00", time_str)
            return 8, 0

    def get_next_run_time(self) -> str:
        """
        Get next scheduled run time.

        Returns:
            Formatted time string
        """
        if not self.is_running:
            return "Scheduler not running"

        job = self.scheduler.get_job("daily_digest")
        if job and job.next_run_time:
            return str(job.next_run_time.strftime("%Y-%m-%d %H:%M:%S %Z"))
        return "No job scheduled"
