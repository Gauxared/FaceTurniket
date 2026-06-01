# Task 014 - Confidence Policy and Thresholds

## Goal

Replace a single hard threshold with an explainable confidence policy.

Do not solve weak recognition by simply lowering the threshold. A face-only
access system needs controlled behavior:

```text
high confidence -> allow
middle confidence -> retry or manual_check
low confidence -> deny
ambiguous 1:N result -> manual_check or deny
```

## Required

1. Extend `AccessPolicy` or a nearby policy module with confidence zones:

- `allow_threshold`;
- `review_threshold`;
- `deny_below_threshold`;
- optional `identification_margin`.

Suggested defaults:

```text
allow_threshold = 0.72
review_threshold = 0.60
identification_margin = 0.05
```

The exact defaults can be adjusted based on existing dataset reports.

2. Update identity matching to expose enough data for ambiguity decisions.

For 1:N identification, the system should know:

- best user id;
- best similarity;
- second-best similarity if available;
- margin between first and second candidate.

3. Update access decision:

- high confidence matched and user allowed -> allow;
- matched but in review zone -> retry or manual_check;
- below review threshold -> deny;
- low quality -> retry before matching;
- ambiguous margin -> manual_check or deny.

4. Keep existing harness scenarios passing or update expected reasons if the
business logic intentionally changes.

5. Update dataset evaluation to report:

- true accept / false reject at configured thresholds;
- manual_check count if applicable;
- ambiguous count;
- suggested threshold observations.

## Forbidden

- Do not lower thresholds just to make a demo pass.
- Do not hard-code a specific person's result.
- Do not mix ML provider code with access decision logic.
- Do not remove retry/manual_check from the system.
- Do not make real ML mandatory for standard tests.

## Tests

Add tests for:

- allow at high similarity;
- manual_check or retry in review zone;
- deny at low similarity;
- ambiguous 1:N result based on small top-2 margin;
- user not allowed still denies even with high similarity;
- low-quality still retries before threshold checks.

## Done Criteria

- Access policy is explainable and documented.
- Threshold behavior is covered by tests.
- Dataset evaluation exposes enough metrics for threshold discussion.
- `scripts/check.ps1` passes.
- `docs/CURRENT_STATE.md` and `docs/CONTRACTS.md` are updated if contracts change.

