from src.contracts.models import RecognitionResult
from src.face.providers.mock_provider import MockFaceRecognitionProvider
from src.face.recognition_pipeline import RecognitionPipeline


def test_pipeline_returns_recognition_result():
    provider = MockFaceRecognitionProvider()
    pipeline = RecognitionPipeline(provider)
    result = pipeline.process("user_001_good.jpg")
    assert isinstance(result, RecognitionResult)
    assert result.match.status == "matched"


def test_pipeline_delegates_to_provider():
    provider = MockFaceRecognitionProvider()
    pipeline = RecognitionPipeline(provider)
    result = pipeline.process("unknown_001.jpg")
    assert result.match.status == "not_found"


def test_pipeline_process_series_selects_best():
    provider = MockFaceRecognitionProvider()
    pipeline = RecognitionPipeline(provider)
    frames = ["low_quality_001.jpg", "user_001_good.jpg", "no_face_001.jpg"]
    selected, result = pipeline.process_series(frames)
    assert selected == "user_001_good.jpg"
    assert result.match.status == "matched"


def test_pipeline_process_series_no_acceptable():
    provider = MockFaceRecognitionProvider()
    pipeline = RecognitionPipeline(provider)
    frames = ["low_quality_001.jpg", "no_face_001.jpg"]
    selected, result = pipeline.process_series(frames)
    assert selected is None
    assert result is not None


def test_pipeline_last_selected_frame_property():
    provider = MockFaceRecognitionProvider()
    pipeline = RecognitionPipeline(provider)
    frames = ["user_001_good.jpg"]
    pipeline.process_series(frames)
    assert pipeline.last_selected_frame == "user_001_good.jpg"


def test_pipeline_last_selected_frame_none():
    provider = MockFaceRecognitionProvider()
    pipeline = RecognitionPipeline(provider)
    frames = ["low_quality_001.jpg"]
    pipeline.process_series(frames)
    assert pipeline.last_selected_frame is None
