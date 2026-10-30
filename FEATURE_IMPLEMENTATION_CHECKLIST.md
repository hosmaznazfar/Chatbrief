# Chatbrief implementation checklist

Use this checklist for non-trivial work. Check an item only when its completion is supported by inspected source, a diff, or actual command output.

## Before implementation

- [ ] Verify repository, intended branch, latest GitHub commit, and available local worktree state.
- [ ] Read `AI_README.md`, `CHATGPT_CONTEXT.md`, `docs/handover/current.md`, README, relevant ADRs/plans, source, and tests.
- [ ] Identify existing conventions and architecture boundaries before proposing new abstractions.
- [ ] Define scope, acceptance criteria, risks, and phases.
- [ ] Update the relevant plan/docs and obtain approval before application-code implementation.

## Implementation

- [ ] Implement only the approved scope, one phase at a time.
- [ ] Keep platform-specific behavior in adapters and domain/digest logic platform-neutral.
- [ ] Preserve existing behavior and configuration compatibility unless a change is explicitly approved.
- [ ] Add or migrate tests for changed behavior; do not delete coverage merely to make imports pass.
- [ ] Update documentation and this checklist as implementation progresses.
- [ ] Keep secrets, local sessions, generated caches, and machine-specific files out of Git.

## Validation

- [ ] Confirm the developer has declared the refactor/implementation ready for tests.
- [ ] Run the relevant Ruff checks and formatter check.
- [ ] Run Pyright and applicable Pylint/Bandit/Vulture checks.
- [ ] Run pytest and record the exact result and coverage.
- [ ] Build the Astro website if website files or shared CI are affected.
- [ ] Review the complete diff, CI results, generated artifacts, and whitespace.
- [ ] Distinguish passed, failed, skipped, and not-run checks.

## Handover

- [ ] Update `docs/handover/current.md` with verified branch/commit and completed work.
- [ ] Record actual validation output, deferred checks, blockers, and exact next steps.
- [ ] Ask before staging, committing, pushing, merging, deploying, publishing, or migrating.
