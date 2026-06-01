# Task 007 - Enrollment and Identity Store

## Goal

Add a local enrollment and identity-search layer before connecting a real face
provider.

The system already selects the best frame from a series. This task adds the
next layer: storing registered users and comparing the selected frame result
against user templates.

This task must still use mock data. It must not add real ML dependencies or real
personal photos.

## Required

Create an `src/identity/` package with modules such as:

- `src/identity/models.py`
- `src/identity/template_store.py`
- `src/identity/enrollment.py`
- `src/identity/matcher.py`

Implement local models for:

- `UserProfile`
- `FaceTemplate`
- `EnrollmentResult`
- optionally `IdentitySearchResult` if it helps keep match logic clear.

Implement a local in-memory template store that can:

- add a user profile;
- add one or more face templates for a user;
- list templates for a user;
- list all templates;
- find a user by id;
- avoid duplicate template ids.

Implement enrollment flow:

```text
image/frame -> recognition pipeline/provider -> template stored for user
```

For this task, a template may use a deterministic mock embedding or a stable
template id derived from the filename. Do not store real image bytes.

Implement matching/search flow:

- `1:1 verification`: compare selected frame against templates for a claimed
  `user_id`;
- `1:N identification`: compare selected frame against all templates.

The first supported production-like mode should be `1:1 verification`. `1:N`
can be implemented as a simple mock search, but it must be clearly documented as
less preferred for large databases.

## Integration Boundary

Keep responsibilities separated:

- face provider extracts recognition/embedding-like data;
- identity layer stores templates and computes match result;
- access module decides `allow`, `deny`, `retry`, or `manual_check`;
- turnstile module returns a command;
- event log records the attempt.

The access module must not directly search template storage.

## Harness Impact

Add or update harness cases for:

- successful `1:1 verification`;
- failed `1:1 verification` for wrong claimed user;
- successful mock `1:N identification`;
- unknown user in template store;
- duplicate enrollment rejected or handled deterministically.

Cases must not use real personal images.

## Forbidden

- Do not add DeepFace, InsightFace, OpenCV SFace, or other real ML libraries.
- Do not train a model.
- Do not store real photos.
- Do not store real biometric embeddings.
- Do not let identity search open the turnstile directly.
- Do not move access decision rules into identity matching.

## Tests

Add tests for:

- creating user profiles and templates;
- adding templates to the store;
- duplicate template behavior;
- `1:1 verification` success;
- `1:1 verification` failure;
- `1:N identification` success;
- unknown user/template handling;
- integration with recognition pipeline using mock provider.

Recommended files:

- `tests/test_identity_store.py`
- `tests/test_enrollment.py`
- `tests/test_identity_matcher.py`

## Documentation

Update:

- `docs/CURRENT_STATE.md`;
- `docs/PROJECT.md` with a short description of enrollment and search;
- `docs/CONTRACTS.md` if new public contracts are introduced;
- `README.md` only if user-facing commands change.

## Done Criteria

- `python -m pytest -q` passes.
- `python harness/run_all.py` passes.
- `scripts/check.ps1` passes.
- Identity store works without real ML dependencies.
- Mock provider and existing harness scenarios still pass.
- `docs/CURRENT_STATE.md` is updated.

