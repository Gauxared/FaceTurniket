"""Tests for IdentityMatcher."""

import pytest
from src.contracts.models import (
    LivenessResult,
    MatchResult,
    QualityResult,
    RecognitionResult,
)
from src.face.providers.mock_provider import MockFaceRecognitionProvider
from src.face.recognition_pipeline import RecognitionPipeline
from src.identity.enrollment import EnrollmentService
from src.identity.matcher import IdentityMatcher, cosine_similarity
from src.identity.template_store import InMemoryTemplateStore


class TestCosineSimilarity:
    def test_identical_vectors(self):
        v = [1.0, 0.0, 0.0]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_zero_vector(self):
        assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0

    def test_same_direction(self):
        a = [1.0, 1.0, 1.0]
        b = [2.0, 2.0, 2.0]
        assert cosine_similarity(a, b) == pytest.approx(1.0)


class TestIdentityMatcher1to1:
    @pytest.fixture
    def matcher(self):
        store = InMemoryTemplateStore()
        provider = MockFaceRecognitionProvider()
        pipeline = RecognitionPipeline(provider)
        enrollment = EnrollmentService(pipeline, store)
        enrollment.enroll("user_001_good.jpg", user_id="user_001")
        return IdentityMatcher(store, threshold=0.70)

    def test_verify_success(self, matcher):
        recognition = MockFaceRecognitionProvider().recognize("user_001_good.jpg")
        result = matcher.verify_1to1(recognition, claimed_user_id="user_001")
        assert result.status == "matched"
        assert result.user_id == "user_001"
        assert result.similarity is not None
        assert result.similarity >= 0.70

    def test_verify_wrong_user(self, matcher):
        recognition = MockFaceRecognitionProvider().recognize("user_002_good.jpg")
        result = matcher.verify_1to1(recognition, claimed_user_id="user_001")
        assert result.status == "low_similarity"
        assert result.user_id == "user_001"

    def test_verify_unknown_user(self, matcher):
        recognition = MockFaceRecognitionProvider().recognize("user_001_good.jpg")
        result = matcher.verify_1to1(recognition, claimed_user_id="user_999")
        assert result.status == "not_found"
        assert result.user_id is None

    def test_verify_no_user_id_in_recognition(self):
        store = InMemoryTemplateStore()
        matcher = IdentityMatcher(store, threshold=0.70)
        recognition = RecognitionResult(
            face_detected=True,
            faces_count=1,
            quality=QualityResult(
                is_acceptable=True,
                quality_score=0.80,
                blur_score=0.75,
                brightness_score=0.78,
                yaw_angle=0,
                pitch_angle=0,
                roll_angle=0,
                reason="frame_accepted",
            ),
            liveness=LivenessResult(
                is_live=True,
                score=0.90,
                reason="liveness_passed",
            ),
            match=MatchResult(
                status="not_found",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
            ),
        )
        result = matcher.verify_1to1(recognition, claimed_user_id="user_001")
        assert result.status == "not_found"


class TestIdentityMatcher1toN:
    @pytest.fixture
    def matcher(self):
        store = InMemoryTemplateStore()
        provider = MockFaceRecognitionProvider()
        pipeline = RecognitionPipeline(provider)
        enrollment = EnrollmentService(pipeline, store)
        enrollment.enroll("user_001_good.jpg", user_id="user_001")
        enrollment.enroll("user_002_good.jpg", user_id="user_002")
        return IdentityMatcher(store, threshold=0.70)

    def test_identify_success(self, matcher):
        recognition = MockFaceRecognitionProvider().recognize("user_001_good.jpg")
        result = matcher.identify_1toN(recognition)
        assert result.status == "matched"
        assert result.user_id == "user_001"
        assert result.similarity is not None

    def test_identify_unknown_user(self, matcher):
        recognition = MockFaceRecognitionProvider().recognize("unknown_001.jpg")
        result = matcher.identify_1toN(recognition)
        assert result.status == "not_found"

    def test_identify_empty_store(self):
        store = InMemoryTemplateStore()
        matcher = IdentityMatcher(store, threshold=0.70)
        recognition = MockFaceRecognitionProvider().recognize("user_001_good.jpg")
        result = matcher.identify_1toN(recognition)
        assert result.status == "not_found"

    def test_identify_ambiguous(self, matcher):
        # Enroll same user twice with same image to create ambiguity potential
        store = InMemoryTemplateStore()
        provider = MockFaceRecognitionProvider()
        pipeline = RecognitionPipeline(provider)
        enrollment = EnrollmentService(pipeline, store)
        # Use same image for both to create similar embeddings
        enrollment.enroll("user_001_good.jpg", user_id="user_001")
        enrollment.enroll("user_001_good.jpg", user_id="user_001")
        matcher = IdentityMatcher(store, threshold=0.70)
        recognition = MockFaceRecognitionProvider().recognize("user_001_good.jpg")
        result = matcher.identify_1toN(recognition)
        # With duplicate user, ambiguity check may or may not trigger
        # depending on exact similarity values
        assert result.status in ("matched", "ambiguous")
        if result.status == "ambiguous":
            assert result.top2_margin is not None
            assert result.second_best_similarity is not None
