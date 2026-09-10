from src.constants import MAX_DIGEST_HOURS


def validate_hours(hours: int) -> None:
    """Reject lookback windows that are not a sane number of hours.

    Raises:
        ValueError: If hours is not an int in [1, MAX_DIGEST_HOURS]
    """
    if not isinstance(hours, int) or isinstance(hours, bool):
        raise ValueError(f"hours must be an int, got {hours!r}")
    if hours <= 0 or hours > MAX_DIGEST_HOURS:
        raise ValueError(f"hours must be between 1 and {MAX_DIGEST_HOURS}, got {hours}")
