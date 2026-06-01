# Task 011 - Product Flow Cleanup

## Goal

Remove or de-emphasize the artificial presentation-only demo layer and make the
normal web interface the main demonstration path.

The diploma system should be shown as a real access-control prototype:

```text
Enrollment -> Recognition / Video -> Access Decision -> Turnstile -> Event Log
```

The current `Demo` tab and `/api/demo/run` endpoint feel detached from the
actual product workflow. The system should not need a special "demo button" to
look convincing.

## Context From Practice Report

The report describes a biometric access-control system for a university:

- users are registered in the system;
- the system receives an image from a camera or terminal;
- the biometric module detects face, checks quality, extracts template, and
  compares it with reference templates;
- business logic checks user activity, consent, access rules, and blocks;
- the system sends a turnstile command and logs the event;
- guard/admin interfaces show results, reasons, users, rights, and events.

The web UI should reflect this business process directly.

## Required

1. Review all demo-specific files and usages:

```text
src/demo/
scripts/prepare_demo.py
demo/
static/index.html
static/js/main.js
src/web_api/app.py
src/web_api/schemas.py
tests/test_demo_mode.py
tests/test_web_api.py
docs/*
README.md
```

2. Remove the `Demo` tab from the main web UI.

3. Remove or hide `/api/demo/run` from the production-facing API.

4. Decide what to do with `src/demo/` and `scripts/prepare_demo.py`:

- preferred: remove them if they duplicate normal product flow;
- acceptable: keep them only as local developer utilities, not as main UI/API;
- if kept, document that they are optional local scripts and not part of the
  product workflow.

5. Update docs so the presentation path is:

```text
1. enroll user
2. check user list
3. upload pass photo or video
4. show access decision
5. show mock turnstile command
6. show event log
```

6. Ensure the web UI still supports:

- image recognition;
- video recognition;
- user enrollment;
- users list;
- events list.

## Forbidden

- Do not bypass the real access decision flow.
- Do not hard-code `allow` for presentation.
- Do not remove useful core modules such as provider, identity matcher,
  access decision, turnstile, or event log.
- Do not commit local personal photos.
- Do not remove mock provider or harness.

## Tests

Update tests as needed:

- remove tests for deleted demo endpoints;
- keep web API tests passing;
- keep harness passing;
- add a simple test that the root UI still serves without the Demo tab if
  practical.

## Done Criteria

- No visible `Demo` tab in the main UI.
- No product-facing demo endpoint unless explicitly documented as local/dev.
- Normal web flow remains usable.
- `scripts/check.ps1` passes.
- `docs/CURRENT_STATE.md` is updated.

