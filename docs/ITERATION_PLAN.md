# Iteration Plan

## Principle

The project is developed by one AI model through small sequential tasks.

Each iteration has a task file in `tasks/`. The agent should complete only the
current task, run checks, and update `docs/CURRENT_STATE.md`.

When `scripts/check.ps1` exists, use:

```powershell
scripts/check.ps1
```

Otherwise run the available checks manually:

```powershell
python -m pytest -q
python harness/run_all.py
```

## Iteration 001 - Project Skeleton

Task file:

```text
tasks/001_project_skeleton.md
```

Goal:

- create base folders;
- add `README.md`;
- add `scripts/check.ps1`;
- add `.gitignore`;
- prepare empty `src`, `tests`, and `harness`.

Forbidden:

- real ML;
- recognition logic;
- API;
- database logic.

## Iteration 002 - Contracts and Mock Pipeline

Task file:

```text
tasks/002_contracts_and_mock_pipeline.md
```

Goal:

- implement contract models;
- create `FaceRecognitionProvider` interface;
- create `MockFaceRecognitionProvider`;
- create `RecognitionPipeline`.

Forbidden:

- DeepFace, InsightFace, OpenCV SFace;
- model training;
- access decision inside provider.

## Iteration 003 - Access Decision

Task file:

```text
tasks/003_access_decision.md
```

Goal:

- implement access decision logic;
- keep access logic separate from ML;
- add tests for allow, deny, retry, and manual_check.

Forbidden:

- ML imports in access module;
- turnstile commands from decision logic;
- event logging from decision logic.

## Iteration 004 - Harness

Task file:

```text
tasks/004_harness.md
```

Goal:

- create `harness/cases`;
- create `harness/fixtures`;
- implement `harness/run_all.py`;
- add baseline scenario cases.

Minimum scenarios:

- `known_user_allowed`;
- `unknown_user_denied`;
- `low_quality_photo`;
- `multiple_faces`;
- `spoof_attempt`;
- `user_without_access`.

## Iteration 005 - Event Log and Mock Turnstile

Task file:

```text
tasks/005_event_log_and_turnstile.md
```

Goal:

- implement mock turnstile;
- implement JSONL event log;
- ensure turnstile opens only on `allow`;
- ensure every attempt can be logged.

## Iteration 006 - Quality Gate and Capture Flow

Task file:

```text
tasks/006_quality_gate_and_capture.md
```

Goal:

- introduce mock camera or frame series input;
- choose best frame deterministically;
- reject bad capture conditions before recognition can allow access.

Forbidden:

- physical camera dependency;
- OpenCV unless explicitly justified;
- real personal images.

## Iteration 007 - Enrollment and Identity Store

Task file:

```text
tasks/007_enrollment_and_identity_store.md
```

Goal:

- add local user profiles and face templates;
- support enrollment with mock templates;
- support `1:1 verification`;
- support simple mock `1:N identification`;
- keep access decisions outside the identity layer.

Forbidden:

- real ML dependencies;
- real photos or real biometric embeddings;
- turnstile commands from identity matching;
- access decision rules inside identity matching.

## Iteration 008 - Optional Real Face Provider

Task file:

```text
tasks/008_real_face_provider.md
```

Goal:

- connect one real face-recognition library through provider/adapter;
- keep mock provider as default;
- keep harness passing without real ML dependencies;
- handle missing optional dependency gracefully.

Possible providers:

- `DeepFaceProvider`;
- `InsightFaceProvider`;
- `OpenCVSFaceProvider`.

## Iteration 009 - Dataset Evaluation

Task file:

```text
tasks/009_dataset_evaluation.md
```

Goal:

- evaluate InsightFace on a local photo dataset;
- keep the dataset outside the repository;
- measure 1:1 verification and 1:N identification;
- write JSON reports under `reports/`;
- keep mock provider and harness stable.

Forbidden:

- model training;
- committing real photos;
- committing biometric embeddings;
- making real ML mandatory for normal tests.

## Iteration 010 - Presentation Demo Mode

Task file:

```text
tasks/010_presentation_demo_mode.md
```

Goal:

- prepare a reliable diploma presentation flow;
- support a controlled allowed-user scenario;
- support denied/unknown and optional video scenarios;
- write a demo report;
- make the web UI/API path easy to demonstrate;
- document the exact defense script and fallback plan.

Forbidden:

- hard-coding `allow` without the real decision flow;
- committing personal photos or embeddings;
- bypassing access decision, turnstile, or event log modules;
- making InsightFace required for normal checks.

## Iteration 011 - Product Flow Cleanup

Task file:

```text
tasks/011_product_flow_cleanup.md
```

Goal:

- remove or de-emphasize the artificial Demo tab/API;
- make normal web flow the defense flow;
- keep enrollment, recognition, video, users, and events usable.

## Iteration 012 - Video Flow Fix

Task file:

```text
tasks/012_video_flow_fix.md
```

Goal:

- process actual video frames;
- select the best real frame;
- base matching, decision, turnstile command, and event log on that frame.

## Iteration 013 - Video Enrollment

Task file:

```text
tasks/013_video_enrollment.md
```

Goal:

- enroll a user from a short video;
- create multiple templates from high-quality frames;
- expose the flow in the web UI.

## Iteration 014 - Confidence Policy and Thresholds

Task file:

```text
tasks/014_confidence_policy_and_thresholds.md
```

Goal:

- replace one hard threshold with confidence zones;
- add top-2 margin handling for 1:N identification;
- report threshold behavior in tests/evaluation.

## Iteration 015 - Diploma Alignment and Final Demo

Task file:

```text
tasks/015_diploma_alignment_and_final_demo.md
```

Goal:

- align docs with the practice report;
- prepare final defense script around normal product flow;
- clearly document limitations and fallback handling.

## Transition Rule

Do not move to the next iteration if:

- the current task is incomplete;
- tests fail;
- harness fails;
- `docs/CURRENT_STATE.md` is not updated;
- the implementation changed files outside the task scope without a clear need.
