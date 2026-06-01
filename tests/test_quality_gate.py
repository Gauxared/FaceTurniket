"""Tests for QualityGate."""

import pytest
from src.face.providers.mock_provider import MockFaceRecognitionProvider
from src.face.quality_gate import QualityGate


class TestQualityGate:
    """Test QualityGate frame selection."""

    @pytest.fixture
    def provider(self):
        return MockFaceRecognitionProvider()

    @pytest.fixture
    def quality_gate(self, provider):
        return QualityGate(provider)

    def test_single_acceptable_frame(self, quality_gate):
        frames = ["user_001_good.jpg"]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected == "user_001_good.jpg"
        assert result.match.status == "matched"
        assert result.quality.is_acceptable is True

    def test_best_frame_selected_from_series(self, quality_gate):
        frames = ["low_quality_001.jpg", "user_001_good.jpg", "unknown_001.jpg"]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected == "user_001_good.jpg"
        assert result.match.user_id == "user_001"

    def test_no_acceptable_frames_returns_none(self, quality_gate):
        frames = ["no_face_001.jpg", "multiple_faces_002.jpg"]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected is None
        assert result is not None

    def test_all_low_quality_returns_none(self, quality_gate):
        frames = ["low_quality_001.jpg", "low_quality_002.jpg"]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected is None
        assert result.quality.is_acceptable is False

    def test_spoof_rejected(self, quality_gate):
        frames = ["spoof_001.jpg"]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected is None
        assert result.liveness.is_live is False

    def test_multiple_bad_one_good(self, quality_gate):
        frames = [
            "low_quality_001.jpg",
            "no_face_001.jpg",
            "user_002_good.jpg",
            "spoof_001.jpg",
            "low_quality_002.jpg",
        ]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected == "user_002_good.jpg"
        assert result.match.user_id == "user_002"

    def test_best_rejected_has_highest_quality(self, quality_gate):
        frames = ["no_face_001.jpg", "multiple_faces_002.jpg"]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected is None
        assert result.quality.quality_score > 0.0

    def test_empty_frames_raises(self, quality_gate):
        with pytest.raises(ValueError, match="must not be empty"):
            quality_gate.evaluate_series([])

    def test_quality_score_comparison(self, quality_gate):
        frames = ["user_001_good.jpg", "user_002_good.jpg"]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected is not None
        assert selected in ["user_001_good.jpg", "user_002_good.jpg"]

    def test_liveness_failed_frame_rejected(self, quality_gate):
        frames = ["spoof_001.jpg", "user_001_good.jpg"]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected == "user_001_good.jpg"

    def test_multiple_faces_rejected(self, quality_gate):
        frames = ["multiple_faces_001.jpg", "user_001_good.jpg"]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected == "user_001_good.jpg"

    def test_no_face_rejected(self, quality_gate):
        frames = ["no_face_001.jpg", "user_001_good.jpg"]
        selected, result = quality_gate.evaluate_series(frames)
        assert selected == "user_001_good.jpg"
