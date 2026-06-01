# Task 003 - Access Decision

## Goal

Implement business decision logic that converts `RecognitionResult` into
`AccessDecision`.

This task separates access policy from ML. The face provider must remain a data
source only.

## Required

Create:

- `src/access/decision.py`
- `src/access/policies.py`

`decision.py` should expose one main function, for example:

```python
decide_access(recognition_result, policy) -> AccessDecision
```

`policies.py` should contain thresholds and policy settings, for example:

- minimum similarity threshold;
- minimum quality threshold;
- ambiguous match behavior: `manual_check` or `deny`.

## Decision Rules

Implement these rules in this priority order:

1. face not detected -> `deny`
2. multiple faces -> `deny`
3. low quality -> `retry`
4. liveness failed -> `deny`
5. match not found -> `deny`
6. ambiguous match -> `manual_check` or `deny`
7. similarity below threshold -> `deny`
8. user not allowed -> `deny`
9. matched and access allowed -> `allow`

The result must be an `AccessDecision`.

If the current `RecognitionResult` does not yet contain access-rights data, use
a small local mock policy/user registry inside `src/access/policies.py`.

## Forbidden

- Do not put ML logic into access module.
- Do not import DeepFace, InsightFace, OpenCV, or real ML code.
- Do not open the turnstile from `decision.py`.
- Do not write event logs from `decision.py`.
- Do not mutate `RecognitionResult`.

## Tests

Add tests for:

- allow matched user with access;
- deny unknown user;
- retry low quality;
- deny spoof attempt;
- deny user without access;
- deny multiple faces;
- deny face not detected;
- deny low similarity;
- manual_check or deny ambiguous match.

Recommended file:

- `tests/test_access_decision.py`

## Harness Impact

If harness already exists, make it use access decision.

If harness does not exist yet, do not build it in this task. Keep the access
module ready for Task 004.

## Documentation

Update `docs/CURRENT_STATE.md`:

- mark access decision as implemented;
- list supported decisions and reasons;
- set the next task to `tasks/004_harness.md`.

## Done Criteria

- `python -m pytest -q` passes.
- Access decision covers every required rule.
- Face provider still has no business decision logic.
- `docs/CURRENT_STATE.md` is updated.

