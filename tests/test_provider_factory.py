"""Tests for ProviderFactory and real provider integration."""

import os
import pytest
from src.face.providers.factory import ProviderFactory
from src.face.providers.mock_provider import MockFaceRecognitionProvider


class TestProviderFactory:
    def test_default_returns_mock(self):
        # Ensure mock is default
        original = os.environ.get("FACE_PROVIDER")
        if "FACE_PROVIDER" in os.environ:
            del os.environ["FACE_PROVIDER"]

        provider = ProviderFactory.create()
        assert isinstance(provider, MockFaceRecognitionProvider)

        if original is not None:
            os.environ["FACE_PROVIDER"] = original

    def test_explicit_mock(self):
        provider = ProviderFactory.create(provider_name="mock")
        assert isinstance(provider, MockFaceRecognitionProvider)

    def test_insightface_when_available(self):
        try:
            provider = ProviderFactory.create(provider_name="insightface")
            # If we get here, InsightFace was imported successfully
            assert provider is not None
        except ImportError:
            # InsightFace not installed - this is expected in test env
            pytest.skip("InsightFace not installed, skipping real provider test")

    def test_invalid_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            ProviderFactory.create(provider_name="invalid")

    def test_env_variable_selection(self):
        original = os.environ.get("FACE_PROVIDER")
        os.environ["FACE_PROVIDER"] = "mock"

        provider = ProviderFactory.create()
        assert isinstance(provider, MockFaceRecognitionProvider)

        if original is not None:
            os.environ["FACE_PROVIDER"] = original
        else:
            del os.environ["FACE_PROVIDER"]

    def test_available_providers_includes_mock(self):
        providers = ProviderFactory.available_providers()
        assert "mock" in providers

    def test_available_providers_may_include_insightface(self):
        providers = ProviderFactory.available_providers()
        # mock should always be present
        assert "mock" in providers
        # insightface may or may not be present
        assert isinstance(providers, list)


class TestMockProviderStillWorks:
    """Ensure mock provider still works after factory addition."""

    def test_mock_recognition(self):
        provider = MockFaceRecognitionProvider()
        result = provider.recognize("user_001_good.jpg")
        assert result.face_detected is True
        assert result.match.status == "matched"
        assert result.match.user_id == "user_001"

    def test_mock_unknown_user(self):
        provider = MockFaceRecognitionProvider()
        result = provider.recognize("unknown_001.jpg")
        assert result.match.status == "not_found"

    def test_mock_multiple_faces(self):
        provider = MockFaceRecognitionProvider()
        result = provider.recognize("multiple_faces_001.jpg")
        assert result.faces_count == 3
        assert result.quality.is_acceptable is False


class TestIntegrationWithPipeline:
    def test_pipeline_with_factory_mock(self):
        from src.face.recognition_pipeline import RecognitionPipeline

        provider = ProviderFactory.create(provider_name="mock")
        pipeline = RecognitionPipeline(provider)
        result = pipeline.process("user_001_good.jpg")
        assert result.match.status == "matched"


class TestInsightFaceProviderSmoke:
    """Optional smoke test for InsightFace provider."""

    @pytest.fixture
    def insightface_available(self):
        try:
            import insightface  # noqa: F401
            return True
        except ImportError:
            return False

    @pytest.mark.skipif(
        not __import__("importlib").import_module("importlib.util").find_spec("insightface"),
        reason="InsightFace not installed",
    )
    def test_insightface_provider_creation(self):
        from src.face.providers.insightface_provider import InsightFaceProvider
        provider = InsightFaceProvider()
        assert provider is not None

    def test_insightface_provider_import_error_when_missing(self, insightface_available):
        if insightface_available:
            pytest.skip("InsightFace is installed, skip missing-dep test")
        with pytest.raises(ImportError, match="InsightFace is not installed"):
            from src.face.providers.insightface_provider import _import_insightface
            _import_insightface()