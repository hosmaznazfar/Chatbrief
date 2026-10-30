"""
Digest service API.
"""

import logging
from typing import Optional

from chatbrief.config.models import Config
from chatbrief.digest.builder import build_digest_parts, join_parts
from chatbrief.digest.cache import write_last_digest
from chatbrief.digest.validators import validate_hours
from chatbrief.platforms.base import MessageSender, MessageSource


async def generate_and_send_digest(
    config: Config,
    logger: logging.Logger,
    source: MessageSource,
    sender: MessageSender,
    hours: int = 24,
    user_id: Optional[int] = None,
) -> bool:
    """Generate and send digest using the provided platform services."""
    validate_hours(hours)

    try:
        built = await build_digest_parts(
            config,
            logger,
            source,
            hours,
        )

        if built is None:
            return False

        parts, summary_message = built

        write_last_digest(
            join_parts(parts, summary_message),
            hours,
            logger,
        )

        if config.settings.auto_cleanup_old_digests:
            await sender.cleanup_old_digests(user_id)

        return await sender.send_channel_messages_with_tracking(
            parts,
            summary_message,
            user_id,
        )

    except Exception as e:
        logger.error(
            f"Digest generation failed: {e}",
            exc_info=True,
        )
        return False


async def build_digest(
    config: Config,
    logger: logging.Logger,
    source: MessageSource,
    hours: int = 24,
) -> str:
    """Build the digest as a single Markdown document without sending it.

    Returns:
        The digest text, or an empty string when there was nothing to report.
    """
    built = await build_digest_parts(
        config,
        logger,
        source,
        hours,
    )
    return "" if built is None else join_parts(*built)
