# Task 002 - Contracts and Mock Pipeline

## Goal

Implement stable data contracts and a deterministic mock recognition pipeline.

The goal is not to recognize real faces. The goal is to create predictable
module boundaries for tests and future harness scenarios.

## Required Contracts

Create contract models for:

- `QualityResult`
- `LivenessResult`
- `MatchResult`
- `RecognitionResult`
- `AccessDecision`
- `EventLogEntry`
- `TurnstileCommand`

Recommended location:

- `src/contracts/`

Contracts may use dataclasses, enums, or Pydantic only if already justified by
the project. Prefer standard-library dataclasses for this task.

Contracts must match `docs/CONTRACTS.md`. If the implementation needs to change
the contract, update `docs/CONTRACTS.md` and tests in the same task.

## Required Face Modules

Create:

- `src/face/providers/base.py`
- `src/face/providers/mock_provider.py`
- `src/face/recognition_pipeline.py`

`base.py` must define the provider interface.

`MockFaceRecognitionProvider` must return `RecognitionResult` based on fixture
data or image filename.

Required filename behavior:

- `user_001_good.jpg` -> matched `user_001`
- `unknown_001.jpg` -> match not found
- `low_quality_001.jpg` -> bad quality
- `multiple_faces_001.jpg` -> multiple faces
- `spoof_001.jpg` -> liveness failed
- unknown filename -> safe not-found or invalid-image result

`recognition_pipeline.py` must orchestrate provider calls but must not make
business access decisions.

## Important Boundary

Face recognition code returns recognition data only.

It must not:

- check whether a user is allowed through a turnstile;
- return final `allow` or `deny`;
- open or close a turnstile;
- write access event logs.

## Forbidden

- Do not connect DeepFace, InsightFace, OpenCV SFace, or similar libraries.
- Do not train any model.
- Do not add API code.
- Do not add database code.
- Do not implement final access decision logic in the face provider.
- Do not make tests depend on real images.

## Tests

Add tests for:

- contract creation and serialization if serialization helpers exist;
- mock provider output for every required filename;
- recognition pipeline output;
- invalid or unknown image scenario;
- provider interface shape.

Recommended files:

- `tests/test_contracts.py`
- `tests/test_mock_provider.py`
- `tests/test_recognition_pipeline.py`

## Documentation

Update `docs/CURRENT_STATE.md`:

- mark contracts and mock pipeline as implemented;
- mention the supported mock filenames;
- set the next task to `tasks/003_access_decision.md`.

## Done Criteria

- `python -m pytest -q` passes.
- Mock provider returns deterministic `RecognitionResult`.
- Recognition pipeline works without real ML dependencies.
- Contracts match `docs/CONTRACTS.md`.
- `docs/CURRENT_STATE.md` is updated.

