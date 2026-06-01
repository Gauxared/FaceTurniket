# Task 012 - Video Flow Fix

## Goal

Fix real video processing so the system evaluates actual video frames, not
placeholder string frame IDs.

Video is important because the diploma presentation can show a realistic
controlled-capture flow:

```text
short video -> frames -> quality gate -> best frame -> matching -> decision
```

## Current Problem

In `src/web_api/services.py`, `recognize_video()` currently builds:

```python
frame_ids = [str(i) for i in range(len(frames[:max_frames]))]
selected_frame_id, best_recognition = self.pipeline.process_series(frame_ids)
```

This means the quality gate is not evaluating the real video frames. It is
evaluating strings such as `"0"`, `"1"`, `"2"`.

## Required

1. Change video processing so every frame passed to the provider is a real
   numpy image frame.

2. Select the best frame using actual recognition results.

3. The selected frame must be the same frame used for:

- final recognition result;
- identity matching;
- access decision;
- event log;
- turnstile command.

4. Support both modes if currently exposed:

- `1:N identification`;
- `1:1 verification` with `claimed_user_id`.

5. Return useful per-frame data:

- frame index;
- selected flag;
- face detected;
- faces count;
- quality score;
- blur score;
- brightness score;
- reason;
- optional match status/similarity if computed.

6. Keep the existing API response shape compatible where possible.

## Suggested Design

Do not use `RecognitionPipeline.process_series()` for web video until it can
accept real frames directly.

Instead, in `RecognitionService.recognize_video()`:

1. Iterate over decoded frames.
2. Run `self.pipeline.process(frame)` for each frame.
3. Reject unacceptable frames using the same quality criteria as `QualityGate`.
4. Pick the acceptable frame with the highest quality score.
5. Run identity matching on the selected frame.
6. Run access decision.
7. Log event and turnstile command.

If no frame is acceptable, select the best rejected frame and return a
`retry`/`deny` decision according to existing rules.

## Forbidden

- Do not use fake frame IDs for real video processing.
- Do not hard-code decisions.
- Do not move access rules into the ML provider.
- Do not make InsightFace mandatory for normal tests.
- Do not break mock provider or harness.

## Tests

Add or update tests for:

- video processing uses actual frames;
- selected frame is marked in frame results;
- final decision is based on selected frame;
- no acceptable frames produces retry/deny without crashing;
- mock provider tests remain deterministic.

Use generated temporary video/images in tests. Do not require private local
photos.

## Done Criteria

- `/api/recognize-video` processes actual frames.
- The best-frame result is consistent with returned timeline/table.
- `scripts/check.ps1` passes.
- `docs/CURRENT_STATE.md` is updated.

