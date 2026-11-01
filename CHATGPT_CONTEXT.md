# Chatbrief — persistent project context

Repository: https://github.com/hosmaznazfar/Chatbrief  
Active modernization branch: `upgrade/full-project-modernization`  
Primary package: `src/chatbrief/`  
Python: `>=3.14`; package/dependency manager: `uv`

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
- Primary `export.json` has a top-level integer `schema_version` starting at `1`, independent of the Chatbrief app version; increment for incompatible export-format changes. Exact fields and compatibility rules remain open in schema design.
- `export-report.json` also has its own top-level integer `schema_version` starting at `1`, independent of both `export.json` and the Chatbrief app version; increment it for incompatible report-format changes. The two documents can evolve independently.
- Optional `media-manifest.json` also has its own top-level integer `schema_version` starting at `1`, independent of both primary-archive documents and the Chatbrief app version; increment it for incompatible manifest-format changes. All three export documents can evolve independently.
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
- Media export ZIP entries use predefined category directories and sanitized basenames only (discard source directory components); resolve collisions deterministically without overwriting. Keep original source filenames in the manifest, never as archive paths, and reject paths still invalid after normalization. Exact sanitization/suffix rules, path validation, and entry-count limits remain open for implementation design.
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

The package/platform implementation migration is the starting point for the Python-only modernization on `upgrade/full-project-modernization`. The full test suite and quality checks have deliberately not been run.

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
