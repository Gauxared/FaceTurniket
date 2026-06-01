# Current State

Date: 2026-05-31.

## Project Stage

Real face provider (InsightFace) is implemented with graceful fallback. Dataset evaluation is available. The web interface is implemented. The project is now centered on the normal product flow rather than a detached demo mode.

## Implemented

- Base documentation files exist:
  - `AGENTS.md`
  - `docs/PROJECT.md`
  - `docs/CONTRACTS.md`
  - `docs/ITERATION_PLAN.md`
  - `docs/CURRENT_STATE.md`
- Project skeleton:
  - `README.md` - project description, provider selection, setup, dataset evaluation, links to docs
  - `scripts/check.ps1` - automated check runner
  - `.gitignore` - Python, venv, IDE, logs, real images, reports
  - `src/` - application source
  - `tests/` - tests
  - `harness/` - integration harness
  - `harness/cases/` - scenario cases
  - `harness/fixtures/` - test fixtures
  - `scripts/` - utility scripts
- Contracts (`src/contracts/models.py`):
  - `QualityResult`, `LivenessResult`, `MatchResult`, `RecognitionResult`
  - `AccessDecision`, `EventLogEntry`, `TurnstileCommand`
  - `RecognitionResult.embedding: Optional[List[float]]`
- Identity layer (`src/identity/`):
  - `src/identity/models.py` - `UserProfile`, `FaceTemplate`, `EnrollmentResult`, `IdentitySearchResult`
  - `src/identity/template_store.py` - `InMemoryTemplateStore`
  - `src/identity/enrollment.py` - `EnrollmentService`
  - `src/identity/matcher.py` - `IdentityMatcher` for 1:1 and 1:N flows
- Face recognition modules:
  - `src/face/providers/base.py` - `FaceRecognitionProvider` interface
  - `src/face/providers/mock_provider.py` - deterministic mock provider
  - `src/face/providers/insightface_provider.py` - InsightFace adapter with graceful fallback
  - `src/face/providers/factory.py` - provider selection by env/config
  - `src/face/quality_gate.py` - frame series evaluation
  - `src/face/recognition_pipeline.py` - `process()` and `process_series()`
- Tests:
  - `tests/test_contracts.py`
  - `tests/test_mock_provider.py`
  - `tests/test_identity_store.py`
  - `tests/test_enrollment.py`
  - `tests/test_identity_matcher.py`
  - `tests/test_quality_gate.py`
  - `tests/test_mock_camera.py`
  - `tests/test_recognition_pipeline.py`
  - `tests/test_provider_factory.py`
  - `tests/test_access_decision.py`
  - `tests/test_harness.py`
  - `tests/test_turnstile.py`
  - `tests/test_event_log.py`
  - `tests/test_evaluate_dataset.py`
  - `tests/test_web_api.py`
- Mock turnstile (`src/devices/`):
  - `src/devices/turnstile.py` - `MockTurnstile`
- Event log (`src/events/`):
  - `src/events/event_log.py` - JSONL event log writer
- Harness (`harness/`):
  - `harness/run_all.py`
  - 16 scenario cases covering allowed, denied, low quality, spoof, multiple faces, low similarity, ambiguous match, and video-series behavior
- Camera modules:
  - `src/camera/mock_camera.py`
- Quality gate:
  - `src/face/quality_gate.py`
- Access decision:
  - `src/access/policies.py`
  - `src/access/decision.py`
- Dataset evaluation:
  - `scripts/evaluate_dataset.py`
  - supports local celebrity dataset evaluation without copying real photos into the repo
- Web API and interface:
  - `src/web_api/app.py`
  - `src/web_api/schemas.py`
  - `src/web_api/services.py`
  - `src/web_api/utils.py`
  - endpoints for recognition, video processing, enrollment, users, events, health
- Web frontend:
  - `static/index.html`
  - `static/css/style.css`
  - `static/js/main.js`
  - tabs for recognition, video, enrollment, users, events

## Not Implemented Yet

- Real-time camera feed with WebSocket streaming
- Advanced visualizations such as landmarks or heat maps
- Admin panel for user management and statistics
- Mobile-first responsive polish
- Authentication and authorization
- Physical turnstile integration
- Production database or persistence layer
- Docker containerization

## Current Work

Task 014 `tasks/014_confidence_policy_and_thresholds.md` is completed.
Access decision now uses confidence zones (allow/review/deny) instead of a single hard threshold.
Identity matching now exposes top-2 margin internally and uses configurable ambiguity margin.
Dataset evaluation report now includes threshold-policy observations and suggested manual-check counts.
LFW dataset support remains available via `tools/prepare_lfw_subset.py`.

## Next Task

Task 015 `tasks/015_diploma_alignment_and_final_demo.md`.

Goal: align the final demonstration and docs with the diploma narrative and defense flow.

## How to Run Web Interface

Development:
```powershell
python -m uvicorn src.web_api.app:app --reload --host 0.0.0.0 --port 8000
```

Then open http://localhost:8000 in a browser.

Production:
```powershell
python -m uvicorn src.web_api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Checks

Run with:

```powershell
scripts/check.ps1
```

Currently `scripts/check.ps1` passes:
- pytest: 152 passed, 2 skipped
- harness: 16 scenarios passing with turnstile command, event logging, quality gate, identity matching, and mock provider
- Web API health check: FastAPI app initializes and root UI serves without the Demo tab; the interface text is now presented in Russian

## Constraints

- Do not add real user photos
- Do not add real biometric data
- Mock provider remains default
- Real ML dependencies are optional
- Do not implement a physical turnstile in the MVP
- Do not mix ML module code with access decision logic

## Provider Selection

Default provider: mock (no ML dependency)

Optional provider: insightface (requires `pip install insightface onnxruntime`)

Enable InsightFace:
```powershell
$env:FACE_PROVIDER = "insightface"
```

Or programmatically:
```python
provider = ProviderFactory.create(provider_name="insightface")
```

## Next Improvement Tasks

After the practice-report review, the project continues with normal product-flow improvements:

- `tasks/012_video_flow_fix.md` - fix web video processing to use real frames
- `tasks/013_video_enrollment.md` - enroll users from short videos and create multiple templates
- `tasks/014_confidence_policy_and_thresholds.md` - add confidence zones and ambiguity margin
- `tasks/015_diploma_alignment_and_final_demo.md` - align docs and final defense script with the practice report
