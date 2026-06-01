# Prompts for Delegated Task Execution

This directory contains ready-to-use prompts for another executor agent.

Recommended order:

1. Give the executor `000_executor_system_prompt.md` as the shared context.
2. Give exactly one task prompt, for example
   `001_project_skeleton_prompt.md`.
3. Review the diff and command output after the task is done.
4. Give the next task only after the previous task passes checks.

Do not give several task prompts at once if you want small controlled
iterations.

Current extra prompts:

- `009_dataset_evaluation_prompt.md` - local InsightFace evaluation on
  `D:\Download\Celebrity Faces Dataset` without training or committing photos.
- `010_presentation_demo_mode_prompt.md` - reliable demo mode for diploma
  presentation with local assets, demo report, and web/API support.
