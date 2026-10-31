"""Protocols for application command services."""

from typing import Protocol

from chatbrief.commands.models import CommandResult


class CommandServiceProtocol(Protocol):
    """Application commands required by platform-specific bot adapters."""

    def check_access(self, user_id: int) -> CommandResult | None:
        """Check whether a user may execute a command."""
        ...

    async def digest(
        self,
        user_id: int,
        *,
        access_checked: bool = False,
    ) -> CommandResult:
        """Generate and send a digest."""
        ...

    async def cleanup(
        self,
        user_id: int,
        *,
        access_checked: bool = False,
    ) -> CommandResult:
        """Clean up previously sent digests."""
        ...

    def status(self, user_id: int) -> CommandResult:
        """Return application status."""
        ...

    def help(self, user_id: int) -> CommandResult:
        """Return command help."""
        ...
