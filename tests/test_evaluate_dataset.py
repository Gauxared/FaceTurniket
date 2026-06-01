"""Tests for dataset evaluation script (without real images)."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from scripts.evaluate_dataset import (
    EvalMetrics,
    evaluate_1to1_verification,
    evaluate_1toN_identification,
    run_evaluation,
    scan_dataset,
    select_images,
)
from src.contracts.models import MatchResult, QualityResult, RecognitionResult
from src.face.providers.mock_provider import MockFaceRecognitionProvider
from src.identity.matcher import IdentityMatcher
from src.identity.template_store import InMemoryTemplateStore


def _import_insightface():
    """Check if insightface is importable."""
    try:
        import insightface
        return True
    except ImportError:
        return False


class TestScanDataset:
    """Test dataset scanning on temporary structure."""

    def test_scan_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = scan_dataset(tmpdir)
            assert result == []

    def test_scan_persons_with_images(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create person directories with dummy image files
            os.makedirs(os.path.join(tmpdir, "Person A"))
            os.makedirs(os.path.join(tmpdir, "Person B"))
            open(os.path.join(tmpdir, "Person A", "001.jpg"), "w").close()
            open(os.path.join(tmpdir, "Person A", "002.png"), "w").close()
            open(os.path.join(tmpdir, "Person B", "001.jpg"), "w").close()

            result = scan_dataset(tmpdir)
            assert len(result) == 2
            names = [p.person_name for p in result]
            assert "Person A" in names
            assert "Person B" in names

            person_a = next(p for p in result if p.person_name == "Person A")
            assert len(person_a.images) == 2

    def test_scan_max_people(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(5):
                os.makedirs(os.path.join(tmpdir, f"Person{i}"))
                open(os.path.join(tmpdir, f"Person{i}", "001.jpg"), "w").close()

            result = scan_dataset(tmpdir, max_people=3)
            assert len(result) == 3


class TestSelectImages:
    """Test deterministic image splitting."""

    def test_select_images_basic(self):
        images = ["a.jpg", "b.jpg", "c.jpg", "d.jpg", "e.jpg"]
        enroll, probe = select_images(images, 2, 2)
        assert len(enroll) == 2
        assert len(probe) == 2

    def test_select_images_deterministic(self):
        images = ["a.jpg", "b.jpg", "c.jpg", "d.jpg"]
        enroll1, probe1 = select_images(images, 2, 1, seed=42)
        enroll2, probe2 = select_images(images, 2, 1, seed=42)
        assert enroll1 == enroll2
        assert probe1 == probe2

    def test_select_images_reuse(self):
        images = ["a.jpg", "b.jpg"]
        enroll, probe = select_images(images, 2, 2)
        assert len(enroll) == 2
        assert len(probe) == 2


class TestEval1to1:
    """Test 1:1 verification evaluation."""

    def test_positive_accept(self):
        provider = MockFaceRecognitionProvider()
        recognition = provider.recognize("user_001_good.jpg")
        
        store = InMemoryTemplateStore()
        from src.identity.enrollment import EnrollmentService, generate_mock_embedding
        from src.face.recognition_pipeline import RecognitionPipeline
        
        pipeline = RecognitionPipeline(provider)
        enrollment = EnrollmentService(pipeline, store)
        enrollment.enroll("user_001_good.jpg", user_id="user_001")
        
        matcher = IdentityMatcher(store, threshold=0.5)
        result, sim = evaluate_1to1_verification("test.jpg", "user_001", matcher, recognition)
        
        assert result in ("accept", "reject")
        assert 0 <= sim <= 1


class TestEval1toN:
    """Test 1:N identification evaluation."""

    def test_found_result(self):
        provider = MockFaceRecognitionProvider()
        recognition = provider.recognize("user_001_good.jpg")
        
        store = InMemoryTemplateStore()
        from src.identity.enrollment import EnrollmentService
        from src.face.recognition_pipeline import RecognitionPipeline
        
        pipeline = RecognitionPipeline(provider)
        enrollment = EnrollmentService(pipeline, store)
        enrollment.enroll("user_001_good.jpg", user_id="user_001")
        
        matcher = IdentityMatcher(store, threshold=0.5)
        result, matched_user, sim = evaluate_1toN_identification(
            "test.jpg", "user_001", matcher, recognition
        )
        
        assert result in ("found", "not_found", "ambiguous")


class TestMetrics:
    """Test metrics aggregation."""

    def test_metrics_defaults(self):
        m = EvalMetrics()
        assert m.total_people == 0
        assert m.enrolled_templates == 0

    def test_metrics_asdict(self):
        m = EvalMetrics(total_people=5, enrolled_templates=10)
        d = m.__dict__
        assert d["total_people"] == 5
        assert d["enrolled_templates"] == 10


class TestReportWriter:
    """Test JSON report writing."""

    def test_report_json_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = os.path.join(tmpdir, "test_report.json")
            
            report = {
                "dataset_path": "test",
                "metrics": {
                    "total_people": 2,
                    "enrolled_templates": 4,
                },
                "results": [],
            }
            
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            
            with open(report_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            
            assert loaded["dataset_path"] == "test"
            assert loaded["metrics"]["total_people"] == 2


class TestProviderPathLoading:
    """Test provider handles missing image paths gracefully."""

    @pytest.mark.skipif(
        not _import_insightface(),
        reason="InsightFace not installed",
    )
    def test_insightface_missing_file(self):
        from src.face.providers.insightface_provider import InsightFaceProvider
        provider = InsightFaceProvider()
        result = provider.recognize("nonexistent_file.jpg")
        
        assert result.face_detected is False
        assert "provider_error" in result.quality.reason or "file_not_found" in result.quality.reason

    def test_mock_provider_not_found_result(self):
        provider = MockFaceRecognitionProvider()
        result = provider.recognize("no_face.jpg")
        
        assert result.face_detected is False
        assert result.embedding is None
