# Demo Mode

This folder describes a safe local presentation setup for the diploma demo.

The repository contains only the example config. Place personal or locally
prepared demo files outside git in:

```text
demo/local/
```

Suggested structure:

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

Use `demo/config.example.json` as the starting point and copy it to
`demo/local/config.json`.

The paths inside `config.json` should be relative to `demo/local/`, for
example `allowed_user/pass_photo.jpg`.

The demo is meant for a live diploma presentation:

- allowed user photo should open the mock turnstile;
- denied or unknown photo should keep it closed;
- optional video should show frame selection and the final decision;
- the demo report should be saved to `reports/demo_report.json`.
