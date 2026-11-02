# Chatbrief — persistent project context

Repository: https://github.com/hosmaznazfar/Chatbrief  
Active branch: `refactor/chatbrief-package-layout`  
Primary package: `src/chatbrief/`  
Python: `>=3.14`; package/dependency manager: `uv`

## Current project status — 2026-11-02

- Active branch: `refactor/chatbrief-package-layout`; latest delivery-attempt lease-fencing implementation is ahead of the developer's last reported local sync, so fast-forward before local validation.
- Package-layout/platform refactor and dependency upgrades are complete.
- Major architecture decisions and proposals are approved, including Telegram hybrid ingestion and Phase 1 export persistence. Do not reopen them without a concrete implementation contradiction.
- Application-state SQLite database foundation, migration runner, export schema, and startup integration are implemented and developer-validated. The optional legacy message-history database remains independent and unchanged.
- Export persistence Steps 3a–3b are implemented and developer-validated. Step 3b results: focused tests **119 passed**; Ruff lint and format passed; Pyright **0 errors, 0 warnings, 0 informations**; full suite **622 passed, 7 skipped**, coverage **94.07%**.
- Step 3c worker lease operations are implemented and developer-validated: atomic due-job claims, bounded lease expiry, generation increments, renewal/release, retry scheduling, and generation-fenced state transitions. Latest full suite: **627 passed, 7 skipped**, coverage **93.38%**; Ruff lint/format and Pyright passed.
- Step 3d fair per-user claim scheduling is implemented and developer-validated: focused tests **33 passed**, Ruff lint/format and Pyright passed, full suite **629 passed, 7 skipped**, coverage **93.39%**.
- Step 3e delivery-attempt lease fencing is implemented remotely with migration 3. Each new attempt persists its creating worker ID and lease generation; start/finish require a live matching lease, and attempts cannot be finalized by a replacement worker using a newer generation. Local validation is pending.
- Worker orchestration, bounded concurrency configuration, graceful shutdown, user-facing export commands, archive generation, actual Telegram network delivery, cleanup execution, and broader hybrid-ingestion migration remain future work.
- Graphify is optional development tooling used to navigate code relationships; generated graph artifacts are not application features or a prerequisite for implementation. Verify source and tests directly.
- Continue in small dependency-ordered implementation slices, with focused tests and documentation updates.
## Read first

At the start of a new session, verify the repository and branch, then read:

1. `AI_README.md`
2. `docs/handover/current.md`
3. `FEATURE_IMPLEMENTATION_CHECKLIST.md`
4. `README.md`
5. `docs/AI_WORKFLOW.md`
6. `docs/GRAPHIFY.md`
7. Relevant ADRs in `docs/adr/`, plans in `docs/plans/`, and the current source/tests.

The handover is a snapshot, not proof of current state. GitHub does not expose the developer's local uncommitted work.

## Product and stack

Chatbrief is an asynchronous, AI-powered digest application. The current implementation collects Telegram messages, summarizes/groups them using configurable AI providers, and delivers digests. It also has scheduling, storage, extension hooks, and an optional MCP server. Bale is a future platform target, not an implemented adapter.

The repository includes:
- Python application/package under `src/chatbrief/`
- Root entry point/composition root: `main.py`
- Python dependencies and tool configuration: `pyproject.toml`, `uv.lock`
- Tests: `tests/`
- CI: `.github/workflows/ci.yml`
- Architecture decisions and plans: `docs/adr/`, `docs/plans/`

## Architectural decisions to preserve

- Domain/digest logic must not import or know Telegram/Bale SDK details.
- Platform adapters own authentication, fetching, sending, URL construction, and platform-specific behavior.
- `Message` contains intrinsic generic message data only; do not add platform-specific channel metadata to it.
- `Message.link` is the individual message link. Channel/source attribution is handled at the grouped digest/platform boundary.
- `MessageSource.get_channel_url(ChannelConfig)` owns channel URL generation; formatters must not parse Telegram URL syntax.
- Services receive `MessageSource` / `MessageSender` dependencies rather than constructing platform clients.
- `PlatformBuilder` and root `main.py` compose concrete platform services.
- `src/core.py` was removed after its responsibilities were migrated to focused modules.
- Keep the standard `src/chatbrief` package layout. Root `main.py` remains the executable composition root.
- Do not implement Bale configuration/credentials as if the adapter already exists.
- Keep existing ADRs authoritative; record material architecture changes explicitly.

## Approved target direction: hybrid Telegram ingestion

The approved future direction is documented in [docs/plans/telegram-hybrid-ingestion.md](docs/plans/telegram-hybrid-ingestion.md). This is a plan, not implemented functionality.

- The same plan also contains the approved personal data export design: two Telegram-delivered ZIPs (primary text plus optional media), durable per-user asynchronous jobs, 24-hour initial availability, authorization checks, cancellation, restart recovery, and explicit confirmed `/export retry` for ambiguous delivery. Export is planned, not implemented; the detailed plan is the source of truth.
- The primary `export.json` uses separate top-level data sections (preferences, schedules, subscriptions, delivery history, messages, and source relationship records) with explicit export-scoped relationships; exact fields and reference format remain in detailed schema design.
- Primary `export.json` has a top-level integer `schema_version` starting at `1`, independent of the Chatbrief app version; increment for incompatible export-format changes. Exact fields and compatibility rules remain open in schema design.
- `export-report.json` also has its own top-level integer `schema_version` starting at `1`, independent of both `export.json` and the Chatbrief app version; increment it for incompatible report-format changes. The two documents can evolve independently.
- Optional `media-manifest.json` also has its own top-level integer `schema_version` starting at `1`, independent of both primary-archive documents and the Chatbrief app version; increment it for incompatible manifest-format changes. All three export documents can evolve independently.
- Both export ZIPs use `README.md` (not `README.txt`). Each README explains archive contents/usage and the `schema_version` of each JSON document it contains, including that document versions evolve independently and increment for incompatible format changes.
- Export JSON schema compatibility is conservative and independent per document: adding optional fields is compatible; removing/renaming fields, changing existing field types, or changing existing field meanings/semantics requires incrementing that document's `schema_version`. Additional edge cases remain for detailed schema design.
- Export-job persistence uses a hybrid relational design: separate job, delivery-attempt, and cleanup-task records, with JSON for evolving metadata/reports and no ZIP binaries in the database. Exact schema details remain open.
- Export workers use database-backed renewable leases with atomic claims and stale-worker fencing, allowing bounded concurrent jobs for different users in the initial single application instance. Telegram send ambiguity still requires explicit `DeliveryUnknown` reconciliation; exact lease/concurrency values remain open.
- Export queue scheduling is fair across users, with FIFO order within each user's queue; scheduling state must survive restarts and work with leased atomic claims. No priority tiers initially.
- Export worker concurrency is configurable via a global export-specific setting (provisionally `export.max_concurrent_jobs`), with a conservative default chosen after resource inspection; it is separate from the per-user active-export rule and does not auto-scale.
- Export workers shut down cooperatively: stop new claims, allow a bounded grace period, stop at safe checkpoints, and preserve durable recovery/cleanup state. Never blindly resend an ambiguous Telegram delivery after shutdown.
- Export-job metadata is deleted when its lifecycle ends: on Ready expiry, or after cleanup for Cancelled/Failed/Invalidated jobs. Retain only minimal durable cleanup/reconciliation records while actionable; do not keep archives or long-term delivery history.
- Telegram document delivery uses at most three attempts (initial plus two retries) for transient failures, with exponential backoff from 5 to 30 seconds and Telegram `retry_after` respected when longer. Permanent failures are not retried; ambiguous results remain `DeliveryUnknown` and require reconciliation.
- Export-message deletion cleanup retries temporary failures with bounded exponential backoff from 1 minute to 1 hour, respects longer Telegram `retry_after` delays, and stops on permanent errors or the 48-hour deletion-window boundary. Persist next-retry state for restart recovery; this does not extend export availability.
- Export progress is queried through `/export status` with named states only; send no intermediate-state notifications or percentages. Notify only on primary export `Ready`, `Failed`, or `Invalidated`.
- Temporary export archives use a dedicated private staging directory (`0700` directories, `0600` files, Chatbrief service-account access only); rely on host disk encryption where available, add no application-managed archive-encryption keys initially, and delete temporary files promptly when no longer needed.
- Media ZIP entries use predefined category directories and deterministic generated basenames derived from export-local `media_ref` values, with only validated safe extensions where known. Do not preserve original filenames in the ZIP or manifest because they may contain personal/third-party information. Validate generated paths; resolve any collision deterministically without overwriting. Exact safe-extension mapping and path validation remain implementation-review items.
- Retry only clearly transient export failures (such as temporary network/service outages or rate limits). Invalid input/data, authorization/access failures, unsupported media, size rejection, and configuration errors are permanent; unknown errors fail safely without automatic retry. Preserve the separate Telegram send/deletion retry rules and ambiguous-delivery handling. Verify exact exception mapping and phase-specific retry limits against installed dependencies and architecture before implementation.
- If the complete primary text export alone exceeds the configured archive/upload limit, fail clearly; never truncate, split, or silently omit primary structured data/messages. Narrowing export scope is not part of the initial design unless separately approved.
- Account deletion cancels queued/running exports, removes staging files, and immediately invalidates Ready exports; best-effort delete delivered primary/media Telegram messages. Retain only minimum actionable deletion metadata independent of the deleted user record, then remove job/attempt/cleanup metadata when cleanup is complete or no longer actionable. Telegram deletion cannot revoke downloaded/forwarded copies.
- If an included source or retained data item is removed (including by retention cleanup) before all applicable export Telegram deliveries finish, invalidate the entire export, stop remaining work, and remove staging files; do not deliver a partial or stale snapshot. Unrelated removals do not affect the job. If the primary was already sent while optional media remains, best-effort delete already-delivered export documents under the approved cleanup policy and retain only actionable cleanup metadata. A fresh request uses a new cutoff/current authorization. Exact event hooks and race/cleanup integration remain open.

- Retain the existing `python-telegram-bot` and Telethon libraries and preserve the current implementation while evolving it incrementally.
- Use the central Bot API integration as the default for continuous ingestion; ordinary Chatbrief users must not need to link a personal Telegram account.
- Keep Telethon as an explicit, optional per-user integration for historical backfill from chats accessible to that user's account.
- Normalize both ingestion paths into the same platform-neutral message pipeline; digest generation must not depend on the collection mechanism.
- Separate Telegram chat access, per-user source subscriptions, digest preferences, and digest grouping.
- Deduplicate overlapping Bot API and Telethon collection using a stable Telegram message identity and persistent uniqueness constraint.
- Treat each Telethon session as a credential owned by exactly one Chatbrief user; secure it at rest and provide disconnect/revocation.
- Before implementation, inspect the current storage/digest lifecycle and single-user assumptions, then propose the minimum data-model and migration changes. Do not assume the final schema in advance.
- Preserve the storage-completeness guarantee: stored rows alone do not prove a collection window is complete. Track collection coverage before using stored messages as an authoritative lookback source.

The current implementation remains single-user and Telethon-backed until these planned phases are implemented and verified. Do not describe multi-user hybrid ingestion as an available feature.

## Current refactor status (2026-10-30)

The package/platform implementation migration is complete on `refactor/chatbrief-package-layout`. The developer confirmed that tests have passed and all package/dependency upgrades are complete. Major architecture decisions and proposals are approved; the project is in the implementation stage.

Completed:
- Migrated test imports to `chatbrief.*` and moved legacy `tests/test_core.py` behavior coverage into `tests/test_digest.py`.
- Added platform-builder tests and updated the shared test configuration to include `Platform.TELEGRAM`.
- Removed the obsolete platform factory; the standalone summarizer now obtains platform services through `PlatformBuilder`.
- Made `TelegramBot` require an injected `CommandService`; root `main.py` remains the application composition root.
- Updated `CommandService` to use injected `MessageSource` and `MessageSender` dependencies.
- Fixed the remaining type-checking-only legacy package import.
- Aligned coverage targets with the `chatbrief` package.
- Updated current README/config/Docker instructions, moved the default prompt template to the package path while preserving the legacy config sentinel, and archived the completed extensibility/storage plans.

Remaining:
- Review the committed changes in the developer's local checkout without overwriting local work.
- Wait for explicit authorization to run Ruff, Pyright, Pylint, Bandit, Vulture, and the full pytest suite.
- Fix any validation findings and record actual results before declaring the refactor complete.

Do not treat the historical pre-refactor test baseline as evidence that the current branch passes.

## Graphify — local CLI, pj automation, and Git-shared graph

Graphify is the selected optional code-graph tool. It runs locally as a standalone CLI; no Codex/editor skill, MCP server, or assistant-specific integration is part of this workflow.

- Operational guide: `docs/GRAPHIFY.md`.
- Full AI workflow: `docs/AI_WORKFLOW.md`.
- Use `./pj graph refresh` and `./pj graph diff` when a new non-trivial task needs a fresh graph; the developer has already handled the graph step for the current refactor and no additional refresh is being requested here.
- The latest verified GitHub tree contains `graphify-out/graph.json` and `graphify-out/manifest.json`; `GRAPH_REPORT.md` and `graph.html` are absent from that remote snapshot. The developer's local state may differ.
- `.graphify_analysis.json` and `.graphify_root` are currently tracked. Review their portability separately; they are not blockers for the package/platform implementation.
- Graphify is not an application dependency and is not part of `.pj/workflow.toml`. It must not enter `pyproject.toml`, `uv.lock`, Docker, or application startup.
- ChatGPT using GitHub reads committed artifacts on the selected branch and verifies relationships against source, tests, and ADRs. It cannot run the developer's local CLI or see uncommitted changes.
- Treat graph relationships as navigation aids; verify important relationships against current source and tests.

## Development workflow contract

Follow `docs/AI_WORKFLOW.md` for the developer's required sequence: inspect the code and graph; request `./pj graph refresh` and `./pj graph diff` at the start of each non-trivial feature/fix/review; review and commit the graph artifacts; research material design options and ask for the developer's decision; implement approved changes in small reviewed commits; update related documentation per step; and finalize migration/planning Markdown files after implementation. Do not skip decision gates or claim local Graphify execution from a GitHub-only session.

## Tooling and commands

Use `uv` and the committed lockfile. Configured tools include Ruff, Pyright, Pylint, Bandit, Vulture, pytest, pytest-cov, pytest-asyncio, and pre-commit. The project is Python-only; Python dependencies and tooling are managed with `uv`.

Do not add Graphify to the Python check pipeline: .pj/workflow.toml remains Python-only. Graphify is available through its separate optional pj graph command group.

## Project-local workflow

- `./pj` is a Python standard-library helper; it does not need a compiler or third-party Python package.
- The Python workflow prerequisites are Python 3.14+ and `uv`. Graphify is an optional separately installed CLI.
- `./pj doctor` checks the Python version, `uv` availability, and workflow configuration validity; it returns non-zero when a required prerequisite or configuration is missing/invalid.
- `.pj/workflow.toml` defines Ruff lint, Ruff format check, Pyright, and pytest, all executed through `uv run`.
- Do not add Rust/Cargo or Graphify to the Python check pipeline. The optional Graphify CLI is managed separately through pj graph commands.

## Safety

No automatic staging, committing, pushing, merging, deployment, publishing, or migrations. Ask before application-code changes when the task is exploratory or feature-oriented. For approved implementation, work in small reviewable phases and keep docs/checklist/handover aligned. Do not run tests before the current refactor is complete unless the developer changes that instruction.

## Export schema unknown-field handling — approved (Option A)

Consumers of `export.json`, `export-report.json`, and `media-manifest.json` ignore unrecognized fields instead of rejecting a document solely for containing them. This keeps consumers forward-compatible with optional fields added in compatible revisions. It does not relax validation of required fields, malformed values, or other schema constraints. Approved target behavior, not implemented; documentation-only.

## Export schema required-field handling — approved (Option A)

Consumers reject `export.json`, `export-report.json`, or `media-manifest.json` when a field required by that document's schema is missing; they do not silently substitute defaults. Optional fields may be absent according to their documented semantics. Exact required/optional field sets remain open for detailed schema design. Approved target behavior, not implemented; documentation-only.

## Export schema null-value handling — approved (Option A)

For `export.json`, `export-report.json`, and `media-manifest.json`, `null` is valid only for fields explicitly declared nullable by that document's schema; otherwise the document is invalid. An omitted optional field is distinct from an explicit `null`. Exact nullable field sets remain open for detailed schema design. Approved target behavior, not implemented; documentation-only.

## Unsupported export schema versions — approved (Option A)

Consumers reject any of `export.json`, `export-report.json`, or `media-manifest.json` whose `schema_version` they do not support, and report the unsupported version; they do not attempt best-effort parsing. Unknown fields are ignored only within a supported schema version. Approved target behavior, not implemented; documentation-only.

## Export JSON root shape — approved (Option A)

`export.json`, `export-report.json`, and `media-manifest.json` each require a top-level JSON object containing that document's `schema_version` and document-specific fields. Top-level arrays and scalar JSON values (including null) are invalid. Approved target behavior, not implemented; documentation-only.


### Duplicate JSON object keys — approved (Option A)

- Reject a JSON document if any object contains duplicate member names, at any nesting level.
- Treat duplicate keys as invalid input rather than relying on parser-specific behavior such as keeping the first or last value.
- Apply this rule independently to `export.json`, `export-report.json`, and `media-manifest.json`.
- This prevents ambiguous interpretation and inconsistent validation across parsers. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


### `schema_version` value validation — approved (Option A)

- In `export.json`, `export-report.json`, and `media-manifest.json`, `schema_version` must be a JSON integer greater than zero.
- Reject zero, negative numbers, decimal/fractional values (including `1.0`), strings (including `"1"`), booleans, null, and any other non-integer or non-positive value.
- Do not coerce or normalize values into integers; validate the JSON value's actual type and value.
- Apply this rule independently to each document. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


### Missing `schema_version` — approved (Option A)

- `export.json`, `export-report.json`, and `media-manifest.json` are invalid if the top-level `schema_version` field is missing.
- Consumers must not infer a default version, including version `1`.
- Apply this requirement independently to each document. Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


### JSON object member-name case sensitivity — approved (Option A)

- JSON object member names are case-sensitive; consumers match documented field names exactly (`schema_version` and `Schema_Version` are different names).
- A differently cased name does not satisfy a required field; the exact required spelling must be present.
- Apply at every object level in `export.json`, `export-report.json`, and `media-manifest.json`.
- Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


### JSON object member-name Unicode handling — approved (Option A)

- Compare JSON object member names by their exact Unicode code-point sequences; do not normalize before comparison.
- Visually identical names with different code-point sequences are distinct.
- Apply at every object level in `export.json`, `export-report.json`, and `media-manifest.json`, in addition to case-sensitive matching.
- Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.


### JSON object member-name whitespace handling — approved default (Option A)

- Compare JSON object member names exactly; do not trim leading or trailing whitespace.
- Whitespace is part of the name: `" schema_version"` and `"schema_version "` do not match `schema_version` and cannot satisfy that required field.
- Apply at every object level in all three export JSON documents, alongside case-sensitive and exact Unicode code-point matching.
- Approved target behavior, not implemented; documentation-only; no application code, schema, migrations, or tests changed/run.



## Export schema conventions — working defaults

Use one opaque UUID `export_id` and common RFC 3339 UTC `created_at` across all included export JSON documents; `export.json` additionally records the request acceptance `cutoff_at`. Timestamps are UTC strings ending in `Z`, preserving sub-second precision where present. Relationships use export-local `src-`, `msg-`, and `media-` references, never internal/Telegram IDs; references are valid only within one export. Arrays and ZIP entries use deterministic ordering except where user-configured order is meaningful. Exact fields and shapes remain open. Recommended working defaults; not implemented.



## Export JSON document shapes — working defaults

In schema v1, require common metadata and all primary sections: `preferences` object; `schedules`, `subscriptions`, `delivery_history`, `messages`, and `sources` arrays. Empty sections are `{}`/`[]`, never omitted or null. Report structure: result, included-record counts, structured omissions, warnings. Media manifest lists only included files and records media/message references, safe ZIP-relative path, type/content type, byte size, and SHA-256. Validate shared export metadata, counts, ZIP paths, and references. Exact domain fields, author/privacy rules, and model alignment remain open; not implemented.



## Export report and media validation — working defaults

Report result is `complete` or `complete_with_omissions`; omissions carry stable reason codes, category, count, and explanation. Counts and byte sizes are non-negative integers. Media entries use SHA-256, exact uncompressed size, known MIME type when available, and predefined media categories. Archive paths are safe relative paths; filenames are sanitized and collisions receive deterministic suffixes. Manifest entries and ZIP binaries must match one-to-one. Source authorization revocation invalidates the export rather than being reported as an ordinary omission. Not implemented.



## Exported message privacy — approved

Export authorized retained message content/captions/timestamps, but no third-party profile data or identity fields (sender names/usernames/Telegram IDs, photos, phone numbers, participant/contact lists, forwarded/quoted author identities). No Telegram transport IDs. Message content remains exportable when authorized. Approved; not implemented.

## Export schema v1 message/source/media defaults — working recommendations

Repository inspection on `refactor/chatbrief-package-layout` found the current `Message` fields are text, sender, timestamp, link, channel_name, has_media, and media_type; the Telegram adapter derives sender names, Telegram links, and localized media labels. `ChannelConfig` has source id/name plus lookback/prompt/filter/group settings. `Settings` mixes user-facing preferences with operational values and target_user_id. Current storage is optional and is not the export-job store.

Working recommendations:
- Export authorized text/captions and source timestamps; exclude sender/author profile identity, Telegram IDs and links, and synthetic author references.
- Keep v1 message content plain text; do not invent entities, reply/forward/reaction/edit/deletion/service-event fields absent from the retained model.
- Use stable media categories, not localized labels. Media-only messages should not gain invented user-authored placeholder text; conversion of legacy placeholders remains a migration-design issue.
- Source records use a safe configured display label and platform only; no Telegram IDs, usernames, invite/deep links, internal keys, or sessions.
- Export an allowlist of user-owned preferences, not raw config. Exclude target_user_id, credentials, sessions, storage paths, internal class paths, and operational settings.
- Recommended media privacy: generated deterministic ZIP filenames based on export-local media refs; omit original filenames from the manifest.
- Recommended v1 purpose: archival/inspection snapshot, not automatic restore/import or account migration. Future import needs separate design.
- Exact v1 field mapping and legacy-data conversion remain open for Phase 1 migration proposal. No code/tests/migrations changed or run.

## Export report and media-only message semantics — working defaults

Repository inspection confirmed the current Telethon adapter synthesizes localized placeholder text (for example `[Photo]`) for media-only messages. This is display text, not author content. Recommended v1:
- Keep message `text` as retained plain text/caption; allow empty string for media-only messages. Never replace with a synthetic placeholder.
- Remove a legacy placeholder only when its synthetic origin is reliably known; if provenance is ambiguous, preserve stored text rather than risk deleting genuine authored text.
- A retained/authorized media-only message remains in the primary export even if its binary is unavailable. Manifest items represent only binaries actually included in the companion ZIP.
- Source event timestamp may be absent only if genuinely unavailable; never substitute export creation or collection time.
- Binary media categories: image, video, document, audio. Poll/location/other interactive or service payloads are not media binaries in v1; report unsupported eligible payloads as media omissions when applicable.
- Do not export a `has_media` flag that implies a binary was included. Message-to-media refs point only to actual companion ZIP items; manifest is authoritative.

Report recommendations:
- Omission reason codes: `expired`, `unavailable`, `unsupported`, `size_limit`, `missing_content`, `not_exportable`. Remove `unsafe_filename`: original filenames are never used. Unsafe filesystem inputs are never read and are reported as `not_exportable` if otherwise eligible.
- Omission categories: preferences, schedules, subscriptions, delivery_history, messages, media. Aggregate by reason/category with positive count and safe explanatory message; no private IDs, paths, filenames, or omitted content.
- `complete_with_omissions` only when eligible requested content is actually absent. Naturally empty categories are not omissions; invalidated/failed jobs do not produce a successful report.
- Fixed non-negative included counts: preferences, schedules, subscriptions, delivery_history, messages, sources, media_files, media_bytes; include omitted_media_items only when known. Counts describe actual archive contents.
- Warnings are structured `{code,message}`; initial codes: `legacy_media_placeholder_removed`, `media_metadata_incomplete`, `timestamp_unavailable`. Warnings alone do not change result; no source text, identifiers, filenames, paths, traces, or secrets in warning messages.
- These are recommended schema semantics, not implemented. Legacy placeholder provenance and exact field mapping remain Phase 1 migration-design items. No code/tests/migrations changed or run.

## Export preference/source field allowlist — working defaults

- Export only requesting-user-owned, user-meaningful values; never copy current single-user/global config wholesale.
- Potential typed preferences include lookback, output language, digest mode, emoji/statistics choices, topic deduplication, and user-owned digest-group definitions, only when actually stored per user in the future domain model.
- Subscription records may carry the requester's own source-specific lookback, digest-group assignment, and authored prompt override where user-owned. Preserve that prompt text as data.
- Do not export prompt-template paths, composer/filter Python class paths, arbitrary filter dictionaries, executable/plugin code, credentials, provider API keys, service endpoints, deployment limits, timeouts, global model/runtime config, or storage/database config.
- Export filters only via stable versioned data-only allowlists. Unsupported filter configuration is omitted with `not_exportable`, never serialized as arbitrary Python objects/import paths.
- Provider/model choice is included only if Phase 1 establishes it as an explicit user-owned preference rather than operator configuration.
- Source records contain platform enum and safe display label only; no source usernames/IDs/invite links/private URLs/transport IDs. Missing required source linkage is invalid snapshot data, not a dangling/synthetic source ref.
- Exact field keys remain dependent on the future user-scoped model and Phase 1 migration proposal. No code/tests/migrations changed or run.

## Phase 1 export persistence migration proposal — approved for implementation

Repository inspection: existing message storage is optional, uses inline `CREATE TABLE IF NOT EXISTS`, and has no versioned migration runner or application-wide user table. It cannot safely supply export ownership or source identity.

Proposed additive design:
- Introduce required application-state storage independent of optional `StorageBackend`, SQLite first, provisionally `data/application.db`; leave optional `data/messages.db` unchanged.
- Add a minimal versioned migration runner using existing `aiosqlite`/`asyncpg`; `schema_migrations(version, applied_at, checksum)`; transactional application; reject checksum drift; enable SQLite foreign keys on every connection. No new migration dependency.
- `export_jobs`: internal UUID PK, unique opaque export_id, owner_telegram_user_id, constrained lifecycle state, media outcome, cutoff_at (acceptance boundary), created_at/updated_at, primary_delivered_at/expires_at, lease owner/expiry/generation, next_run_at, opaque staging_key, optional validated report/manifest JSON, stable last_error_code. No ZIP bytes or absolute paths.
- `export_delivery_attempts`: job FK, primary/media kind, per-kind attempt number unique per job, started/succeeded/failed/delivery_unknown outcome, timestamps/retry time, restricted Telegram chat/message/file IDs, sanitized error code. Append-only attempts; never overwrite ambiguity.
- `export_cleanup_tasks`: nullable job FK ON DELETE SET NULL, telegram-message-delete/staging-delete type, pending/succeeded/abandoned state, minimal target IDs or opaque staging key, bounded retry/deadline/error metadata. Cleanup survives account/job deletion only while actionable.
- Partial unique index enforces one blocking job per user for queued/collecting/packaging/ready; indexes support queue claims, owner status, leases, expiry, attempts, and cleanup.
- Short atomic transactions; worker writes fenced by lease generation; no DB transaction across archive or Telegram calls.
- Additive migration only. Do not alter old messages, delivery JSON, config, or Telethon session. Do not backfill old message rows: they lack stored owner, stable source ID, and message ID. Any later backfill requires a separate proof-based mapping proposal.
- First migration creates only export tables and migration metadata. PostgreSQL migrations, shared users/sources/subscriptions/messages/coverage/session tables, workers/commands/ZIP/delivery implementation, and legacy backfill remain out of scope.
- Implementation status: approved direction; implement additively in tested slices. The proposal is not yet implemented, and legacy data must remain untouched unless a separately approved proof-based mapping is established.
