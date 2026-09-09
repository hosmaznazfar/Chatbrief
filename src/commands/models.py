"""Models used by application commands."""

from dataclasses import dataclass
from enum import Enum


class CommandStatus(Enum):
    """Possible outcomes of an application command."""

    SUCCESS = "success"
    ERROR = "error"
    UNAUTHORIZED = "unauthorized"
    RATE_LIMITED = "rate_limited"


@dataclass(frozen=True)
class CommandResult:
    """Result returned by an application command."""

    status: CommandStatus
    message: str
