"""Application-level command service."""

import logging
import time

from src.config.models import Config
from src.core import generate_and_send_digest
from src.platforms.factory import create_message_sender
from src.scheduler import DigestScheduler
from src.ui_strings import get_ui_strings

from .models import CommandResult, CommandStatus


class CommandService:
    """Execute application commands without depending on a messaging platform."""

    RATE_LIMIT_SECONDS = 30

    def __init__(
        self,
        config: Config,
        logger: logging.Logger,
        scheduler: DigestScheduler | None = None,
    ) -> None:
        self.config = config
        self.logger = logger
        self.scheduler = scheduler
        self._ui = get_ui_strings(config.settings.output_language)
        self._command_timestamps: dict[int, float] = {}

    def is_authorized(self, user_id: int) -> bool:
        """Return whether a user is authorized to execute commands."""
        return user_id == self.config.settings.target_user_id

    def _is_rate_limited(self, user_id: int) -> bool:
        """Return whether a user has exceeded the command rate limit."""
        now = time.monotonic()

        if user_id not in self._command_timestamps:
            self._command_timestamps[user_id] = now
            return False

        if now - self._command_timestamps[user_id] < self.RATE_LIMIT_SECONDS:
            return True

        self._command_timestamps[user_id] = now
        return False

    def _check_authorization(self, user_id: int) -> CommandResult | None:
        """Check whether a user is authorized to execute commands."""
        if not self.is_authorized(user_id):
            self.logger.warning("Unauthorized command attempt from user %s", user_id)
            return CommandResult(
                status=CommandStatus.UNAUTHORIZED,
                message="",
            )

        return None

    def _check_rate_limit(self, user_id: int) -> CommandResult | None:
        """Check whether a user has exceeded the command rate limit."""
        if self._is_rate_limited(user_id):
            return CommandResult(
                status=CommandStatus.RATE_LIMITED,
                message=self._ui["rate_limited"],
            )

        return None

    def check_access(self, user_id: int) -> CommandResult | None:
        """Check authorization and rate limiting before executing a command."""
        authorization_result = self._check_authorization(user_id)
        if authorization_result is not None:
            return authorization_result

        return self._check_rate_limit(user_id)

    async def digest(
        self,
        user_id: int,
        *,
        access_checked: bool = False,
    ) -> CommandResult:
        """Generate and send a digest for an authorized user."""
        if not access_checked:
            access_result = self.check_access(user_id)
            if access_result is not None:
                return access_result

        self.logger.info("Manual digest requested by user %s", user_id)

        try:
            success = await generate_and_send_digest(
                config=self.config,
                logger=self.logger,
                hours=24,
                user_id=user_id,
            )

            if success:
                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message=self._ui["digest_done"],
                )

            return CommandResult(
                status=CommandStatus.ERROR,
                message=self._ui["digest_error"],
            )

        except Exception as e:
            self.logger.error(
                "Error generating digest: %s",
                e,
                exc_info=True,
            )
            return CommandResult(
                status=CommandStatus.ERROR,
                message=self._ui["digest_exception"],
            )

    async def cleanup(
        self,
        user_id: int,
        *,
        access_checked: bool = False,
    ) -> CommandResult:
        """Clean up previously sent digests for an authorized user."""
        if not access_checked:
            access_result = self.check_access(user_id)
            if access_result is not None:
                return access_result

        self.logger.info("Manual cleanup requested by user %s", user_id)

        try:
            sender = create_message_sender(self.config, self.logger)
            success = await sender.cleanup_old_digests(user_id)

            if success:
                return CommandResult(
                    status=CommandStatus.SUCCESS,
                    message=self._ui["cleanup_done"],
                )

            return CommandResult(
                status=CommandStatus.ERROR,
                message=self._ui["cleanup_partial"],
            )

        except Exception as e:
            self.logger.error(
                "Error during cleanup: %s",
                e,
                exc_info=True,
            )
            return CommandResult(
                status=CommandStatus.ERROR,
                message=self._ui["cleanup_error"],
            )

    def status(self, user_id: int) -> CommandResult:
        """Return the current application status."""
        authorization_result = self._check_authorization(user_id)
        if authorization_result is not None:
            return authorization_result

        ai_model = self.config.settings.ai_model
        auto_cleanup_value = (
            self._ui["enabled"]
            if self.config.settings.auto_cleanup_old_digests
            else self._ui["disabled"]
        )

        status_lines = [
            self._ui["status_header"],
            f"{self._ui['provider_label']}: {self.config.settings.ai_provider}",
            f"{self._ui['model_label']}: {ai_model}",
            f"{self._ui['channels_configured']}: {len(self.config.channels)}",
            f"{self._ui['auto_cleanup_label']}: {auto_cleanup_value}",
        ]

        if self.scheduler:
            next_run = self.scheduler.get_next_run_time()
            status_lines.append(f"{self._ui['next_digest']}: {next_run}")
        else:
            status_lines.append(self._ui["scheduler_not_running"])

        status_lines.extend(
            [
                "",
                self._ui["available_commands"],
                "/digest - " + self._ui["cmd_digest_desc"],
                "/cleanup - " + self._ui["cmd_cleanup_desc"],
                "/status - " + self._ui["cmd_status_desc"],
                "/help - " + self._ui["cmd_help_desc"],
            ]
        )

        return CommandResult(
            status=CommandStatus.SUCCESS,
            message="\n".join(status_lines),
        )

    def help(self, user_id: int) -> CommandResult:
        """Return help text for an authorized user."""
        authorization_result = self._check_authorization(user_id)
        if authorization_result is not None:
            return authorization_result

        help_text = (
            f"{self._ui['help_title']}\n\n"
            f"{self._ui['help_intro']}\n\n"
            f"{self._ui['help_commands_header']}\n\n"
            f"/digest - {self._ui['cmd_digest_desc']}\n"
            f"/cleanup - {self._ui['cmd_cleanup_desc']}\n"
            f"/status - {self._ui['cmd_status_desc']}\n"
            f"/help - {self._ui['cmd_help_desc']}\n\n"
            f"{self._ui['help_auto_mode']}\n"
            + self._ui["help_auto_desc"].format(
                schedule=self.config.settings.schedule_time + " UTC"
            )
            + f"\n\n{self._ui['help_features']}\n"
            + self._ui["help_features_list"].format(
                output_lang=self.config.settings.output_language,
                provider=self.config.settings.ai_provider,
            )
        )

        return CommandResult(
            status=CommandStatus.SUCCESS,
            message=help_text,
        )
