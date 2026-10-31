import logging
from datetime import datetime, timezone

from chatbrief.config.models import Config
from chatbrief.digest.collector import collect_messages
from chatbrief.digest.state import digest_lock
from chatbrief.digest.validators import validate_hours
from chatbrief.formatter import DigestFormatter
from chatbrief.grouper import DigestGrouper
from chatbrief.platforms.base import MessageSource
from chatbrief.summarizer import ERROR_SUMMARY_PREFIX, Summarizer
from chatbrief.ui_strings import get_ui_strings
from chatbrief.utils import split_message


async def _summarize_channels(
    config: Config, logger: logging.Logger, messages_by_channel: dict
) -> dict:
    """Generate AI summaries for all channels."""
    logger.info("Generating AI summaries")
    summarizer = Summarizer(config, logger)
    summary_result = await summarizer.summarize_all(messages_by_channel)
    logger.info(f"Generated summaries for {len(summary_result['channel_summaries'])} channels")
    return summary_result


def _filter_valid_summaries(channel_summaries: dict) -> dict:
    """Filter out empty or error summaries."""
    return {
        name: summary
        for name, summary in channel_summaries.items()
        if summary and not summary.lower().startswith(ERROR_SUMMARY_PREFIX.lower())
    }


async def _get_channel_urls(
    config: Config,
    source: MessageSource,
    logger: logging.Logger,
) -> dict[str, str]:
    """Get platform-specific URLs for configured channels."""
    urls: dict[str, str] = {}

    for channel_config in config.channels:
        try:
            url = await source.get_channel_url(channel_config)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning(
                f"Could not get URL for {channel_config.name!r}: {type(e).__name__}: {e}"
            )
            continue

        if url:
            urls[channel_config.name] = url

    return urls


def _format_group_messages(
    formatter: "DigestFormatter", grouped: dict, config: "Config", hours: int
) -> list[tuple[str, str]]:
    """Format each group into a message, ordered by config definition."""
    result = []
    for name in _order_groups(grouped, config):
        points = grouped.get(name, [])
        if not points:
            continue
        fmt = formatter.format_group_message(group_name=name, points=points, hours=hours)
        if fmt:
            for part in split_message(fmt, max_length=4000):
                result.append((name, part))
    return result


def _order_groups(grouped: dict, config: Config) -> list[str]:
    """Order group names: config-defined order first, then remaining, 'Other' last.

    Recognizes both the localized UI string and the literal "Other"
    (case-insensitive) as the special bucket to push to the end.
    """
    config_order = [g.name for g in config.settings.digest_groups]
    localized_other = get_ui_strings(config.settings.output_language).get("group_other", "Other")

    def _is_other(name: str) -> bool:
        return name == localized_other or name.lower() == "other"

    not_config_ordered = grouped.keys() - set(config_order)
    remaining = sorted(k for k in not_config_ordered if not _is_other(k))
    other_keys = sorted(k for k in not_config_ordered if _is_other(k))
    return [n for n in config_order if n in grouped] + remaining + other_keys


async def _build_grouped_parts(
    config: Config,
    logger: logging.Logger,
    source: MessageSource,
    hours: int,
) -> tuple[list[tuple[str, str]], str] | None:
    """Build topic-grouped digest messages. Returns None if there is nothing to send."""
    messages_by_channel = await collect_messages(config, logger, source, hours)
    if not sum(len(msgs) for msgs in messages_by_channel.values()):
        logger.warning("No messages collected, skipping digest generation")
        return None

    summary_result = await _summarize_channels(config, logger, messages_by_channel)
    valid_summaries = _filter_valid_summaries(summary_result["channel_summaries"])
    if not valid_summaries:
        logger.warning("No valid channel summaries to group")
        return None

    logger.info("Grouping summaries by topic")
    channel_urls = await _get_channel_urls(config, source, logger)

    grouper = DigestGrouper(config, logger)
    grouped = await grouper.group_summaries(valid_summaries, channel_urls)
    if not grouped:
        logger.warning("No groups produced, skipping send")
        return None

    logger.info("Formatting group messages")
    formatter = DigestFormatter(config, logger)
    group_messages = _format_group_messages(formatter, grouped, config, hours)
    if not group_messages:
        logger.warning("No valid group messages to send")
        return None

    total_points = sum(len(pts) for pts in grouped.values())

    # Same group can appear in multiple chunks when its formatted message
    # exceeds split_message threshold; dedupe while preserving order so the
    # summary header lists each group exactly once.
    group_names = list(dict.fromkeys(name for name, _ in group_messages))
    summary_message = formatter.format_group_summary_message(
        group_names=group_names,
        total_points=total_points,
        hours=hours,
    )
    return group_messages, summary_message


async def _build_channel_parts(
    config: Config,
    logger: logging.Logger,
    source: MessageSource,
    hours: int,
) -> tuple[list[tuple[str, str]], str] | None:
    """Build one digest message per channel. Returns None if there is nothing to send."""
    messages_by_channel = await collect_messages(config, logger, source, hours)
    total_messages = sum(len(msgs) for msgs in messages_by_channel.values())
    if total_messages == 0:
        logger.warning("No messages collected, skipping digest generation")
        return None

    summary_result = await _summarize_channels(config, logger, messages_by_channel)
    valid_summaries = _filter_valid_summaries(summary_result["channel_summaries"])

    channel_urls = await _get_channel_urls(config, source, logger)

    formatter = DigestFormatter(config, logger)
    channel_messages = []

    for channel_name, summary in valid_summaries.items():
        messages = messages_by_channel.get(channel_name, [])
        formatted_message = formatter.format_channel_message(
            channel_name=channel_name,
            summary=summary,
            messages=messages,
            hours=hours,
            channel_url=channel_urls.get(channel_name),
        )
        channel_messages.append((channel_name, formatted_message))

    if not channel_messages:
        logger.warning("No valid channel messages to send")
        return None

    summary_message = formatter.format_summary_message(
        total_channels=len(channel_messages),
        total_messages=total_messages,
        hours=hours,
    )
    return channel_messages, summary_message


async def build_digest_parts(
    config: Config,
    logger: logging.Logger,
    source: MessageSource,
    hours: int,
) -> tuple[list[tuple[str, str]], str] | None:
    """Collect, summarize and format the digest according to the configured digest_mode.

    Single chokepoint for every digest producer (scheduler, bot, MCP server), so the
    lock and the cache write only need to exist here.

    Returns:
        (messages, summary_header) or None when there is nothing worth sending
    """
    validate_hours(hours)

    async with digest_lock:
        mode = config.settings.digest_mode
        start_time = datetime.now(timezone.utc)
        logger.info(f"Starting {mode!r} digest build for last {hours} hours")

        if mode == "digest":
            built = await _build_grouped_parts(config, logger, source, hours)
        else:
            built = await _build_channel_parts(config, logger, source, hours)

        if built is None:
            return None

        parts, summary_message = built

        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(f"Digest build completed in {execution_time:.1f}s")
        return parts, summary_message


def join_parts(parts: list[tuple[str, str]], summary_message: str) -> str:
    """Join digest messages into one document, header first (matches send order)."""
    return "\n\n".join([summary_message, *(text for _, text in parts)])
