"""Tests for EnrollmentService."""

import pytest
from src.face.providers.mock_provider import MockFaceRecognitionProvider
from src.face.recognition_pipeline import RecognitionPipeline
from src.identity.enrollment import EnrollmentService, generate_mock_embedding
from src.identity.template_store import InMemoryTemplateStore


class TestGenerateMockEmbedding:
    def test_deterministic(self):
        e1 = generate_mock_embedding("user_001")
        e2 = generate_mock_embedding("user_001")
        assert e1 == e2

    def test_different_seeds_different_embeddings(self):
        e1 = generate_mock_embedding("user_001")
        e2 = generate_mock_embedding("user_002")
        assert e1 != e2

    def test_default_dimension(self):
        e = generate_mock_embedding("user_001")
        assert len(e) == 128

    def test_custom_dimension(self):
        e = generate_mock_embedding("user_001", dim=64)
        assert len(e) == 64

    def test_values_in_range(self):
        e = generate_mock_embedding("user_001")
        assert all(0.0 <= v <= 1.0 for v in e)


class TestEnrollmentService:
    @pytest.fixture
    def service(self):
        provider = MockFaceRecognitionProvider()
        pipeline = RecognitionPipeline(provider)
        store = InMemoryTemplateStore()
        return EnrollmentService(pipeline, store)

    def test_successful_enrollment(self, service):
        result = service.enroll("user_001_good.jpg", user_id="user_001")
        assert result.success is True
        assert result.user_id == "user_001"
        assert result.template_id is not None
        assert result.reason == "enrolled"

    def test_enrollment_adds_template_to_store(self, service):
        service.enroll("user_001_good.jpg", user_id="user_001")
        assert service.store.template_count() == 1
        templates = service.store.get_templates_for_user("user_001")
        assert len(templates) == 1

    def test_enrollment_face_not_detected(self, service):
        result = service.enroll("no_face_001.jpg", user_id="user_001")
        assert result.success is False
        assert result.reason == "face_not_detected"

    def test_enrollment_low_quality(self, service):
        result = service.enroll("low_quality_001.jpg", user_id="user_001")
        assert result.success is False
        assert result.reason.startswith("quality_not_acceptable")

    def test_enrollment_spoof(self, service):
        result = service.enroll("spoof_001.jpg", user_id="user_001")
        assert result.success is False
        assert result.reason.startswith("liveness_failed")

    def test_multiple_enrollments_same_user(self, service):
        result1 = service.enroll("user_001_good.jpg", user_id="user_001")
        result2 = service.enroll("user_001_good.jpg", user_id="user_001")
        assert result1.success is True
        assert result2.success is True
        assert result1.template_id != result2.template_id
        assert service.store.template_count() == 2

    def test_enrollment_source_image_id(self, service):
        service.enroll("user_001_good.jpg", user_id="user_001")
        template = service.store.get_templates_for_user("user_001")[0]
        assert template.source_image_id == "user_001_good.jpg"
