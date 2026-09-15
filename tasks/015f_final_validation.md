# Task 015f - Final Validation Checkpoint

## Goal

Validate the completed Task 015 documentation changes and leave the repository in a clean, handoff-ready state.

This task is a checkpoint. Do not add new features.

## Required context

Read only:

- `docs/CURRENT_STATE.md`;
- `README.md` final launch/demo section;
- `docs/DEFENSE_DEMO_SCRIPT.md`;
- `docs/PROJECT.md` relevant project/limitations sections.

Open additional files only when a failing check points to them.

## Allowed changes

- files required to fix a regression discovered by validation;
- `docs/CURRENT_STATE.md`.

Any fix outside documentation must be minimal and directly necessary for restoring an existing check. Do not implement new functionality.

## Steps

1. Confirm 015a–015e handoffs are reflected in the current documentation.
2. Run the full project checkpoint:

```powershell
scripts/check.ps1
```

3. If it passes, do not perform additional refactoring.
4. If it fails, identify the smallest regression attributable to Task 015 work and fix only that regression.
5. Perform one targeted search for stale active Demo-flow recommendations.
6. Update `docs/CURRENT_STATE.md` with final Task 015 status and the next development task.

## Checks

Required:

```powershell
scripts/check.ps1
```

Also perform targeted repository search for obsolete active Demo instructions.

## Forbidden

- No new product features.
- No broad cleanup/refactoring.
- No dependency upgrades unless strictly required to restore a previously working check.
- Do not start the next development task in this context.

## Done criteria

- `scripts/check.ps1` passes, or any environment-only blocker is documented precisely without pretending success.
- Final docs consistently describe the normal product flow.
- No obsolete Demo path is recommended as the current preferred workflow.
- `docs/CURRENT_STATE.md` marks Task 015 complete and names exactly one next task.
- Agent stops after this checkpoint.

## Handoff

This closes parent Task 015. Start any subsequent development work in a fresh context window.