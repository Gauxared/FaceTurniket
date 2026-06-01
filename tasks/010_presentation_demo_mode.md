# Task 010 - Presentation Demo Mode

## Goal

Prepare a reliable demonstration mode for the diploma presentation.

The goal is not to prove perfect face recognition in uncontrolled conditions.
The goal is to show a complete access-control prototype:

```text
photo or video input
-> quality/capture processing
-> face recognition provider
-> identity matching
-> access decision
-> mock turnstile command
-> event log
-> clear web UI result
```

The demo must be predictable enough to run in front of the commission without
depending on luck, lighting, or live camera conditions.

## Business Framing

The system is a diploma MVP for a turnstile access-control scenario.

For the presentation, the expected story is:

- a user is registered in the system;
- the system receives a photo or video;
- the system checks face quality and recognition result;
- the system decides whether access is allowed;
- the mock turnstile receives an `open` or `keep_closed` command;
- the access attempt is written to the event log;
- the UI explains the result in a way that is easy to demonstrate.

## Required

### 1. Demo Assets Strategy

Create a safe local demo structure:

```text
demo/
  README.md
  DEMO_SCRIPT.md
  config.example.json
```

Do not commit real personal photos or biometric data.

The `demo/README.md` must explain where local demo files should be placed, for
example:

```text
demo/local/
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

`demo/local/` must be gitignored.

### 2. Demo Configuration

Add a demo config format that can describe:

- demo user id;
- display name;
- access allowed flag;
- enrollment images;
- successful pass image;
- optional successful pass video;
- denied/unknown image;
- optional low-quality image;
- provider name;
- threshold values used for the demo.

The config should be local-file friendly and easy to edit before presentation.

Suggested file:

```text
demo/config.example.json
```

Suggested local file:

```text
demo/local/config.json
```

The example config must not reference real private photos.

### 3. Demo Preparation Script

Create:

```text
scripts/prepare_demo.py
```

The script must:

1. Load `demo/local/config.json` or a path passed through `--config`.
2. Validate that referenced files exist.
3. Initialize the selected provider, preferably `insightface` when available.
4. Enroll the allowed demo user from configured enrollment images.
5. Run a positive photo pass check.
6. Run an unknown/denied photo check if configured.
7. Run a video check if configured and supported by existing code.
8. Write a JSON report to:

```text
reports/demo_report.json
```

9. Print a short console summary:

```text
Demo preparation passed
Allowed photo: allow/open
Unknown photo: deny/keep_closed
Video: allow/open
Report: reports/demo_report.json
```

If optional inputs are missing, the script should skip them with a clear message.
It should not crash unless the required positive demo scenario cannot run.

### 4. Demo Report

The demo report must include:

- timestamp;
- provider;
- threshold values;
- demo user id;
- enrollment image count;
- positive photo result;
- unknown photo result if present;
- video result if present;
- access decision;
- turnstile command;
- recognition reason/status;
- similarity;
- quality score;
- event log path if events were written.

Do not store raw embeddings in the report.

### 5. Web UI Demo Support

Add a minimal, reliable way to use the demo from the web interface.

Choose the smallest option that fits the current UI:

- Option A: Add a "Demo" tab.
- Option B: Add demo preset buttons to the existing Recognition/Video tabs.
- Option C: Add API endpoints only, if UI changes would be too risky.

The demo UI should help the presenter run:

- allowed user photo;
- unknown/denied photo;
- optional video demo;
- event log view.

It must show the important fields visibly:

- decision;
- reason;
- similarity;
- quality score;
- turnstile command;
- event id or log status.

Keep the UI practical and calm. This is an operator/testing console, not a
marketing landing page.

### 6. Presentation Script

Create:

```text
demo/DEMO_SCRIPT.md
```

It must contain a step-by-step talk track for the defense:

1. Start the server.
2. Open the web UI.
3. Show the registered demo user.
4. Upload or run the allowed photo scenario.
5. Explain the recognition result.
6. Explain the access decision.
7. Show the mock turnstile command.
8. Show the event log.
9. Run a denied/unknown scenario.
10. Run a video scenario if prepared.
11. Explain system limitations honestly.

The script must include a fallback plan:

- if live upload fails;
- if InsightFace dependency is unavailable;
- if the room lighting makes a fresh photo unreliable;
- if video processing is too slow.

### 7. Documentation Updates

Update:

- `README.md` with demo mode commands;
- `docs/CURRENT_STATE.md` with Task 010 status;
- `docs/WEB_QUICK_START.md` or `docs/WEB_INTERFACE.md` if UI/API changes were made;
- `.gitignore` for local demo assets and generated demo reports.

## Suggested Commands

Prepare local demo:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_demo.py --config demo\local\config.json --report reports\demo_report.json
```

Run checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe harness\run_all.py
```

Run web UI:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.web_api.app:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## Tests

Add tests that do not require real personal photos:

- demo config parser/validator;
- missing optional files are skipped clearly;
- missing required positive scenario fails clearly;
- demo report writer;
- demo service/script can run with mock provider and temporary fixture files;
- web API demo endpoint tests if endpoints are added.

Do not make normal tests depend on InsightFace or private local images.

## Forbidden

- Do not commit real personal photos.
- Do not commit real biometric embeddings.
- Do not train a model.
- Do not make InsightFace required for all tests.
- Do not remove mock provider.
- Do not bypass access decision logic just to force `allow`.
- Do not fake the event log or turnstile command in the final demo flow.
- Do not put access rules inside the ML provider.
- Do not use gender, age, race, emotion, or similar sensitive attributes.

## Done Criteria

- `demo/README.md` exists and explains local demo assets.
- `demo/DEMO_SCRIPT.md` exists and gives a defense-ready scenario.
- `demo/config.example.json` exists.
- `demo/local/` is gitignored.
- `scripts/prepare_demo.py` exists and writes `reports/demo_report.json`.
- The positive demo flow can produce `allow` and `open` using configured assets.
- The denied demo flow can produce `deny` or `retry` and `keep_closed`.
- The web UI or API has a clear demo path.
- Tests pass.
- Harness passes.
- README and CURRENT_STATE are updated.

## Final Answer Requirements

When this task is complete, report:

- what files were created or changed;
- which demo scenarios are supported;
- how to prepare local demo assets;
- exact commands to run the demo;
- which checks passed;
- remaining limitations for the diploma presentation.
