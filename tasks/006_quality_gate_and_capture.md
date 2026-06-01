# Task 006 - Quality Gate and Capture Flow

## Goal

Introduce a clearer capture and quality-gate layer before recognition.

This task prepares the project for real camera input without adding a real
camera or real ML dependency.

## Required

Create modules such as:

- `src/camera/mock_camera.py`
- `src/face/quality_gate.py`

The mock camera should produce a deterministic series of frame descriptors or
fixture paths.

The quality gate should:

- evaluate a series of candidate frames;
- reject frames with no face, multiple faces, low quality, or spoof indicators
  when that information is available;
- choose the best acceptable frame;
- return a `QualityResult` or a small capture result object that references the
  selected frame.

Recognition pipeline should use the selected frame.

## Required Scenarios

Add or update harness cases for:

- no acceptable frame;
- one good frame among bad frames;
- all frames low quality.

## Forbidden

- Do not connect a physical camera.
- Do not add OpenCV unless the task explicitly justifies it.
- Do not use real personal photos.
- Do not let a rejected frame produce `allow`.

## Tests

Add tests for:

- best frame selection;
- all frames rejected;
- low quality leads to retry or deny according to access policy;
- recognition pipeline receives the selected frame.

Recommended files:

- `tests/test_quality_gate.py`
- `tests/test_mock_camera.py`

## Documentation

Update:

- `docs/CURRENT_STATE.md`;
- `docs/PROJECT.md` if the capture flow description changes;
- `docs/CONTRACTS.md` if new public capture contracts are introduced.

## Done Criteria

- `python -m pytest -q` passes.
- `python harness/run_all.py` passes.
- Capture/quality behavior is deterministic.
- No real camera or heavy ML dependency is added.
- `docs/CURRENT_STATE.md` is updated.

