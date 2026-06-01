# Task 009 — Celebrity Dataset Evaluation

## Goal

Create a local evaluation/smoke flow on real celebrity photos through InsightFace provider.

## What was implemented

1. **InsightFace provider path handling** (`src/face/providers/insightface_provider.py`):
   - Accepts `str`, `Path`, or numpy array;
   - Loads image via `cv2.imread` for paths;
   - Returns `RecognitionResult` with `face_detected=False` for missing/unreadable files.

2. **Embedding flow** (`src/contracts/models.py`, `src/identity/enrollment.py`, `src/identity/matcher.py`):
   - Added `embedding: Optional[List[float]]` to `RecognitionResult`;
   - `EnrollmentService` uses real embedding from provider when available, falls back to mock;
   - `IdentityMatcher` uses real embedding from `recognition.embedding` when available, falls back to mock.

3. **Dataset evaluation script** (`scripts/evaluate_dataset.py`):
   - Scans dataset directory structure;
   - Selects enrollment and probe images deterministically;
   - Runs 1:1 verification (positive and negative pairs);
   - Runs 1:N identification;
   - Computes metrics: TA, FR, TR, FA, Top-1 Correct, Not Found, Ambiguous;
   - Outputs JSON report;
   - Does NOT copy photos to repository.

4. **Tests** (`tests/test_evaluate_dataset.py`):
   - Dataset scanner on temporary folders;
   - Image selection determinism;
   - Metrics aggregation;
   - JSON report writer;
   - Provider error handling.

5. **Documentation**:
   - Updated `docs/CONTRACTS.md` with `embedding` field;
   - Updated `docs/CURRENT_STATE.md`;
   - Updated `README.md` with dataset evaluation commands.

## Commands

Smoke run:
```powershell
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --dataset "D:\Download\Celebrity Faces Dataset" --max-people 3 --enroll-per-person 2 --probe-per-person 2 --threshold 0.7 --provider insightface --report reports/dataset_eval_smoke.json
```

Full evaluation:
```powershell
.\.venv\Scripts\python.exe scripts\evaluate_dataset.py --dataset "D:\Download\Celebrity Faces Dataset" --enroll-per-person 3 --probe-per-person 5 --threshold 0.7 --provider insightface --report reports/dataset_eval.json
```

## Results (smoke run)

- People processed: 3
- Enrolled templates: 6
- Probe images: 6
- Detection failures: 1
- Quality failures: 1
- True Accept: 2
- False Reject: 2
- True Reject: 4
- False Accept: 0
- Top-1 Correct: 1
- Not Found: 2
- Ambiguous: 1
- Avg similarity positive: 0.6583
- Avg similarity negative: 0.0000

## Results (full run, 17 people)

- People processed: 17
- Enrolled templates: 47
- Probe images: 85
- Detection failures: 4
- Quality failures: 11
- True Accept: 31
- False Reject: 43
- True Reject: 74
- False Accept: 0
- Top-1 Correct: 17
- Not Found: 43
- Ambiguous: 14
- Avg similarity positive: 0.6657
- Avg similarity negative: 0.0000

## Constraints preserved

- Mock provider remains default;
- No real photos in repository;
- No dataset copying;
- `reports/` is gitignored;
- No gender/age/race/emotion for access decisions;
- ML module does not open turnstile.
