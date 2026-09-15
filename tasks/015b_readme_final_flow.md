# Task 015b - README Final Flow

## Goal

Make the README contain one concise, reliable launch and demonstration flow for the current product path.

## Required context

Read only:

- `README.md`
- `tasks/015_diploma_alignment_and_final_demo.md`

Do not preload other docs unless a command in README must be verified against a specific file.

## Allowed changes

- `README.md`
- `docs/CURRENT_STATE.md`

## Steps

1. Find the current setup/run/demo instructions in README.
2. Add or normalize one final flow in this order:
   - run checks;
   - start the FastAPI web UI;
   - enroll a user from photo;
   - enroll a user from video;
   - recognize photo/video;
   - inspect users/events.
3. Clearly distinguish the default mock provider from optional InsightFace usage.
4. Remove duplicated or conflicting launch instructions only where they directly conflict with the final flow.
5. Keep the section operational and short enough to follow during a defense demo.

## Checks

Verify only the commands you changed or added.

At minimum, confirm the README uses the existing project commands rather than inventing new scripts or endpoints.

No full test suite is required in this iteration.

## Forbidden

- No source-code changes.
- No redesign of the README outside launch/demo instructions.
- Do not claim InsightFace is required for normal tests.
- Do not describe the old detached Demo tab as the preferred path.

## Done criteria

- README has one obvious final launch/demo path.
- Photo and video enrollment are both represented.
- Photo/video recognition and event viewing are represented.
- Mock vs InsightFace behavior is not misleading.
- `docs/CURRENT_STATE.md` ends with `Next task: 015c`.

## Handoff

Stop after the handoff. Start 015c in a fresh context.