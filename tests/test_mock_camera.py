"""Tests for MockCamera."""

import pytest
from src.camera.mock_camera import MockCamera


class TestMockCamera:
    """Test MockCamera deterministic behavior."""

    def test_camera_id_defaults(self):
        camera = MockCamera()
        assert camera.camera_id == "mock_001"

    def test_camera_id_custom(self):
        camera = MockCamera(camera_id="cam_42")
        assert camera.camera_id == "cam_42"

    def test_known_user_good_scenario(self):
        camera = MockCamera()
        frames = camera.capture_series("known_user_good")
        assert frames == ["user_001_good.jpg"]

    def test_known_user_with_noise_scenario(self):
        camera = MockCamera()
        frames = camera.capture_series("known_user_with_noise")
        assert len(frames) == 3
        assert "user_001_good.jpg" in frames

    def test_no_acceptable_scenario(self):
        camera = MockCamera()
        frames = camera.capture_series("no_acceptable")
        assert len(frames) == 2
        assert "no_face_001.jpg" in frames
        assert "multiple_faces_002.jpg" in frames

    def test_all_low_quality_scenario(self):
        camera = MockCamera()
        frames = camera.capture_series("all_low_quality")
        assert len(frames) == 2
        assert all("low_quality" in f for f in frames)

    def test_unknown_user_scenario(self):
        camera = MockCamera()
        frames = camera.capture_series("unknown_user")
        assert frames == ["unknown_001.jpg"]

    def test_spoof_attempt_scenario(self):
        camera = MockCamera()
        frames = camera.capture_series("spoof_attempt")
        assert frames == ["spoof_001.jpg"]

    def test_mixed_quality_ambiguous_scenario(self):
        camera = MockCamera()
        frames = camera.capture_series("mixed_quality_ambiguous")
        assert len(frames) == 3
        assert "user_001_ambiguous.jpg" in frames

    def test_multiple_bad_one_good_scenario(self):
        camera = MockCamera()
        frames = camera.capture_series("multiple_bad_one_good")
        assert len(frames) == 5
        assert "user_002_good.jpg" in frames

    def test_unknown_scenario_returns_default(self):
        camera = MockCamera()
        frames = camera.capture_series("nonexistent_scenario")
        assert frames == ["unknown_001.jpg"]

    def test_deterministic_same_scenario(self):
        camera = MockCamera()
        frames1 = camera.capture_series("known_user_with_noise")
        frames2 = camera.capture_series("known_user_with_noise")
        assert frames1 == frames2
