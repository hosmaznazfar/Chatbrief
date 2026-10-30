"""Tests for digest collection, building, caching, and delivery."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chatbrief.config.models import ChannelConfig, DigestGroupConfig, FilterSpec, StorageConfig
from chatbrief.digest import builder as digest_builder
from chatbrief.digest import cache as digest_cache
from chatbrief.digest import collector as digest_collector
from chatbrief.digest.builder import build_digest_parts
from chatbrief.digest.cache import read_last_digest
from chatbrief.digest.collector import (
    _apply_filters,
    _resolve_channel,
    collect_channel_messages,
    collect_messages,
)
from chatbrief.digest.service import build_digest, generate_and_send_digest
from chatbrief.digest.validators import validate_hours
from chatbrief.grouper import GroupedPoint


def _make_source(sample_messages):
    """Create a mock source implementing the platform-neutral contract."""
    source = MagicMock()
    source.connect = AsyncMock()
    source.disconnect = AsyncMock()
    source.fetch_messages = AsyncMock(return_value={"Test Channel": sample_messages})
    source.fetch_channel_messages = AsyncMock(return_value=sample_messages)
    source.get_channel_url = AsyncMock(return_value=None)
    return source


def _make_sender(send_result=True):
    """Create a mock sender implementing the platform-neutral contract."""
    sender = MagicMock()
    sender.cleanup_old_digests = AsyncMock(return_value=True)
    sender.send_channel_messages_with_tracking = AsyncMock(return_value=send_result)
    return sender


def _configure_channel_builder(monkeypatch, summaries=None):
    """Replace AI and formatting dependencies for the channel digest path."""
    summarizer = MagicMock()
    summarizer.summarize_all = AsyncMock(
        return_value={
            "channel_summaries": summaries or {"Test Channel": "Summary"},
            "overview": "Overview",
        }
    )
    formatter = MagicMock()
    formatter.format_channel_message.return_value = "Channel msg"
    formatter.format_summary_message.return_value = "Header"
    monkeypatch.setattr(digest_builder, "Summarizer", lambda *_: summarizer)
    monkeypatch.setattr(digest_builder, "DigestFormatter", lambda *_: formatter)
    return summarizer, formatter


def _configure_group_builder(monkeypatch, grouped):
    """Replace AI, grouping, and formatting dependencies for topic digests."""
    summarizer = MagicMock()
    summarizer.summarize_all = AsyncMock(
        return_value={
            "channel_summaries": {"Test Channel": "- Point A\n- Point B"},
            "overview": "Overview",
        }
    )
    grouper = MagicMock()
    grouper.group_summaries = AsyncMock(return_value=grouped)
    formatter = MagicMock()
    formatter.format_group_message.side_effect = lambda group_name, **_: f"{group_name} msg"
    formatter.format_group_summary_message.return_value = "Summary header"
    monkeypatch.setattr(digest_builder, "Summarizer", lambda *_: summarizer)
    monkeypatch.setattr(digest_builder, "DigestGrouper", lambda *_: grouper)
    monkeypatch.setattr(digest_builder, "DigestFormatter", lambda *_: formatter)
    return summarizer, grouper, formatter


@pytest.mark.unit
@pytest.mark.asyncio
async def test_build_digest_uses_injected_source_and_formats_channel_output(
    sample_config, mock_logger, sample_messages, monkeypatch
):
    source = _make_source(sample_messages)
    summarizer, formatter = _configure_channel_builder(monkeypatch)

    result = await build_digest(sample_config, mock_logger, source, hours=24)

    assert result == "Header\n\nChannel msg"
    source.connect.assert_awaited_once()
    source.fetch_messages.assert_awaited_once_with(hours=24)
    source.disconnect.assert_awaited_once()
    summarizer.summarize_all.assert_awaited_once()
    formatter.format_channel_message.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_build_digest_disconnects_when_collection_fails(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    source.fetch_messages.side_effect = RuntimeError("Collection failed")

    with pytest.raises(RuntimeError, match="Collection failed"):
        await build_digest(sample_config, mock_logger, source, hours=24)

    source.disconnect.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_and_send_digest_caches_and_sends_result(
    sample_config, mock_logger, sample_messages, monkeypatch, tmp_path
):
    source = _make_source(sample_messages)
    sender = _make_sender()
    _configure_channel_builder(monkeypatch)
    monkeypatch.setattr(digest_cache, "_DIGEST_CACHE_PATH", tmp_path / "last_digest.json")

    result = await generate_and_send_digest(
        sample_config, mock_logger, source, sender, hours=12, user_id=123456789
    )

    assert result is True
    sender.cleanup_old_digests.assert_awaited_once_with(123456789)
    sender.send_channel_messages_with_tracking.assert_awaited_once_with(
        [("Test Channel", "Channel msg")], "Header", 123456789
    )
    cached = read_last_digest()
    assert cached is not None
    assert cached["text"] == "Header\n\nChannel msg"
    assert cached["hours"] == 12
    assert cached["generated_at"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_and_send_digest_returns_false_when_sender_fails(
    sample_config, mock_logger, sample_messages, monkeypatch
):
    source = _make_source(sample_messages)
    sender = _make_sender(send_result=False)
    _configure_channel_builder(monkeypatch)

    result = await generate_and_send_digest(
        sample_config, mock_logger, source, sender, hours=24
    )

    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_and_send_digest_validates_hours_before_runtime_handling(
    sample_config, mock_logger, sample_messages
):
    with pytest.raises(ValueError, match="hours must be"):
        await generate_and_send_digest(
            sample_config, mock_logger, _make_source(sample_messages), _make_sender(), hours=0
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_grouped_digest_builds_and_sends_topic_messages(
    sample_config, mock_logger, sample_messages, monkeypatch
):
    sample_config.settings.digest_mode = "digest"
    source = _make_source(sample_messages)
    sender = _make_sender()
    grouped = {
        "News": [GroupedPoint(point="Point A", source="Test Channel")],
        "Other": [GroupedPoint(point="Point B", source="Test Channel")],
    }
    summarizer, grouper, formatter = _configure_group_builder(monkeypatch, grouped)

    result = await generate_and_send_digest(
        sample_config, mock_logger, source, sender, hours=24, user_id=123456789
    )

    assert result is True
    summarizer.summarize_all.assert_awaited_once()
    grouper.group_summaries.assert_awaited_once()
    assert formatter.format_group_message.call_count == 2
    formatter.format_group_summary_message.assert_called_once()
    sent = sender.send_channel_messages_with_tracking.call_args.args[0]
    assert sent == [("News", "News msg"), ("Other", "Other msg")]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_grouped_digest_skips_empty_groups(
    sample_config, mock_logger, sample_messages, monkeypatch
):
    sample_config.settings.digest_mode = "digest"
    source = _make_source(sample_messages)
    grouped = {
        "News": [GroupedPoint(point="Point A", source="Test Channel")],
        "Sport": [],
    }
    _, _, formatter = _configure_group_builder(monkeypatch, grouped)

    result = await build_digest_parts(sample_config, mock_logger, source, hours=24)

    assert result is not None
    formatter.format_group_message.assert_called_once_with(
        group_name="News",
        points=[GroupedPoint(point="Point A", source="Test Channel")],
        hours=24,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_channel_mode_does_not_instantiate_topic_grouper(
    sample_config, mock_logger, sample_messages, monkeypatch
):
    source = _make_source(sample_messages)
    _configure_channel_builder(monkeypatch)
    with patch.object(digest_builder, "DigestGrouper") as grouper:
        result = await build_digest_parts(sample_config, mock_logger, source, hours=24)

    assert result is not None
    grouper.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_split_group_name_is_listed_once_in_summary_header(
    sample_config, mock_logger, sample_messages, monkeypatch
):
    sample_config.settings.digest_mode = "digest"
    source = _make_source(sample_messages)
    grouped = {"News": [GroupedPoint(point="Point A", source="Test Channel")]}
    _, _, formatter = _configure_group_builder(monkeypatch, grouped)
    formatter.format_group_message.side_effect = None
    formatter.format_group_message.return_value = "x" * 4500

    result = await build_digest_parts(sample_config, mock_logger, source, hours=24)

    assert result is not None
    assert len(result[0]) > 1
    assert formatter.format_group_summary_message.call_args.kwargs["group_names"] == ["News"]


@pytest.mark.unit
def test_order_groups_places_other_last(sample_config):
    sample_config.settings.output_language = "Russian"
    grouped = {"News": [], "Other": [], "Sport": []}

    order = digest_builder._order_groups(grouped, sample_config)

    assert order[-1] == "Other"
    assert set(order) == set(grouped)


@pytest.mark.unit
def test_order_groups_handles_case_insensitive_other(sample_config):
    grouped = {"News": [], "OTHER": [], "Sport": []}

    order = digest_builder._order_groups(grouped, sample_config)

    assert order[-1] == "OTHER"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_messages_without_storage_returns_filtered_messages(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    sample_config.storage = StorageConfig(enabled=False)

    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        return_value=None,
    ):
        result = await collect_messages(sample_config, mock_logger, source, hours=24)

    assert result == {"Test Channel": sample_messages}
    source.connect.assert_awaited_once()
    source.disconnect.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_messages_saves_flat_filtered_messages(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    sample_config.storage = StorageConfig(enabled=True, backend="sqlite", path=":memory:")
    backend = MagicMock()
    backend.save_messages = AsyncMock(return_value=len(sample_messages))
    backend.close = AsyncMock()

    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        return_value=backend,
    ):
        result = await collect_messages(sample_config, mock_logger, source, hours=24)

    assert result == {"Test Channel": sample_messages}
    backend.save_messages.assert_awaited_once_with(sample_messages)
    backend.close.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_messages_storage_initialization_failure_is_non_fatal(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        side_effect=RuntimeError("db down"),
    ):
        result = await collect_messages(sample_config, mock_logger, source, hours=24)

    assert result == {"Test Channel": sample_messages}
    mock_logger.error.assert_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_messages_storage_write_and_close_failures_are_non_fatal(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    sample_config.storage = StorageConfig(enabled=True, backend="sqlite", path=":memory:")
    backend = MagicMock()
    backend.save_messages = AsyncMock(side_effect=RuntimeError("write failed"))
    backend.close = AsyncMock(side_effect=RuntimeError("close failed"))

    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        return_value=backend,
    ):
        result = await collect_messages(sample_config, mock_logger, source, hours=24)

    assert result == {"Test Channel": sample_messages}
    backend.close.assert_awaited_once()
    assert mock_logger.error.call_count >= 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_messages_applies_filters_before_storage(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    sample_config.settings.filters = [
        FilterSpec(
            class_path="chatbrief.extensions.filters.MinLengthFilter",
            config={"min_chars": 99999},
        )
    ]
    sample_config.storage = StorageConfig(enabled=True, backend="sqlite", path=":memory:")
    backend = MagicMock()
    backend.save_messages = AsyncMock(return_value=0)
    backend.close = AsyncMock()

    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        return_value=backend,
    ):
        result = await collect_messages(sample_config, mock_logger, source, hours=24)

    assert result == {"Test Channel": []}
    backend.save_messages.assert_awaited_once_with([])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_apply_filters_empty_specs_preserve_messages(
    sample_config, mock_logger, sample_messages
):
    sample_config.settings.filters = []
    channel = ChannelConfig(id="@test", name="Test Channel")

    result = await _apply_filters(channel, sample_messages, sample_config, mock_logger)

    assert result == sample_messages


@pytest.mark.unit
@pytest.mark.asyncio
async def test_channel_empty_filter_list_overrides_global_filters(
    sample_config, mock_logger, sample_messages
):
    sample_config.settings.filters = [
        FilterSpec(
            class_path="chatbrief.extensions.filters.MinLengthFilter",
            config={"min_chars": 99999},
        )
    ]
    channel = ChannelConfig(id="@test", name="Test Channel", filters=[])

    result = await _apply_filters(channel, sample_messages, sample_config, mock_logger)

    assert result == sample_messages


@pytest.mark.unit
@pytest.mark.asyncio
async def test_channel_filter_list_replaces_global_filter_chain(
    sample_config, mock_logger, sample_messages
):
    sample_config.settings.filters = [
        FilterSpec(
            class_path="chatbrief.extensions.filters.MinLengthFilter",
            config={"min_chars": 99999},
        )
    ]
    channel = ChannelConfig(
        id="@test",
        name="Test Channel",
        filters=[
            FilterSpec(
                class_path="chatbrief.extensions.filters.KeywordFilter",
                config={"include": ["message 2"]},
            )
        ],
    )

    result = await _apply_filters(channel, sample_messages, sample_config, mock_logger)

    assert [message.text for message in result] == ["Test message 2"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_filter_initialization_failure_is_logged_and_skipped(
    sample_config, mock_logger, sample_messages
):
    class BrokenConstructor:
        def __init__(self):
            raise RuntimeError("invalid configuration")

    sample_config.settings.filters = [FilterSpec("broken.filter", {})]
    channel = ChannelConfig(id="@test", name="Test Channel")
    with patch.object(digest_collector, "load_class", return_value=BrokenConstructor):
        result = await _apply_filters(channel, sample_messages, sample_config, mock_logger)

    assert result == sample_messages
    mock_logger.error.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_filter_chain_applies_in_order(sample_config, mock_logger):
    from datetime import datetime, timezone

    from chatbrief.message import Message

    messages = [
        Message(
            "hello job",
            "user",
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            "#",
            "Test",
            False,
            "",
        ),
        Message(
            "job at company",
            "user",
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            "#",
            "Test",
            False,
            "",
        ),
        Message(
            "hello world",
            "user",
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            "#",
            "Test",
            False,
            "",
        ),
    ]
    sample_config.settings.filters = [
        FilterSpec("chatbrief.extensions.filters.KeywordFilter", {"include": ["job"]}),
        FilterSpec("chatbrief.extensions.filters.KeywordFilter", {"exclude": ["company"]}),
    ]
    channel = ChannelConfig(id="@test", name="Test")

    result = await _apply_filters(channel, messages, sample_config, mock_logger)

    assert [message.text for message in result] == ["hello job"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unresolvable_filter_is_logged_and_skipped(
    sample_config, mock_logger, sample_messages
):
    sample_config.settings.filters = [FilterSpec("missing.filter", {})]
    channel = ChannelConfig(id="@test", name="Test Channel")
    with patch.object(digest_collector, "load_class", side_effect=ImportError("missing filter")):
        result = await _apply_filters(channel, sample_messages, sample_config, mock_logger)

    assert result == sample_messages
    mock_logger.error.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_filter_exception_is_isolated_from_following_filters(
    sample_config, mock_logger, sample_messages
):
    class BrokenFilter:
        name = "broken"

        def __init__(self):
            pass

        async def filter(self, channel, messages):
            raise RuntimeError("filter failed")

    class PassFilter:
        name = "pass"

        def __init__(self):
            pass

        async def filter(self, channel, messages):
            return messages[:1]

    sample_config.settings.filters = [
        FilterSpec("broken", {}),
        FilterSpec("pass", {}),
    ]
    channel = ChannelConfig(id="@test", name="Test Channel")
    with patch.object(
        digest_collector, "load_class", side_effect=[BrokenFilter, PassFilter]
    ):
        result = await _apply_filters(channel, sample_messages, sample_config, mock_logger)

    assert result == sample_messages[:1]
    mock_logger.error.assert_called_once()


@pytest.mark.unit
@pytest.mark.parametrize(
    "wanted", ["Test Channel", "test channel", "@test_channel", " @TEST_CHANNEL "]
)
def test_resolve_channel_matches_name_or_id(sample_config, wanted):
    assert _resolve_channel(sample_config, wanted).name == "Test Channel"


@pytest.mark.unit
def test_resolve_channel_unknown_lists_configured_names(sample_config):
    with pytest.raises(ValueError, match="Test Channel, Private Group"):
        _resolve_channel(sample_config, "Nope")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_channel_messages_prefers_storage(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    sample_config.storage = StorageConfig(enabled=True, backend="sqlite", path=":memory:")
    backend = MagicMock()
    backend.query_messages = AsyncMock(return_value=list(reversed(sample_messages)))
    backend.close = AsyncMock()

    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        return_value=backend,
    ):
        messages, origin = await collect_channel_messages(
            sample_config, mock_logger, source, "Test Channel", hours=12, limit=50
        )

    assert origin == "storage"
    assert messages == sample_messages
    backend.query_messages.assert_awaited_once()
    backend.close.assert_awaited_once()
    source.connect.assert_not_awaited()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_channel_messages_falls_back_to_live_source(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    sample_config.storage = StorageConfig(enabled=False)

    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        return_value=None,
    ):
        messages, origin = await collect_channel_messages(
            sample_config, mock_logger, source, "@test_channel", hours=6
        )

    assert origin == "live"
    assert messages == sample_messages
    source.connect.assert_awaited_once()
    source.fetch_channel_messages.assert_awaited_once()
    source.disconnect.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_channel_messages_falls_back_when_storage_is_empty(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    sample_config.storage = StorageConfig(enabled=True, backend="sqlite", path=":memory:")
    backend = MagicMock()
    backend.query_messages = AsyncMock(return_value=[])
    backend.close = AsyncMock()

    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        return_value=backend,
    ):
        messages, origin = await collect_channel_messages(
            sample_config, mock_logger, source, "Test Channel"
        )

    assert origin == "live"
    assert messages == sample_messages
    backend.close.assert_awaited_once()
    source.disconnect.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_channel_messages_falls_back_when_storage_query_fails(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    sample_config.storage = StorageConfig(enabled=True, backend="sqlite", path=":memory:")
    backend = MagicMock()
    backend.query_messages = AsyncMock(side_effect=RuntimeError("read failed"))
    backend.close = AsyncMock()

    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        return_value=backend,
    ):
        messages, origin = await collect_channel_messages(
            sample_config, mock_logger, source, "Test Channel"
        )

    assert origin == "live"
    assert messages == sample_messages
    backend.close.assert_awaited_once()
    source.disconnect.assert_awaited_once()
    mock_logger.error.assert_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_channel_messages_storage_failure_falls_back_to_live(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    sample_config.storage = StorageConfig(enabled=True, backend="sqlite", path=":memory:")

    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        side_effect=RuntimeError("db down"),
    ):
        messages, origin = await collect_channel_messages(
            sample_config, mock_logger, source, "Test Channel"
        )

    assert origin == "live"
    assert messages == sample_messages
    source.disconnect.assert_awaited_once()
    mock_logger.error.assert_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collect_channel_messages_keeps_newest_within_limit(
    sample_config, mock_logger, sample_messages
):
    source = _make_source(sample_messages)
    source.fetch_channel_messages.return_value = sample_messages
    with patch.object(
        digest_collector,
        "create_storage",
        new_callable=AsyncMock,
        return_value=None,
    ):
        messages, _ = await collect_channel_messages(
            sample_config, mock_logger, source, "Test Channel", limit=1
        )

    assert messages == sample_messages[-1:]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, -1, 501, True, 2.5, "10"])
async def test_collect_channel_messages_rejects_invalid_limit(
    sample_config, mock_logger, sample_messages, limit
):
    source = _make_source(sample_messages)
    with patch.object(digest_collector, "create_storage", new_callable=AsyncMock) as create_storage:
        with pytest.raises(ValueError, match="limit must be between"):
            await collect_channel_messages(
                sample_config, mock_logger, source, "Test Channel", limit=limit
            )

    create_storage.assert_not_awaited()
    source.connect.assert_not_awaited()


@pytest.mark.unit
def test_read_last_digest_ignores_corrupt_cache(tmp_path, monkeypatch):
    cache = tmp_path / "corrupt.json"
    cache.write_text('{"text": "half-writ', encoding="utf-8")
    monkeypatch.setattr(digest_cache, "_DIGEST_CACHE_PATH", cache)

    assert read_last_digest() is None


@pytest.mark.unit
@pytest.mark.parametrize("hours", [0, -1, 169, 1000, True, 2.5, "24"])
def test_validate_hours_rejects_invalid_input(hours):
    with pytest.raises(ValueError):
        validate_hours(hours)


@pytest.mark.unit
@pytest.mark.parametrize("hours", [1, 24, 168])
def test_validate_hours_accepts_valid_input(hours):
    validate_hours(hours)
