# Task 001 - Project Skeleton

## Goal

Create the initial local Python project structure for solo-agent development.

This task prepares the repository for later code work. It must not implement
recognition, access decisions, API, database, or real ML.

## Context

The project is a local prototype for identifying or verifying an
employee/student by face photo before deciding whether a turnstile should open.

Development is intentionally incremental:

1. project skeleton;
2. contracts and mock recognition;
3. access decision;
4. harness;
5. event log and mock turnstile;
6. quality/capture improvements;
7. optional real face provider.

## Required

Create directories:

- `src/`
- `tests/`
- `harness/`
- `harness/cases/`
- `harness/fixtures/`
- `scripts/`
- `docs/`
- `tasks/`

Because empty directories are not tracked by git, add `.gitkeep` files only
where needed.

Create files:

- `README.md`
- `scripts/check.ps1`
- `.gitignore`

`README.md` must include:

- short project description;
- project goal;
- local setup instructions;
- how to run tests;
- how to run harness;
- link to `AGENTS.md`;
- link to `docs/PROJECT.md`;
- link to `docs/CURRENT_STATE.md`.

`scripts/check.ps1` must:

- run `python -m pytest -q` when tests exist;
- run `python harness/run_all.py` when harness exists;
- print a clear message if tests or harness are not implemented yet;
- exit with non-zero code when an implemented check fails.

`.gitignore` must ignore:

- Python cache folders;
- virtual environments;
- pytest cache;
- local reports/logs;
- local environment files;
- real user images or biometric data folders if they appear later.

## Forbidden

- Do not add real ML dependencies.
- Do not implement face recognition.
- Do not implement access decision logic.
- Do not implement API.
- Do not add database logic.
- Do not create extra architecture documents beyond the current docs set.

## Tests

No application tests are required yet.

If adding a placeholder test, it must not pretend the system is implemented.

## Documentation

Update `docs/CURRENT_STATE.md`:

- mark skeleton as implemented;
- set the next task to `tasks/002_contracts_and_mock_pipeline.md`;
- record which checks can currently run.

## Done Criteria

- Required directories exist.
- `README.md` exists and has the required sections.
- `scripts/check.ps1` exists and is safe to run.
- `.gitignore` exists.
- `docs/CURRENT_STATE.md` is updated.
- No real ML libraries are installed or imported.

