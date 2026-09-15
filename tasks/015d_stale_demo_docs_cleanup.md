# Task 015d - Stale Demo Documentation Cleanup

## Goal

Remove or clearly mark stale documentation that still recommends the old detached Demo flow.

## Required context

Do not read all documentation up front.

First search the repository for these terms:

- `Demo tab`
- `demo tab`
- `/api/demo`
- `demo endpoint`
- `presentation demo`
- `detached demo`

Then open only the files that contain relevant stale instructions.

## Allowed changes

- `docs/*.md`
- `demo/*.md`
- `README.md` only if a stale Demo recommendation still remains there
- `docs/CURRENT_STATE.md`

Do not modify code in this task.

## Steps

1. Search for old Demo-flow references.
2. Classify each hit as either:
   - stale operational instruction that must be removed/updated; or
   - historical information that may remain if clearly marked historical.
3. Update only the relevant paragraphs.
4. Prefer links to the normal README/defense flow instead of duplicating long instructions.
5. Stop when no stale recommendation presents the detached Demo path as the current preferred workflow.

## Checks

Repeat the same targeted search after editing.

No test suite is required.

## Forbidden

- No source-code changes.
- Do not rewrite unrelated documentation.
- Do not delete historical files solely because their name contains `demo`.
- Do not remove useful fallback information that is still accurate.

## Done criteria

- Repository search finds no active recommendation to use an obsolete detached Demo tab/API as the preferred flow.
- Historical references, if retained, are clearly labeled as historical/deprecated.
- `docs/CURRENT_STATE.md` ends with `Next task: 015e`.

## Handoff

Stop after the handoff. Run 015e in a fresh context.