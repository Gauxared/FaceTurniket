# Task 008 - Optional Real Face Provider

## Goal

Add one real face-recognition provider through the existing provider/adapter
architecture.

This task is optional until the mock pipeline, harness, access decision, event
log, quality flow, and identity store are stable.

## Required

Choose one provider implementation:

- `DeepFaceProvider`
- `InsightFaceProvider`
- `OpenCVSFaceProvider`

The real provider must:

- implement the same `FaceRecognitionProvider` interface;
- return project contracts, not raw library objects;
- not change access decision logic;
- not remove `MockFaceRecognitionProvider`;
- work with the identity/enrollment layer;
- be selectable through config;
- fail gracefully when optional dependencies are not installed.

Add a config mechanism such as:

- environment variable;
- small config file;
- factory function.

Default provider must remain mock.

## Forbidden

- Do not train a model from scratch.
- Do not use gender, age, race, emotion, or similar attributes for access
  decisions.
- Do not store real personal photos in the repository.
- Do not break mock provider or harness.
- Do not make real ML dependencies mandatory for normal tests.
- Do not import optional ML packages at module import time if that breaks users
  without the dependency.

## Tests

Add tests that:

- provider interface remains stable;
- mock provider still works;
- config can select mock provider;
- config can request real provider;
- missing real provider dependency produces a clear error;
- identity store still works with mock provider;
- harness still passes with mock provider.

For real provider tests, prefer smoke tests marked as optional or skipped when
the dependency is missing.

## Documentation

Update:

- `README.md` with optional install instructions;
- `docs/CURRENT_STATE.md`;
- `docs/PROJECT.md` if provider choice changes system behavior;
- `docs/CONTRACTS.md` only if the public contract changes.

## Done Criteria

- `python -m pytest -q` passes without real ML dependencies.
- `python harness/run_all.py` passes with mock provider.
- Real provider can be enabled locally when optional dependencies are installed.
- Missing optional dependency is handled gracefully.
- `docs/CURRENT_STATE.md` is updated.

