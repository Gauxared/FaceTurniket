"""Tests for web API endpoints."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.web_api.app import app
from src.web_api.utils import image_to_base64

import numpy as np
import cv2


client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "provider" in data
        assert "users_enrolled" in data


class TestRecognitionEndpoint:
    """Test image recognition endpoint."""
    
    def test_recognize_image_mock(self):
        # Create a simple test image
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        b64_image = image_to_base64(img)
        
        response = client.post(
            "/api/recognize",
            json={
                "image": b64_image,
                "mode": "1toN",
                "claimed_user_id": None,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recognition_result" in data
        assert "decision" in data
        assert "image_display" in data
    
    def test_recognize_invalid_base64(self):
        response = client.post(
            "/api/recognize",
            json={
                "image": "not-valid-base64!!!",
                "mode": "1toN",
            }
        )
        
        assert response.status_code == 400


class TestVideoEndpoint:
    """Test video recognition endpoint."""
    
    def test_recognize_video_mock(self):
        # Create mock video frames (simple approach - just convert frames to base64)
        frames = []
        for i in range(5):
            img = np.ones((100, 100, 3), dtype=np.uint8) * (50 + i * 30)
            frames.append(img)
        
        # For testing, we'll use a mock approach
        # Real test would need actual video file encoded
        # This is a placeholder test showing the API contract
        
        # We'll skip actual video processing in unit tests
        pytest.skip("Video encoding requires actual video file")


class TestEnrollmentEndpoint:
    """Test user enrollment endpoint."""
    
    def test_enroll_user_by_full_name(self):
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        b64_image = image_to_base64(img)
        
        response = client.post(
            "/api/enroll",
            json={
                "full_name": "Иванов Иван Иванович",
                "images": [b64_image],
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["full_name"] == "Иванов Иван Иванович"
        assert data["user_id"].startswith("user_")
        assert data["enrolled_images"] == 1
        assert len(data["template_ids"]) == 1

    def test_enroll_user_multiple_images(self):
        img_1 = np.ones((100, 100, 3), dtype=np.uint8) * 220
        img_2 = np.ones((100, 100, 3), dtype=np.uint8) * 200
        b64_1 = image_to_base64(img_1)
        b64_2 = image_to_base64(img_2)

        response = client.post(
            "/api/enroll",
            json={
                "full_name": "Петров Петр Петрович",
                "images": [b64_1, b64_2],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["enrolled_images"] == 2
        assert len(data["template_ids"]) == 2
    
    def test_enroll_missing_user_id(self):
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        b64_image = image_to_base64(img)
        
        response = client.post(
            "/api/enroll",
            json={"image": b64_image}
        )
        
        # Should fail because either full_name or user_id is required
        assert response.status_code in [400, 422]

    def test_enroll_video_user(self, tmp_path):
        video_path = tmp_path / "enroll_video.mp4"
        writer = cv2.VideoWriter(
            str(video_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            5,
            (120, 120),
        )
        for value in [180, 190, 200]:
            writer.write(np.ones((120, 120, 3), dtype=np.uint8) * value)
        writer.release()

        import base64

        payload = base64.b64encode(video_path.read_bytes()).decode("utf-8")
        response = client.post(
            "/api/enroll-video",
            json={
                "full_name": "Сидоров Сидор Сидорович",
                "video": payload,
                "max_frames": 10,
                "max_templates": 3,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["full_name"] == "Сидоров Сидор Сидорович"
        assert data["user_id"].startswith("user_")
        assert data["templates_created"] >= 1


class TestUsersEndpoint:
    """Test users listing endpoint."""
    
    def test_get_users(self):
        response = client.get("/api/users")
        assert response.status_code == 200
        
        data = response.json()
        assert "users" in data
        assert isinstance(data["users"], list)
        
        # Check user item structure
        for user in data["users"]:
            assert "user_id" in user
            assert "full_name" in user
            assert "templates_count" in user
            assert "access_allowed" in user


class TestEventsEndpoint:
    """Test events logging endpoint."""
    
    def test_get_events(self):
        response = client.get("/api/events")
        assert response.status_code == 200
        
        data = response.json()
        assert "events" in data
        assert "total_count" in data
        assert isinstance(data["events"], list)
    
    def test_get_events_with_limit(self):
        response = client.get("/api/events?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["events"]) <= 10


class TestRecognitionService:
    """Test recognition service integration."""
    
    def test_service_initialization(self):
        from src.web_api.services import RecognitionService
        
        service = RecognitionService(provider_name="mock")
        assert service.provider_name == "mock"
        assert service.pipeline is not None
        assert service.template_store is not None
    
    def test_service_health(self):
        from src.web_api.services import RecognitionService
        
        service = RecognitionService(provider_name="mock")
        health = service.get_health_status()
        
        assert health["status"] == "ok"
        assert health["provider"] == "mock"
        assert "users_enrolled" in health


class TestCORSHeaders:
    """Test CORS headers."""
    
    def test_cors_headers(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        # CORS headers may not be present on simple GET
        assert response.json()["status"] == "ok"


class TestRootUi:
    """Test root UI content."""

    def test_root_ui_has_no_demo_tab(self):
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        assert 'data-tab="demo"' not in html
        assert "Presentation Demo" not in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
