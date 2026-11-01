# Personal Data Export

**Status:** Approved target behavior; implementation not started  
**Repository branch:** `refactor/chatbrief-package-layout`  
**Related plan:** `docs/plans/telegram-hybrid-ingestion.md`  
**Last updated:** 2026-11-01

This document records the approved product and security decisions for a user-requested
personal data export. It is a design specification, not evidence that export functionality
exists. Application code, database schema, migrations, and tests have not been changed
as part of this design.

## 1. Purpose and scope

A Chatbrief user can request a downloadable copy of the personal data they are currently
authorized to access.

Include:

- The requesting user's preferences and schedules.
- The user's subscriptions.
- The user's delivery history.
- All currently accessible retained messages, not only messages previously included in
  digests.
- Actual retained binary media files when the user is currently authorized to access them.

Shared-source messages and media are included only while the requesting user is authorized
to access the corresponding source. Shared storage does not itself grant access.

Exclude:

- Other users' personal information.
- Credentials, including Telethon sessions and authentication secrets.
- Internal filesystem paths and storage identifiers.
- Data or media the user is not currently authorized to access.

Exporting must not modify subscriptions, retention settings, messages, or account state.

## 2. Archive format

The export is a ZIP archive with this target layout:

```text
chatbrief-export.zip
├── README.txt
├── export.json
├── export-report.json
└── media/
    ├── images/
    ├── videos/
    ├── documents/
    └── audio/
```

- `export.json` contains the included structured personal data and authorized retained
  messages.
- `media/` contains actual retained binary media files that pass authorization,
  availability, retention, and size checks.
- `export-report.json` records the export timestamp, completeness information, and
  omitted media with reasons where known.
- `README.txt` explains the archive layout and how to interpret its contents.

The archive must not expose internal storage paths or identifiers.

## 3. Media inclusion and retention

Include actual retained binary media when the requesting user is currently authorized.

- Apply existing media-retention rules, source authorization, and per-operation media-access
  checks.
- Include only media retained and available during export generation.
- Apply configurable export-size limits.
- Do not select media the requester is not currently authorized to access. Omit expired,
  unavailable, or over-limit media and report those omissions and reasons where known.
- Do not delete or alter source media as a side effect of exporting.

The existing media retention and authorization rules remain authoritative; export does not
extend media retention.

## 4. Size-limit behavior

When the export reaches its configured size limit, prefer a valid, useful partial export
rather than rejecting the entire request.

Priority:

1. Structured personal data.
2. Currently accessible retained messages.
3. Binary media, subject to the remaining size budget.

Include media until the configured limit prevents further additions. Omit media that cannot
fit and record the omission and reason in `export-report.json`, where known.

Never silently truncate JSON or create a corrupt ZIP. The report must clearly indicate
whether the export is complete or contains omissions.

**Still open:** the exact behavior when structured data and messages alone exceed the
configured limit. The archive must remain valid and must not silently truncate structured
JSON; the detailed policy requires review against actual data volumes and storage limits.

## 5. Snapshot and authorization semantics

Each export has a fixed cutoff timestamp recorded when its request is accepted.

- The personal-data and message scope is bounded by that cutoff. Messages arriving later
  are not added to the export.
- Message inclusion is limited to messages retained and accessible under the applicable
  source authorization rules.
- Media availability is checked during generation. Media that has expired, disappeared,
  or cannot be included within the limit is omitted and reported. Content for which the
  requester lacks authorization is excluded at selection time.
- Authorization is checked when selecting content and again before every archive download.

If authorization for any source whose content has been selected for the export is revoked
at any point before download (including while generation is still running), invalidate the
**entire** export:

- Revoke the download link.
- Schedule deletion of the archive and temporary files.
- Notify the user that the export is unavailable because authorization changed.
- Require a new export under current authorization.

Do not serve a partial remainder of an archive after such a revocation.

## 6. Generation workflow

Generation is an asynchronous background job.

1. The user requests an export through the bot.
2. Chatbrief creates and queues the job, records its cutoff timestamp, and acknowledges
   the request without waiting for generation.
3. A background worker collects the eligible data and media.
4. The worker packages the ZIP and records the completeness report.
5. When ready, the bot notifies the user and sends the temporary download link.
6. The user can check the job's current status or cancel it while cancellation is allowed.

Allow at most one active export per user at a time. A second request is rejected while
that user already has an active export. Failed, cancelled, expired, and invalidated jobs
must not permanently block a new request.

The exact definition of an active job across the ready/downloadable period, queue
implementation, worker ownership/leases, progress granularity, and request rate limits
remain implementation-design details.

## 7. User-visible job states and notifications

The agreed user-visible states are:

| State | Meaning |
|---|---|
| `Queued` | Waiting for a worker |
| `Collecting` | Gathering personal data and messages |
| `Packaging` | Building the ZIP and adding media |
| `Ready` | Archive is available for download |
| `Cancelled` | User cancelled the export |
| `Failed` | Generation failed |
| `Invalidated` | Authorization changed and the archive is unavailable |
| `Expired` | The download period ended |

Notify the user when an export becomes ready, fails, or is invalidated. The user can request
the current status at any time.

Internal cleanup/reconciliation states need not be exposed as user-visible job states.

## 8. Download-link security and lifecycle

Provide a short-lived, user-bound download link.

- Generate a cryptographically random, unguessable token.
- Store only a hash of the token, never the raw token.
- Bind the token to the requesting Chatbrief user and export job.
- Require the requester to authenticate as that same user before downloading.
- Recheck authorization before every download.
- Permit repeated downloads until expiry or revocation, so interrupted downloads can be
  retried without generating another archive.
- Do not expose a permanent public storage URL.

The initial expiry is **24 hours** and must be configurable. At expiry, the link becomes
unusable and the generated archive is scheduled for deletion.

## 9. Cancellation and race handling

Cancellation can stop a queued or in-progress job. If generation has already completed,
cancellation revokes the download link and schedules archive deletion.

- Stop further collection and packaging as soon as practical.
- Schedule deletion of partial archives and temporary files.
- Repeated cancellation is idempotent.
- Repeating cancellation for an already cancelled, expired, invalidated, or failed job
  does not change its state.
- If cancellation and completion race, make the competing state transition atomic so only
  one outcome wins.
- Cancellation does not alter the user's account, subscriptions, messages, or retained
  source media.
- A copy already downloaded by the user cannot be remotely deleted.

Deletion is scheduled rather than assumed to have succeeded synchronously.

## 10. Security and privacy requirements

- Enforce source authorization at content selection and archive access.
- Enforce media authorization at every media retrieval/access operation.
- Do not rely on shared storage as evidence of user authorization.
- Do not expose another user's personal data, credentials, internal paths, or storage IDs.
- Do not expose a permanent public storage URL.
- Keep the export token secret; persist only its hash.
- Ensure the archive's contents and report use safe archive-relative filenames and do not
  allow internal paths to leak into the ZIP.
- Export must be read-only with respect to source/account data.

Archive filename collision handling, filename normalization, encryption-at-rest guarantees
for temporary/archive storage, audit-event detail, and exact token/authentication integration
must be settled during implementation design after inspecting existing storage and security
boundaries.

## 11. Approved decisions summary

The following decisions have been approved:

1. Export preferences, schedules, subscriptions, delivery history, and all currently
   accessible retained messages.
2. Exclude other users' personal information, credentials, Telethon sessions, and internal
   storage paths/identifiers.
3. Include actual retained media when currently authorized, subject to retention and size
   limits.
4. Use a ZIP archive with `README.txt`, `export.json`, `export-report.json`, and
   categorized `media/` directories.
5. On size limits, prioritize structured data and messages over media; report omitted media
   and never silently truncate JSON or produce a corrupt archive.
6. Use a fixed cutoff timestamp recorded when the request is accepted.
7. Use asynchronous background generation and allow at most one active export per user.
8. Expose the agreed job states and notify on ready, failure, and authorization invalidation.
9. Use a reusable, authenticated, user-bound link with a random token whose hash is stored.
10. Use a configurable expiry, initially 24 hours.
11. Recheck authorization at download time; revocation of any included source invalidates the
    entire archive.
12. Support cancellation during generation; cancellation is idempotent and race-safe, and
    completed archives can be revoked and scheduled for deletion.
13. Export does not change account state, subscriptions, retention, messages, or source media.

## 12. Remaining design work before implementation

The following details are deliberately not decided yet:

- Exact maximum archive size, item count, generation duration, and resource/concurrency
  limits; defaults must be selected after inspecting actual storage and deployment limits.
- Behavior when structured data and messages alone exceed the archive limit.
- Whether a ready-but-not-yet-expired export counts as an active export for the one-active-job
  rule.
- Exact bot commands and interaction UX for requesting, checking, and cancelling exports.
- Progress granularity and whether progress percentages are meaningful/reliable.
- Worker queue, job persistence, leases, crash recovery, and duplicate-worker prevention.
- Atomic state-transition model and complete transition matrix.
- Final authorization race handling between collection, packaging, finalization, and download.
- Durable archive/temporary-file cleanup retries and reconciliation after failures/restarts.
- Exact export JSON schema, schema versioning, message fields, media metadata, and report
  schema.
- Safe naming, duplicate filename handling, archive path validation, and maximum entry count.
- Storage location, access controls, encryption-at-rest, and audit logging.
- Interaction with account deletion, source removal, retention cleanup, and application
  shutdown.
- Failure classification and whether/how a failed export can be retried.

These details must be resolved against the existing application architecture, storage
interfaces, authorization model, worker/scheduler lifecycle, and tests. Do not introduce
new abstractions or schema before inspecting those existing boundaries.

## 13. Implementation boundary

This document records approved target behavior only. It does not authorize premature
application changes or imply that export is implemented.

Before implementation:

1. Verify the repository branch, latest commit, and local worktree state.
2. Read the project workflow/context documents and inspect relevant source, storage,
   authorization, media, bot-command, worker, cleanup, and test code.
3. Trace the existing architecture and Graphify relationships; ask for the required local
   graph refresh/diff where applicable.
4. Resolve the remaining design questions and agree on acceptance criteria and scope.
5. Implement in small reviewable steps, updating this document, tests, and handover as
   decisions and implementation progress warrant.

No application code, schema, migrations, or tests were changed or run for this design
record.
