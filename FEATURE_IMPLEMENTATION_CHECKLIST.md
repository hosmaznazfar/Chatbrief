# Chatbrief implementation checklist

Use this checklist for non-trivial work. Check an item only when its completion is supported by inspected source, a diff, or actual command output.

## Before implementation

- [ ] Verify repository, intended branch, latest GitHub commit, and available local worktree state.
- [ ] Read `AI_README.md`, `CHATGPT_CONTEXT.md`, `docs/AI_WORKFLOW.md`, `docs/handover/current.md`, `docs/GRAPHIFY.md`, README, relevant ADRs/plans, source, and tests.
- [ ] Check whether the committed Graphify report/JSON exist on the selected branch; use them to locate relevant relationships and verify findings against source/tests.
- [ ] Identify existing conventions and architecture boundaries before proposing new abstractions.
- [ ] Define scope, acceptance criteria, risks, and phases.
- [ ] Update the relevant plan/docs and obtain approval before application-code implementation.

## Implementation

- [ ] Implement only the approved scope, one phase at a time.
- [ ] Keep platform-specific behavior in adapters and domain/digest logic platform-neutral.
- [ ] Preserve existing behavior and configuration compatibility unless a change is explicitly approved.
- [ ] Add or migrate tests for changed behavior; do not delete coverage merely to make imports pass.
- [ ] Update documentation and this checklist as implementation progresses.
- [ ] If source relationships changed, run `./pj graph sync` locally and review the generated `graphify-out/` diff before committing it with the matching source revision.
- [ ] Confirm Graphify Git hooks are installed when automatic post-commit/branch-switch refresh is desired (`./pj graph hooks status`).
- [ ] Keep secrets, local sessions, generated caches, and machine-specific files out of Git; Graphify's documented project graph artifacts are intentionally tracked.

## Validation

- [ ] Confirm the developer has declared the refactor/implementation ready for tests.
- [ ] Run the relevant Ruff checks and formatter check.
- [ ] Run Pyright and applicable Pylint/Bandit/Vulture checks.
- [ ] Run pytest and record the exact result and coverage.
- [ ] Build the Astro website if website files or shared CI are affected.
- [ ] Review the complete diff, CI results, generated Graphify artifacts, and whitespace.
- [ ] Distinguish passed, failed, skipped, and not-run checks.

## Handover

- [ ] Update `docs/handover/current.md` with verified branch/commit and completed work.
- [ ] Record Graphify artifact availability and freshness only when verified.
- [ ] Record actual validation output, deferred checks, blockers, and exact next steps.
- [ ] Ask before staging, committing, pushing, merging, deploying, publishing, or migrating.
