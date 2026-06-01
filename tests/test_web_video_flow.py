"""Tests for real frame-based video flow in web recognition service."""

import numpy as np

from src.web_api.services import RecognitionService


def test_recognize_video_selects_real_best_frame():
    service = RecognitionService(provider_name="mock")
    frames = [
        np.zeros((64, 64, 3), dtype=np.uint8),
        np.ones((64, 64, 3), dtype=np.uint8) * 120,
        np.ones((64, 64, 3), dtype=np.uint8) * 200,
    ]

    frame_results, best_recognition, final_data = service.recognize_video(
        frames,
        max_frames=3,
        mode="1toN",
    )

    assert len(frame_results) == 3
    selected = [r for r in frame_results if r["selected"]]
    assert len(selected) == 1
    assert best_recognition is not None
    assert "decision" in final_data
    assert final_data["quality_score"] == best_recognition.quality.quality_score


def test_recognize_video_no_acceptable_frame_returns_decision():
    service = RecognitionService(provider_name="mock")
    frames = [
        "low_quality_001.jpg",
        "low_quality_001.jpg",
    ]

    frame_results, best_recognition, final_data = service.recognize_video(
        frames,
        max_frames=2,
        mode="1toN",
    )

    assert len(frame_results) == 2
    selected = [r for r in frame_results if r["selected"]]
    assert len(selected) == 1
    assert best_recognition is not None
    assert "decision" in final_data
    assert final_data["decision"].decision in {"retry", "deny"}
