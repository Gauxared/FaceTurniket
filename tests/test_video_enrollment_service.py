"""Tests for video-based enrollment in web recognition service."""

import numpy as np

from src.web_api.services import RecognitionService


def test_enroll_user_video_creates_multiple_templates():
    service = RecognitionService(provider_name="mock")
    frames = [
        np.ones((80, 80, 3), dtype=np.uint8) * 160,
        np.ones((80, 80, 3), dtype=np.uint8) * 170,
        np.ones((80, 80, 3), dtype=np.uint8) * 180,
    ]

    result = service.enroll_user_video("video_enroll_user", frames, max_templates=3)

    assert result["success"] is True
    assert result["templates_created"] >= 1
    users = service.get_enrolled_users()
    user = next(u for u in users if u["user_id"] == "video_enroll_user")
    assert user["templates_count"] == result["templates_created"]


def test_enroll_user_video_no_acceptable_frames():
    service = RecognitionService(provider_name="mock")
    frames = ["low_quality_001.jpg", "low_quality_001.jpg"]

    result = service.enroll_user_video("video_enroll_fail", frames, max_templates=3)

    assert result["success"] is False
    assert result["templates_created"] == 0
    assert result["accepted_frames"] == 0
