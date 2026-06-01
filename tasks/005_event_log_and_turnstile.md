# Task 005 - Event Log and Mock Turnstile

## Goal

Implement local event logging and a mock turnstile adapter.

This task completes the local MVP loop:

```text
recognition -> access decision -> turnstile command -> event log
```

## Required

Create:

- `src/devices/turnstile.py`
- `src/events/event_log.py`

`MockTurnstile` must:

- open only when `AccessDecision.decision == "allow"`;
- stay closed for `deny`, `retry`, and `manual_check`;
- return `TurnstileCommand`;
- not know anything about ML internals.

`EventLog` must:

- write every access attempt;
- support JSONL format for local MVP;
- include:
  - timestamp;
  - user_id;
  - decision;
  - reason;
  - similarity;
  - quality_score;
  - turnstile_id;
  - command.

Default log location should be local and gitignored, for example:

```text
reports/events.jsonl
```

## Harness Impact

Update harness so every scenario produces:

- recognition result;
- access decision;
- turnstile command;
- event log entry.

Harness expected checks should include turnstile command when practical.

## Forbidden

- Do not connect real hardware.
- Do not use external databases.
- Do not store real personal data.
- Do not log image bytes or real biometric templates.
- Do not make event logging required for unit tests unless using a temp path.

## Tests

Add tests for:

- turnstile opens only on allow;
- deny does not open turnstile;
- retry does not open turnstile;
- manual_check does not open turnstile;
- event is written for every decision;
- JSONL line can be parsed back.

Recommended files:

- `tests/test_turnstile.py`
- `tests/test_event_log.py`

## Documentation

Update:

- `docs/CURRENT_STATE.md`;
- `README.md` if the local event log path matters for users;
- `.gitignore` if reports/logs are not ignored yet.

## Done Criteria

- `python -m pytest -q` passes.
- `python harness/run_all.py` passes.
- Successful and failed attempts are logged in JSONL during harness or explicit
  integration tests.
- Mock turnstile never opens unless decision is `allow`.
- `docs/CURRENT_STATE.md` is updated.

