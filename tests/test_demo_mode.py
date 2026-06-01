"""Tests for presentation demo mode."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

from src.demo.config import load_demo_config, validate_demo_config
from src.demo.runner import DemoRunner, save_demo_report


def _write_image(path: Path, value: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = np.ones((120, 120, 3), dtype=np.uint8) * value
    cv2.imwrite(str(path), image)


def _write_video(path: Path, frame_values: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        5,
        (120, 120),
    )
    try:
        for value in frame_values:
            frame = np.ones((120, 120, 3), dtype=np.uint8) * value
            writer.write(frame)
    finally:
        writer.release()


def test_demo_config_loading_and_validation(tmp_path):
    config_dir = tmp_path / "demo" / "local"
    config_dir.mkdir(parents=True)
    _write_image(config_dir / "allowed_user" / "enroll_01.jpg", 180)
    _write_image(config_dir / "allowed_user" / "enroll_02.jpg", 180)
    _write_image(config_dir / "allowed_user" / "pass_photo.jpg", 180)

    config_path = config_dir / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "provider": "mock",
                "thresholds": {
                    "verification_threshold": 0.5,
                    "identification_threshold": 0.5,
                    "quality_threshold": 0.5,
                },
                "demo_user": {
                    "user_id": "demo_user_001",
                    "display_name": "Demo Presenter",
                    "access_allowed": True,
                    "enroll_images": [
                        "allowed_user/enroll_01.jpg",
                        "allowed_user/enroll_02.jpg",
                    ],
                    "pass_photo": "allowed_user/pass_photo.jpg",
                    "denied_photo": "denied_user/unknown_photo.jpg",
                    "low_quality_photo": "low_quality/bad_photo.jpg",
                },
            }
        ),
        encoding="utf-8",
    )

    config = load_demo_config(config_path)
    errors = validate_demo_config(config)

    assert config.provider == "mock"
    assert config.demo_user.user_id == "demo_user_001"
    assert len(config.demo_user.enroll_images) == 2
    assert errors == []


def test_demo_runner_produces_report(tmp_path):
    config_dir = tmp_path / "demo" / "local"
    config_dir.mkdir(parents=True)
    allowed_dir = config_dir / "allowed_user"
    denied_dir = config_dir / "denied_user"
    low_quality_dir = config_dir / "low_quality"

    _write_image(allowed_dir / "enroll_01.jpg", 180)
    _write_image(allowed_dir / "enroll_02.jpg", 180)
    _write_image(allowed_dir / "pass_photo.jpg", 180)
    _write_video(allowed_dir / "pass_video.mp4", [120, 150, 180])
    _write_image(denied_dir / "unknown_photo.jpg", 30)
    _write_image(low_quality_dir / "bad_photo.jpg", 90)

    config_path = config_dir / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "provider": "mock",
                "thresholds": {
                    "verification_threshold": 0.5,
                    "identification_threshold": 0.5,
                    "quality_threshold": 0.5,
                },
                "demo_user": {
                    "user_id": "demo_user_001",
                    "display_name": "Demo Presenter",
                    "access_allowed": True,
                    "enroll_images": [
                        "allowed_user/enroll_01.jpg",
                        "allowed_user/enroll_02.jpg",
                    ],
                    "pass_photo": "allowed_user/pass_photo.jpg",
                    "pass_video": "allowed_user/pass_video.mp4",
                    "denied_photo": "denied_user/unknown_photo.jpg",
                    "low_quality_photo": "low_quality/bad_photo.jpg",
                },
            }
        ),
        encoding="utf-8",
    )

    runner = DemoRunner(load_demo_config(config_path))
    report = runner.run()

    assert report["provider"] == "mock"
    assert report["demo_user"]["user_id"] == "demo_user_001"
    assert report["positive_photo"]["decision"]["decision"] == "allow"
    assert report["positive_photo"]["turnstile_command"]["command"] == "open"
    assert report["unknown_photo"]["decision"]["decision"] in {"deny", "retry", "allow"}
    assert report["low_quality_photo"]["decision"]["decision"] in {"retry", "deny"}
    assert report["video_result"] is not None

    report_path = save_demo_report(report, tmp_path / "demo_report.json")
    assert report_path.exists()


def test_demo_report_writer(tmp_path):
    report = {"success": True, "provider": "mock"}
    report_path = save_demo_report(report, tmp_path / "reports" / "demo_report.json")
    loaded = json.loads(report_path.read_text(encoding="utf-8"))
    assert loaded["success"] is True
    assert loaded["provider"] == "mock"
