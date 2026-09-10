import inspect
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from src.config.models import ChannelConfig, Config
from src.constants import MAX_CHANNEL_MESSAGES
from src.extensions.loader import load_class
from src.message import Message
from src.platforms.base import MessageSource
from src.storage import create_storage

from .state import digest_lock
from .validators import validate_hours


async def _save_to_storage(
    config: Config, messages_by_channel: dict, logger: logging.Logger
) -> None:
    """Persist collected messages to the configured storage backend, if enabled."""
    sc = config.storage
    storage = None
    try:
        storage = await create_storage(sc)
    except Exception as e:
        logger.error(
            f"Storage init failed ({type(e).__name__}), digest continues",
            exc_info=True,
        )
    if storage:
        try:
            flat = [msg for msgs in messages_by_channel.values() for msg in msgs]
            saved = await storage.save_messages(flat)
            logger.info(f"Stored {saved} messages ({sc.backend})")
        except Exception as e:
            logger.error(
                f"Storage write failed ({type(e).__name__}), digest continues",
                exc_info=True,
            )
        finally:
            try:
                await storage.close()
            except Exception as e:
                logger.error(
                    f"Storage close failed ({type(e).__name__})",
                    exc_info=True,
                )


async def _apply_filters(
    channel_cfg: ChannelConfig,
    messages: list,
    config: Config,
    logger: logging.Logger,
) -> list:
    """Apply the effective filter chain to messages for a given channel."""
    effective_specs = (
        channel_cfg.filters if channel_cfg.filters is not None else config.settings.filters
    )
    if not effective_specs:
        return messages

    for spec in effective_specs:
        try:
            cls = load_class(spec.class_path)
            filter_instance = cls(**spec.config)
        except Exception as e:
            logger.error(
                f"Filter load/init failed ({spec.class_path}, {type(e).__name__}), skipping",
                exc_info=True,
            )
            continue
        if not hasattr(filter_instance, "filter"):
            logger.error(
                f"Filter {spec.class_path!r} missing filter() method, skipping",
            )
            continue
        if not inspect.iscoroutinefunction(filter_instance.filter):
            logger.error(
                f"Filter {spec.class_path!r} filter() is not async — add 'async' keyword, skipping",
            )
            continue
        try:
            result = await filter_instance.filter(channel_cfg, messages)
            if not isinstance(result, list):
                logger.error(
                    f"Filter {getattr(filter_instance, 'name', spec.class_path)!r} filter() returned"
                    f" {type(result).__name__} (expected list), skipping",
                )
            else:
                messages = result
        except Exception as e:
            logger.error(
                f"Filter {getattr(filter_instance, 'name', spec.class_path)!r} filter() raised"
                f" {type(e).__name__} ({spec.class_path}), skipping",
                exc_info=True,
            )

    return messages


async def _channel_from_storage(
    config: Config,
    logger: logging.Logger,
    channel_cfg: ChannelConfig,
    since: datetime,
    limit: int,
) -> Optional[list[Message]]:
    """Read one channel from storage. None when storage is off, empty or unreadable."""
    try:
        storage = await create_storage(config.storage)
    except Exception as e:
        logger.error(f"Storage init failed ({type(e).__name__}), falling back to live source")
        return None

    if storage is None:
        return None

    try:
        messages = await storage.query_messages(
            channel_name=channel_cfg.name,
            since=since,
            limit=limit,
        )
        messages.reverse()  # query_messages returns newest first
        return messages or None
    except Exception as e:
        logger.error(f"Storage read failed ({type(e).__name__}), falling back to live source")
        return None
    finally:
        try:
            await storage.close()
        except Exception as e:
            logger.error(
                f"Storage close failed ({type(e).__name__})",
                exc_info=True,
            )


def _resolve_channel(config: Config, channel: str) -> ChannelConfig:
    """Find the configured channel by its name or its id.

    Raises:
        ValueError: If no configured channel matches
    """
    wanted = channel.strip().lower()
    for ch in config.channels:
        if wanted in (ch.name.lower(), str(ch.id).lower()):
            return ch
    known = ", ".join(ch.name for ch in config.channels) or "none configured"
    raise ValueError(f"Unknown channel {channel!r}. Configured channels: {known}")


async def collect_channel_messages(
    config: Config,
    logger: logging.Logger,
    source: MessageSource,
    channel: str,
    hours: int = 24,
    limit: int = 200,
) -> tuple[list[Message], str]:
    """Fetch one channel's messages, preferring stored ones over a live source read.

    Args:
        config: Application configuration
        logger: Logger instance
        source: Message source used when stored messages are unavailable
        channel: Channel name or id as configured under channels[*]
        hours: Lookback window
        limit: Maximum messages to return, newest kept

    Returns:
        (messages in chronological order, source) where source is "storage" or "live"

    Raises:
        ValueError: If hours or limit are out of range, or channel is not configured
    """
    validate_hours(hours)
    if (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or not 1 <= limit <= MAX_CHANNEL_MESSAGES
    ):
        raise ValueError(f"limit must be between 1 and {MAX_CHANNEL_MESSAGES}, got {limit!r}")

    channel_cfg = _resolve_channel(config, channel)
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    stored = await _channel_from_storage(config, logger, channel_cfg, since, limit)
    if stored is not None:
        logger.info(f"Read {len(stored)} stored messages for {channel_cfg.name!r}")
        return stored, "storage"

    # Same process-wide lock as digest builds — one live source session at a time.
    async with digest_lock:
        await source.connect()
        try:
            messages = await source.fetch_channel_messages(channel_cfg, since)
        finally:
            await source.disconnect()

    # Filters run outside the lock: they are user code and may block on the network.
    messages = await _apply_filters(channel_cfg, messages, config, logger)
    logger.info(f"Fetched {len(messages)} live messages for {channel_cfg.name!r}")
    return messages[-limit:], "live"


async def collect_messages(
    config: Config,
    logger: logging.Logger,
    source: MessageSource,
    hours: int,
) -> dict:
    """Collect messages from configured channels using the provided message source."""
    logger.info("Collecting messages from configured channels")

    await source.connect()
    try:
        messages_by_channel = await source.fetch_messages(hours=hours)
    finally:
        await source.disconnect()

    total = sum(len(msgs) for msgs in messages_by_channel.values())
    logger.info(f"Collected {total} messages from {len(messages_by_channel)} channels")

    channel_map = {ch.name: ch for ch in config.channels}
    filtered: dict = {}
    for channel_name, msgs in messages_by_channel.items():
        ch_cfg = channel_map.get(channel_name)
        if ch_cfg is not None:
            msgs = await _apply_filters(ch_cfg, msgs, config, logger)
        else:
            logger.warning(f"Channel {channel_name!r} not in config; skipping filters")
        filtered[channel_name] = msgs
    messages_by_channel = filtered

    await _save_to_storage(config, messages_by_channel, logger)
    return messages_by_channel
