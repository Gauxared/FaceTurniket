# Task 013 - Video Enrollment

## Goal

Add enrollment from a short video or frame series.

This is the strongest practical improvement for the face-only access scenario.
Instead of relying on one enrollment photo, the system should extract several
good templates from a controlled video, similar in spirit to Face ID setup:

```text
short enrollment video
-> extract frames
-> filter bad frames
-> keep diverse high-quality frames
-> create multiple face templates
```

## Business Reason

The practice report positions the system as biometric identification for access
control. If the system is expected to work without cards, single-photo
enrollment is too fragile. Video enrollment gives the system multiple reference
templates for small changes in pose, lighting, expression, glasses, hairstyle,
and camera angle.

## Required

1. Add backend support for enrollment from video.

Suggested endpoint:

```text
POST /api/enroll-video
```

Request fields:

- `user_id`;
- base64 video;
- optional `max_frames`;
- optional `max_templates`.

2. Extract frames from video using existing utilities.

3. Run provider recognition on frames.

4. Keep only frames that pass:

- one face detected;
- acceptable quality;
- liveness not failed;
- embedding exists or mock fallback is available.

5. Select up to `max_templates` best frames.

Minimum selection:

- sort by quality score descending;
- avoid exact duplicate embeddings when possible.

Better selection if easy:

- include simple diversity by choosing frames with different similarity/pose.

6. Save multiple templates for the user.

7. Add the user to access policy as allowed after successful enrollment.

8. Return:

- success flag;
- user id;
- number of frames processed;
- number of accepted frames;
- number of templates created;
- rejected frame reasons;
- template ids.

9. Add UI support in Enrollment tab:

- keep photo enrollment;
- add video enrollment upload;
- show count of templates created.

## Forbidden

- Do not store video files in the repository.
- Do not store raw real photos in the repository.
- Do not store raw embeddings in reports/logs.
- Do not train a model.
- Do not use gender, age, race, emotion, or similar attributes.
- Do not make InsightFace mandatory for normal tests.

## Tests

Add tests for:

- video enrollment endpoint with generated test video;
- multiple templates created;
- no acceptable frames returns a clear failure;
- user appears in users list after enrollment;
- existing photo enrollment still works.

## Done Criteria

- User can be enrolled from a short video.
- Multiple templates are created for that user.
- Web UI exposes video enrollment clearly.
- `scripts/check.ps1` passes.
- `docs/CURRENT_STATE.md` and web docs are updated.

