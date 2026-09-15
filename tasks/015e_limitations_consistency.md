# Task 015e - Limitations Consistency

## Goal

Make the final user-facing documentation state the same prototype limitations and fallback rules without broad rewrites.

## Required context

Read only:

- the limitations/restrictions section of `docs/PROJECT.md`;
- the relevant launch/demo section of `README.md`;
- the limitations/end section of `docs/DEFENSE_DEMO_SCRIPT.md`.

Do not read entire unrelated docs.

## Allowed changes

- `docs/PROJECT.md`
- `README.md`
- `docs/DEFENSE_DEMO_SCRIPT.md`
- `docs/CURRENT_STATE.md`

## Required limitations

Ensure the documents are consistent about these points:

- no physical turnstile integration in the prototype;
- no production database/persistence layer yet;
- liveness is limited or mocked unless a real provider supplies it;
- controlled capture conditions are required;
- real deployment requires consent, privacy/security controls and threshold calibration;
- ambiguous/low-quality cases must fall back to retry/manual check rather than forced access.

## Steps

1. Compare only the relevant sections of the three documents.
2. Fix contradictions or missing items with minimal edits.
3. Keep wording appropriate to each document instead of copying one large identical block everywhere.
4. Confirm that none of the three documents imply production readiness.

## Checks

No code tests are required.

Perform a focused text review of the changed sections only.

## Forbidden

- No source-code changes.
- No new features.
- No speculative legal claims or invented compliance certifications.
- Do not overstate recognition accuracy or liveness capabilities.

## Done criteria

- The required limitations are consistent across final-facing docs.
- Fallback/manual-check behavior is explicit.
- No production-ready claim remains in those sections.
- `docs/CURRENT_STATE.md` ends with `Next task: 015f`.

## Handoff

Stop after the handoff. Run 015f in a fresh context.