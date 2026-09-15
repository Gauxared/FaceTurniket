# Task 015a - Project Narrative Alignment

## Goal

Bring the core project description in `docs/PROJECT.md` in line with the final diploma narrative without changing code or unrelated documentation.

## Required context

Read only:

- `docs/PROJECT.md`
- `tasks/015_diploma_alignment_and_final_demo.md`

`AGENTS.md` and `docs/CURRENT_STATE.md` are already part of the mandatory minimal startup context.

## Allowed changes

- `docs/PROJECT.md`
- `docs/CURRENT_STATE.md`

Do not edit any other file in this iteration.

## Steps

1. Check how `docs/PROJECT.md` currently describes the problem and target users.
2. Make the university access-control context explicit: students, employees, guards/admins and visitors where relevant.
3. Describe biometric identification as the main prototype flow and physical passes/cards as the workflow being improved, without claiming an existing production deployment.
4. Make fallback handling explicit: low-confidence, low-quality or exceptional cases go to retry/manual check instead of forced access.
5. State the prototype constraints relevant to the narrative: consent/privacy requirements, audit/event logging and mock turnstile.
6. Keep the document concise; do not duplicate implementation details already documented elsewhere.

## Checks

No code tests are required.

Before finishing, re-read only the changed sections and confirm they do not claim:

- production readiness;
- perfect recognition;
- real physical turnstile integration;
- real liveness when only mock/limited liveness is available.

## Forbidden

- No code changes.
- No README changes.
- No defense-script changes.
- No broad rewrite of `docs/PROJECT.md` outside the diploma narrative.

## Done criteria

- University context is clear.
- Main users and access scenario are clear.
- Biometric identification, fallback/manual check, consent/privacy, event logging and mock turnstile are described consistently.
- `docs/CURRENT_STATE.md` contains a short handoff with `Next task: 015b`.

## Handoff

Stop after updating `docs/CURRENT_STATE.md`. Do not start 015b in the same context window.