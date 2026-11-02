# Chatbrief implementation checklist

Use this checklist for non-trivial work. Check an item only when its completion is supported by inspected source, a diff, or actual command output.

## Inspect and decide before implementation

- [ ] Verify repository, intended branch, latest GitHub commit, and available local worktree state.
- [ ] Read `AI_README.md`, `CHATGPT_CONTEXT.md`, `docs/AI_WORKFLOW.md`, `docs/handover/current.md`, `docs/GRAPHIFY.md`, README, relevant ADRs/plans, source, and tests.
- [ ] Inspect the initial source/graph context, then ask the developer to run `./pj graph refresh` and `./pj graph diff` for this task; review and commit any changed portable artifacts, then inspect the refreshed graph on GitHub.
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
- [ ] Review the complete diff, CI results, generated Graphify artifacts, and whitespace.
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
- [ ] Run focused export/storage/lifecycle pytest tests locally.
- [ ] Run Ruff lint/format and Pyright locally.
- [ ] Review complete implementation diff; refresh/review Graphify after validation.
- [ ] Add delivery-attempt and cleanup-task repository operations in the next slice.
