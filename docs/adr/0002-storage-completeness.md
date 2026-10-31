-

## ADR 0002: Stored Message History Is Not Proof of Collection Completeness

**Status:** Accepted

**Date:** 2026-10-31

### Context

The message store records individual messages, but it does not record successful collection
windows, pagination completion, source failures, or the filters applied during collection.
A non-empty query result therefore proves only that some messages were stored. It does not
prove that the store contains every message in the requested time window. An empty result
likewise cannot distinguish a genuinely quiet channel from a failed or incomplete collection.

The live Telegram source can also isolate channel-level failures, so the absence of stored
messages cannot safely be interpreted as proof that a successful fetch returned no messages.

### Decision

`collect_channel_messages` always fetches the requested window from the configured live
source. Stored messages remain available through the storage query API for history and export,
but they are not treated as an authoritative cache for digest or MCP collection.

Storage implementations normalize nullable `Message.link` and `Message.media_type` values
to empty strings when persisting them. This preserves the existing non-null database schema
and gives SQLite and PostgreSQL the same representation.

### Consequences

- MCP channel-message requests report live-source results rather than implying cache coverage.
- Storage remains useful for historical queries and external consumers.
- A future cache-first design must persist explicit per-channel collection coverage, including
  the requested time interval and whether collection completed without truncation or failure.
  Coverage must also account for relevant filtering semantics before stored messages can
  replace a live fetch.
