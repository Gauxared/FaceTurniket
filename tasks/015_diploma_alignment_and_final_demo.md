# Task 015 - Diploma Alignment and Final Demo

## Goal

Align the project with the practice report and prepare the final defense-ready
demonstration.

The final story should be:

```text
The system replaces a simple card/pass workflow with biometric identification
in a controlled access point, while keeping fallback handling for exceptions.
```

## Required

1. Update project documentation from the practice report.

Make sure docs clearly describe:

- university access-control context;
- users: students, employees, guards, admins, visitors;
- problem with physical passes;
- biometric identification as the main MVP flow;
- fallback handling through guard/manual check;
- consent and biometric-data constraints;
- event logging and auditability;
- mock turnstile for prototype stage.

2. Update README with final launch flow:

- run checks;
- start web UI;
- enroll user from photo;
- enroll user from video;
- recognize photo/video;
- view events.

3. Create or update final defense script:

Suggested file:

```text
docs/DEFENSE_DEMO_SCRIPT.md
```

The script must show normal product flow, not a special demo endpoint:

1. Start server.
2. Open web UI.
3. Enroll user from video.
4. Show created templates.
5. Run recognition on a pass photo/video.
6. Show `allow/open`.
7. Run unknown or low-quality example.
8. Show `deny/retry/keep_closed`.
9. Show event log.
10. Explain limitations and next steps.

4. Remove stale docs that claim the old detached Demo tab is the preferred path.

5. Add final limitations section:

- no physical turnstile in prototype;
- no production database yet;
- liveness is limited or mocked unless a real provider is added;
- controlled capture is required;
- real deployment requires consent, security controls, and calibration.

## Forbidden

- Do not claim the system is production-ready.
- Do not claim perfect recognition in uncontrolled conditions.
- Do not present mock provider as real ML.
- Do not hide limitations.
- Do not include private personal photos in repo.

## Tests

No large new code should be needed, but run:

```powershell
scripts/check.ps1
```

If final docs reference commands, verify commands still work.

## Done Criteria

- Documentation matches the practice report.
- Final demo script exists.
- README has concise final workflow.
- No stale recommendation to use artificial Demo tab.
- `scripts/check.ps1` passes.
- `docs/CURRENT_STATE.md` is updated.

