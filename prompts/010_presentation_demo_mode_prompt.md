# Prompt - Task 010 Presentation Demo Mode

Working directory:

```text
D:\Kamenev_solo2
```

You are implementing:

```text
tasks/010_presentation_demo_mode.md
```

## Context

This is a diploma project: a prototype access-control system for a turnstile.

The presentation goal is to demonstrate a reliable end-to-end flow:

```text
photo/video input
-> quality/capture processing
-> face recognition
-> identity matching
-> access decision
-> mock turnstile command
-> event log
-> visible result in web UI
```

Do not try to solve perfect uncontrolled face recognition. The demo must be
predictable, explainable, and safe to run in front of the commission.

## Before You Start

Read:

- `AGENTS.md`
- `README.md`
- `docs/PROJECT.md`
- `docs/CONTRACTS.md`
- `docs/CURRENT_STATE.md`
- `docs/WEB_INTERFACE.md`
- `tasks/010_presentation_demo_mode.md`

Also inspect:

- `src/web_api/`
- `static/`
- `scripts/evaluate_dataset.py`
- `src/identity/`
- `src/face/`
- `src/access/`
- `src/devices/`
- `src/events/`

## Main Requirement

Implement a presentation demo mode without breaking the existing MVP.

The demo must support:

- an allowed registered user;
- an unknown/denied user;
- optional low-quality example;
- optional video example;
- event log visibility;
- mock turnstile command visibility.

## Important Design Rule

Do not fake the business flow.

The successful demo must still pass through the actual system modules:

```text
provider -> pipeline -> identity matcher -> access decision -> turnstile -> event log
```

It is fine to use controlled demo assets and tuned demo thresholds, but do not
hard-code "allow" in the UI or bypass the decision module.

## Implement

1. Create:

```text
demo/README.md
demo/DEMO_SCRIPT.md
demo/config.example.json
scripts/prepare_demo.py
```

2. Add `.gitignore` entries for:

```text
demo/local/
reports/demo_report.json
```

3. Implement demo config loading and validation.

4. Implement `scripts/prepare_demo.py`:

- loads config;
- validates files;
- initializes provider;
- enrolls demo user;
- runs allowed photo scenario;
- runs denied/unknown scenario if configured;
- runs video scenario if configured and feasible;
- writes `reports/demo_report.json`;
- prints a concise summary.

5. Add web UI/API demo support using the smallest safe approach:

- preferred: a small Demo tab or demo preset controls;
- acceptable: demo API endpoints if UI changes are risky.

6. Update docs:

- `README.md`;
- `docs/CURRENT_STATE.md`;
- `docs/WEB_QUICK_START.md` or `docs/WEB_INTERFACE.md` if web behavior changes.

7. Add tests that do not require private photos:

- config parser/validator;
- report writer;
- mock-provider demo preparation flow with temporary fixture files;
- web endpoint tests if endpoints are added.

## Local Demo Assets

Do not commit personal photos.

The user may create local files like:

```text
demo/local/
  config.json
  allowed_user/
    enroll_01.jpg
    enroll_02.jpg
    pass_photo.jpg
    pass_video.mp4
  denied_user/
    unknown_photo.jpg
  low_quality/
    bad_photo.jpg
```

Your code must work with this structure, but the repo should only contain
`demo/config.example.json` and documentation.

## Verification Commands

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe harness\run_all.py
```

If demo local assets exist, also run:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_demo.py --config demo\local\config.json --report reports\demo_report.json
```

If web UI changed, run or smoke-check:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.web_api.app:app --reload --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

## Forbidden

- Do not commit real photos.
- Do not commit embeddings.
- Do not train a model.
- Do not make InsightFace mandatory for normal tests.
- Do not remove mock provider.
- Do not bypass access decision logic.
- Do not fake turnstile/event results.
- Do not add unrelated production features.

## Final Response

In the final response, include:

- files changed;
- demo scenarios supported;
- commands to run checks and demo;
- whether tests and harness passed;
- whether local real-photo demo was run or skipped;
- remaining risks for the live presentation.
