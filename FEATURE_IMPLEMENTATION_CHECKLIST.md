# Chatbrief implementation checklist

Use this checklist for non-trivial work. Check an item only when its completion is supported by inspected source, a diff, or actual command output.

## Inspect and decide before implementation

- [ ] Verify repository, intended branch, latest GitHub commit, and available local worktree state.
- [ ] Read `AI_README.md`, `CHATGPT_CONTEXT.md`, `docs/AI_WORKFLOW.md`, `docs/handover/current.md`, `docs/GRAPHIFY.md`, README, relevant ADRs/plans, source, and tests.
- [ ] Use the existing Graphify graph when it materially helps navigate an unfamiliar area; request a refresh only if the graph is stale and updating it would help the implementation. Graph artifacts are not a product deliverable or a routine completion gate.
- [ ] Trace graph findings against source, tests, configuration, and ADRs; identify existing conventions and architecture boundaries.
- [ ] List material design/implementation decisions. Research current external options online where relevant, cite evidence, compare trade-offs, recommend an option, and ask the developer to choose.
- [ ] Agree on scope, acceptance criteria, non-goals, risks, and implementation steps before changing application code.

## Implementation

- [ ] Implement only the approved scope, one small step at a time.
- [ ] After each step, review the complete diff, update directly related docs/tests/ADRs, and commit that step before proceeding (when direct Git commits are authorized).
- [ ] Keep platform-specific behavior in adapters and domain/digest logic platform-neutral.
- [ ] Preserve existing behavior and configuration compatibility unless a change is explicitly approved.
- [ ] Add or migrate tests for changed behavior; do not delete coverage merely to make imports pass.
- [ ] Update documentation and this checklist as implementation progresses.
- [ ] If source relationships changed, ask the developer to run `./pj graph refresh` and `./pj graph diff`; review and commit portable graph artifacts with the source revision they describe before treating the shared graph as current.
- [ ] Confirm Graphify Git hooks are installed when automatic post-commit/branch-switch refresh is desired (`./pj graph hooks status`).
- [ ] Keep secrets, local sessions, generated caches, and machine-specific files out of Git; Graphify's documented project graph artifacts are intentionally tracked.

## Validation

- [ ] Confirm the developer has declared the refactor/implementation ready for tests.
- [ ] Run the relevant Ruff checks and formatter check.
- [ ] Run Pyright and applicable Pylint/Bandit/Vulture checks.
- [ ] Run pytest and record the exact result and coverage.
- [ ] Review the complete source/test/documentation diff, CI results, and whitespace; inspect graph artifacts only when they are part of the requested work.
- [ ] Distinguish passed, failed, skipped, and not-run checks.

## Completion and handover

- [ ] After all implementation steps are complete, update the relevant migration and planning Markdown files to describe actual completed work, deferred items, and remaining migration tasks.
- [ ] Update `docs/handover/current.md` with verified branch/commit and completed work.
- [ ] Record Graphify artifact availability and freshness only when verified.
- [ ] Record actual validation output, deferred checks, blockers, and exact next steps.
- [ ] Commit each reviewed implementation step when the task authorizes direct Git commits; ask before pushing, merging, deploying, publishing, or running migrations.


## Application-state database foundation — steps 1–2

- [x] Add independent application database configuration with a safe default path.
- [x] Add versioned transactional SQLite migration runner and checksum validation.
- [x] Add the approved export persistence schema and constraints as migration 1.
- [x] Add focused migration and configuration tests.
- [x] Run Step 1 focused tests, full suite, Ruff lint/format, and Pyright; results were confirmed by the developer.
- [x] Initialize the required application database in root `main.py` before constructing platform/application services.
- [x] Retain the initialized database object on `ChatbriefApp` for future repository/service injection.
- [x] Add lifecycle tests for startup ordering and fail-closed behavior when database initialization fails.
- [x] Preserve the independent optional legacy message-history store; no legacy schema/data changes.
- [x] Run the lifecycle-focused tests; the developer confirmed the focused run passed after the pytest import-path correction.
- [x] Run the full suite after lifecycle integration; the developer confirmed it passed (exact follow-up counts were not provided).
- [x] Run Graphify sync, review/update the portable graph, and push commit `ab53ac1` (developer-confirmed).


## Export persistence — Step 3a: job repository and atomic transitions

- [x] Add typed export job and lifecycle-state models.
- [x] Add job creation with opaque IDs and database-enforced per-user blocking-job uniqueness.
- [x] Add owner-scoped job reads and active-job lookup.
- [x] Add short transactional compare-and-set state transitions with an explicit lifecycle graph.
- [x] Reject premature `ready` transitions unless a successful primary delivery attempt is already persisted.
- [x] Add focused tests for ownership, uniqueness, state transitions, terminal release, and metadata validation.
- [x] Run focused export/storage/config/lifecycle pytest tests locally — developer-confirmed **109 passed**.
- [x] Run Ruff lint and Pyright locally — developer-confirmed; Pyright **0 errors, 0 warnings, 0 informations**.
- [x] Run Ruff format locally — developer formatted the application-storage and export test files; Ruff format check then reported **8 files already formatted**.
- [x] Run full suite after Step 3a — developer-confirmed **612 passed, 7 skipped**, coverage **94.42%**.
- [x] Refresh and commit the graph after Step 3a — developer reported the updated graph was committed; exact commit not yet recorded here.

## Export persistence — Step 3c: worker claims and lease fencing

- [x] Add atomic selection and claiming of the next due queued/collecting/packaging job.
- [x] Assign worker owner, bounded lease expiry, and incremented generation on each claim/reclaim.
- [x] Add live-owner/generation-checked lease renewal and release with optional retry scheduling.
- [x] Add lease-generation-fenced worker state transitions; clear leases when work reaches ready or a terminal state.
- [x] Add focused tests for competing claims, expiry/reclaim, stale-worker rejection, renewal/release, scheduling, and invalid parameters.
- [x] Run focused tests, Ruff lint/format, Pyright, and full pytest locally — developer-confirmed **627 passed, 7 skipped**, coverage **93.38%**; Ruff lint/format and Pyright passed.

## Export persistence — Step 3b: delivery attempts and cleanup tasks

- [x] Add typed delivery document-kind, attempt-outcome, cleanup-task-type/state models.
- [x] Add owner-scoped delivery-attempt creation with sequential per-document attempt numbers and unresolved-attempt protection.
- [x] Allow retry only after a known failed attempt; prevent automatic retry after ambiguous delivery.
- [x] Require confirmed primary delivery before media delivery and before the job can transition to `ready`.
- [x] Add one-time finalization of started attempts with restricted Telegram identifiers and stable error metadata.
- [x] Persist media delivery outcomes on the export job.
- [x] Add owner-checked Telegram-message and staging-object cleanup task creation.
- [x] Add due-task listing, task lookup, retry/result recording, and parent-job deletion survival.
- [x] Add focused tests for delivery attempts, ownership, retries, media outcome, cleanup scheduling, and orphan cleanup.
- [x] Rerun focused Step 3b tests after fix commit `44ec74e` — developer-confirmed **119 passed**.
- [x] Rerun Ruff lint and Pyright after fix commit `44ec74e` — Ruff passed; Pyright **0 errors, 0 warnings, 0 informations**.
- [x] Rerun Ruff format check after fix commit `44ec74e` — developer-confirmed pass (**8 files already formatted**).
- [x] Rerun full pytest suite after fix commit `44ec74e` — developer-confirmed **622 passed, 7 skipped**, coverage **94.07%**.
- [x] Format Step 3a files and rerun the application-storage/export formatter check — developer-confirmed **8 files already formatted**.
- [x] Review and fix the Step 3b implementation issues; Graphify is development tooling and is not a project implementation deliverable.


## Export persistence — Step 3d: fair per-user claim scheduling

- [x] Add a migration-backed persisted last-claimed marker to export jobs.
- [x] Prefer users never previously served, then rotate by least-recently-claimed order.
- [x] Keep candidate selection, lease assignment, and fairness-marker update in one short transaction.
- [x] Add focused multi-user rotation and existing-database migration-upgrade tests.
- [x] Run focused tests, Ruff lint/format, Pyright, and full pytest locally — developer-confirmed **33 focused passed**, **629 passed, 7 skipped** overall, coverage **93.39%**.


## Export persistence — Step 3e: delivery-attempt lease fencing

- [x] Require a live worker lease and generation to start a delivery attempt.
- [x] Persist the creating worker ID and lease generation on each new attempt.
- [x] Require both the current job lease and the attempt's original worker/generation to finish an attempt.
- [x] Add migration 3 without inferring ownership for pre-existing attempts.
- [x] Test stale-worker rejection after lease release and reclaim.
- [x] Run focused delivery/storage tests, Ruff lint/format, Pyright, and full pytest locally — developer-confirmed **19 passed**, **631 passed, 7 skipped** overall, coverage **93.40%**; Ruff lint/format passed and Pyright reported **0 errors, 0 warnings, 0 informations**.


## Export worker orchestration — Step 4a: worker service foundation

- [x] Add state-based async phase-handler dispatch around durable job claims.
- [x] Bound worker concurrency to a validated maximum of 32 active jobs.
- [x] Renew active leases while handlers run; cancel a handler when its lease is lost.
- [x] Release leases after phase completion and schedule backoff for no-op, missing, or failed handlers.
- [x] Stop new claims on shutdown, wait for a configurable grace period, then cancel remaining handlers.
- [x] Add focused tests for dispatch, bounded concurrency, lease renewal/loss, cooperative shutdown, and retry scheduling.
- [x] Run Ruff lint, Ruff format, Pyright, and the full pytest suite locally — developer-confirmed on 2026-11-02: Ruff passed; **102 files already formatted**; Pyright **0 errors, 0 warnings, 0 informations**; pytest collected **652 tests**, with **7 skipped** and **93.19% coverage**. The pasted output omitted pytest's final passed count.
- [x] Keep startup wiring deferred until at least one real phase handler is implemented.
- [x] Add migration 4 for identity-only users, sources, technical source access, explicit user authorizations, subscriptions, normalized deduplicated messages, and known-complete collection coverage intervals.
- [ ] Validate migration 4 upgrade/idempotency, foreign keys, uniqueness, and constraints locally; run Ruff, Pyright, and the full suite.
- [ ] Add typed repository operations for user/source/access/authorization/subscription/message/coverage records.
- [ ] Add an authorization-aware export snapshot query that enforces source access and user grants independently of subscription state.
- [ ] Implement the collecting phase handler only after the snapshot query exists; use cancellation-safe checkpoints and lease-generation-fenced transitions. Do not backfill legacy message-history rows.
