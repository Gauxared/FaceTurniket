import pytest

from src.face.providers.mock_provider import MockFaceRecognitionProvider


@pytest.fixture
def provider():
    return MockFaceRecognitionProvider()


def test_provider_interface_shape(provider):
    """Provider must have recognize method."""
    assert hasattr(provider, "recognize")
    assert callable(provider.recognize)


def test_user_001_good_matched(provider):
    result = provider.recognize("user_001_good.jpg")
    assert result.face_detected is True
    assert result.faces_count == 1
    assert result.quality.is_acceptable is True
    assert result.liveness.is_live is True
    assert result.match.status == "matched"
    assert result.match.user_id == "user_001"
    assert result.match.similarity == 0.87


def test_unknown_user_not_found(provider):
    result = provider.recognize("unknown_001.jpg")
    assert result.face_detected is True
    assert result.match.status == "not_found"
    assert result.match.user_id is None


def test_low_quality_bad_quality(provider):
    result = provider.recognize("low_quality_001.jpg")
    assert result.quality.is_acceptable is False
    assert result.match.status == "skipped_due_to_quality"


def test_multiple_faces_detected(provider):
    result = provider.recognize("multiple_faces_001.jpg")
    assert result.faces_count > 1
    assert result.quality.is_acceptable is False
    assert result.match.status == "skipped_due_to_quality"


def test_spoof_liveness_failed(provider):
    result = provider.recognize("spoof_001.jpg")
    assert result.liveness.is_live is False
    assert result.match.status == "not_found"


def test_unknown_filename_safe_fallback(provider):
    result = provider.recognize("random_file_xyz.png")
    assert result.face_detected is False
    assert result.faces_count == 0
    assert result.quality.is_acceptable is False
    assert result.match.status == "not_found"


def test_object_with_name_attribute(provider):
    class FakeImage:
        name = "user_042_good.png"

    result = provider.recognize(FakeImage())
    assert result.match.status == "matched"
    assert result.match.user_id == "user_042"


def test_numpy_array_face_detected(provider):
    """Numpy arrays should return face_detected=True with deterministic embedding."""
    import numpy as np

    img = np.ones((100, 100, 3), dtype=np.uint8) * 128
    result = provider.recognize(img)
    assert result.face_detected is True
    assert result.faces_count == 1
    assert result.quality.is_acceptable is True
    assert result.liveness.is_live is True
    assert result.embedding is not None
    assert len(result.embedding) == 128


def test_numpy_array_deterministic_embedding(provider):
    """Same numpy array should produce same embedding."""
    import numpy as np

    img = np.ones((64, 64, 3), dtype=np.uint8) * 200
    r1 = provider.recognize(img)
    r2 = provider.recognize(img)
    assert r1.embedding == r2.embedding


def test_numpy_array_different_images_different_embeddings(provider):
    """Different numpy arrays should produce different embeddings."""
    import numpy as np

    img1 = np.ones((64, 64, 3), dtype=np.uint8) * 100
    img2 = np.ones((64, 64, 3), dtype=np.uint8) * 200
    r1 = provider.recognize(img1)
    r2 = provider.recognize(img2)
    assert r1.embedding != r2.embedding
