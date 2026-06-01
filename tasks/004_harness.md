# Task 004 - Harness

## Goal

Create a local scenario harness that verifies the recognition pipeline and
access decision behavior end to end.

The harness is the main regression safety net for this project.

## Required

Create or complete:

- `harness/cases/`
- `harness/fixtures/`
- `harness/run_all.py`

The harness must:

1. Load YAML or JSON test cases.
2. Run the recognition pipeline.
3. Run access decision.
4. Compare actual result with expected result.
5. Print a readable passed/failed line for every case.
6. Print a final summary.
7. Exit with non-zero code if any case fails.

Use JSON if YAML support would require a new dependency. Use YAML only if a
parser already exists or a tiny safe parser is implemented for the limited case
format.

## Required Cases

Add at least these scenarios:

- `known_user_allowed`
- `unknown_user_denied`
- `low_quality_photo`
- `multiple_faces`
- `spoof_attempt`
- `user_without_access`

Recommended next scenarios if scope remains small:

- `no_face`
- `low_similarity`
- `ambiguous_match`

## Case Format

Each case must include:

- case name;
- input image path or fixture key;
- expected decision;
- expected reason;
- expected turnstile command only if turnstile command already exists.

Cases must not require real personal photos.

## Forbidden

- Do not use real personal images.
- Do not depend on real ML.
- Do not depend on external services.
- Do not hide failed assertions behind broad exception handling.
- Do not make the harness pass when a case file is malformed.

## Tests

Add tests for:

- harness loads all cases;
- all committed harness cases pass;
- a deliberately mismatched temporary case fails with understandable output;
- CLI exits with code `0` when cases pass.

Recommended file:

- `tests/test_harness.py`

## Documentation

Update:

- `README.md` with harness run command if missing;
- `docs/CURRENT_STATE.md` with the current number of scenarios.

## Done Criteria

- `python harness/run_all.py` works.
- Harness has at least 6 scenarios.
- Failing case output is understandable.
- `python -m pytest -q` passes.
- `scripts/check.ps1` passes if it exists.
- `docs/CURRENT_STATE.md` is updated.

