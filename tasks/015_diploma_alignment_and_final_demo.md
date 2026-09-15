# Task 015 - Diploma Alignment and Final Demo (parent task)

## Purpose

This is a parent task only. Do **not** execute it as one large iteration.

The work is intentionally split into small context-friendly tasks so a local model can complete one task per fresh context window.

## Execution order

1. `tasks/015a_project_narrative_alignment.md`
2. `tasks/015b_readme_final_flow.md`
3. `tasks/015c_defense_demo_script.md`
4. `tasks/015d_stale_demo_docs_cleanup.md`
5. `tasks/015e_limitations_consistency.md`
6. `tasks/015f_final_validation.md`

## Shared outcome

After all six child tasks are complete:

- project docs describe the university access-control context consistently;
- README contains the final launch/demo flow;
- defense script uses the normal product flow;
- stale recommendations for the old detached Demo flow are removed or clearly marked historical;
- limitations and fallback/manual-check handling are explicit;
- `scripts/check.ps1` passes;
- `docs/CURRENT_STATE.md` points to the next real development task.

## Shared constraints

- Do not claim production readiness.
- Do not claim perfect recognition in uncontrolled conditions.
- Do not present the mock provider as real ML.
- Do not hide limitations.
- Do not add private photos, personal data, or biometric embeddings.
- Do not implement unrelated features while completing these documentation tasks.

## Context rule

Never load all six child tasks at once. Start a fresh agent context for each child task and stop after its handoff is written.