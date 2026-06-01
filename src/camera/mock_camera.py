"""Mock camera that produces deterministic frame sequences."""

from typing import List


class MockCamera:
    """
    Deterministic mock camera for testing capture flow.

    Instead of capturing from a real camera, this returns predefined
    sequences of frame descriptors (filenames or fixture paths) based
    on the scenario name.
    """

    def __init__(self, camera_id: str = "mock_001"):
        self.camera_id = camera_id

    def capture_series(self, scenario: str) -> List[str]:
        """
        Return a deterministic sequence of frame identifiers for a scenario.

        Each scenario returns a list of frame descriptors (filenames).
        The RecognitionPipeline or QualityGate will process these frames
        and select the best acceptable one.

        Scenarios:
        - "known_user_good" -> single good frame
        - "known_user_with_noise" -> good frame surrounded by bad frames
        - "no_acceptable" -> all frames bad (no face, multiple faces, etc.)
        - "all_low_quality" -> all frames low quality
        - "unknown_user" -> single unknown frame
        - "spoof_attempt" -> spoof frame
        - "mixed_quality_ambiguous" -> mix leading to ambiguous match
        """
        scenarios = {
            "known_user_good": ["user_001_good.jpg"],
            "known_user_with_noise": [
                "low_quality_001.jpg",
                "user_001_good.jpg",
                "low_quality_002.jpg",
            ],
            "no_acceptable": ["no_face_001.jpg", "multiple_faces_002.jpg"],
            "all_low_quality": ["low_quality_001.jpg", "low_quality_002.jpg"],
            "unknown_user": ["unknown_001.jpg"],
            "spoof_attempt": ["spoof_001.jpg"],
            "mixed_quality_ambiguous": [
                "low_quality_001.jpg",
                "user_001_ambiguous.jpg",
                "low_quality_002.jpg",
            ],
            "multiple_bad_one_good": [
                "low_quality_001.jpg",
                "no_face_001.jpg",
                "user_002_good.jpg",
                "spoof_001.jpg",
                "low_quality_002.jpg",
            ],
        }

        return scenarios.get(scenario, ["unknown_001.jpg"])
