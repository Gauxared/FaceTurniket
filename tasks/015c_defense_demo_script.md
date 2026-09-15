# Task 015c - Defense Demo Script

## Goal

Make `docs/DEFENSE_DEMO_SCRIPT.md` a short defense-ready script that demonstrates the normal product flow instead of a special demo path.

## Required context

Read only:

- `docs/DEFENSE_DEMO_SCRIPT.md`
- the final launch/demo section of `README.md`

Open a source file only if a concrete behavior in the script cannot be verified from those two files.

## Allowed changes

- `docs/DEFENSE_DEMO_SCRIPT.md`
- `docs/CURRENT_STATE.md`

## Steps

1. Keep the script focused on a live demonstration, not architecture exposition.
2. Use this order:
   - start server;
   - open web UI;
   - enroll a user from video;
   - show that templates/user were created;
   - run recognition on a known user;
   - show `allow` and mock turnstile open behavior;
   - run unknown or low-quality input;
   - show `deny`, `retry` or `manual_check` with turnstile kept closed;
   - show the event log;
   - finish with limitations and next steps.
3. Add a minimal fallback note for demo failure: use the mock provider or a prepared non-personal test fixture, but do not bypass the real decision pipeline.
4. Remove references that require a detached Demo tab or demo-only endpoint.

## Checks

No full test suite in this iteration.

Cross-check the script against the README launch flow. Do not inspect unrelated implementation files.

## Forbidden

- No code changes.
- No fake hard-coded `allow` path.
- No claim that mock output is real ML.
- No personal photos or biometric data in the repository.

## Done criteria

- Script follows the normal UI/product flow.
- Success and failure/fallback scenarios are both shown.
- Event log is part of the demonstration.
- Limitations are visible rather than hidden.
- `docs/CURRENT_STATE.md` ends with `Next task: 015d`.

## Handoff

Stop after the handoff. Run 015d in a fresh context.