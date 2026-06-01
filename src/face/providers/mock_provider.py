import hashlib
from typing import Any, List, Optional

import numpy as np

from src.contracts.models import (
    LivenessResult,
    MatchResult,
    QualityResult,
    RecognitionResult,
)
from src.face.providers.base import FaceRecognitionProvider


class MockFaceRecognitionProvider(FaceRecognitionProvider):
    """
    Deterministic mock provider that returns RecognitionResult based on filename
    or image content hash.

    Expected filename patterns:
    - user_<id>_good.<ext>    -> matched user_<id>
    - unknown_<id>.<ext>      -> not_found
    - low_quality_<id>.<ext>  -> bad quality
    - multiple_faces_<id>.<ext> -> multiple faces
    - spoof_<id>.<ext>        -> liveness failed
    - anything else (including numpy arrays) -> face detected with hash-based
      deterministic embedding for enrollment/recognition from web UI.
    """

    def recognize(self, image: Any) -> RecognitionResult:
        filename = self._extract_filename(image)

        # For numpy arrays (from web UI), compute a deterministic embedding
        # from image content so the same person gets consistent embeddings.
        if isinstance(image, np.ndarray):
            return self._resolve_by_array(image)

        return self._resolve_by_filename(filename)

    @staticmethod
    def _extract_filename(image: Any) -> str:
        if isinstance(image, str):
            return image
        if hasattr(image, "name"):
            return image.name
        return ""

    @staticmethod
    def _image_hash(image: np.ndarray) -> str:
        """Compute a deterministic hash from image pixels."""
        data = image.tobytes()
        return hashlib.md5(data).hexdigest()

    def _resolve_by_filename(self, filename: str) -> RecognitionResult:
        name = filename.lower().strip()

        if "multiple_faces" in name:
            return self._multiple_faces_result()

        if "low_quality" in name:
            return self._low_quality_result()

        if "spoof" in name:
            return self._spoof_result()

        if name.startswith("user_") and "_good" in name:
            user_id = self._extract_user_id(name)
            return self._matched_result(user_id)

        if name.startswith("user_") and "_low_sim" in name:
            user_id = self._extract_user_id(name)
            return self._low_similarity_result(user_id)

        if name.startswith("user_") and "_ambiguous" in name:
            user_id = self._extract_user_id(name)
            return self._ambiguous_result(user_id)

        if name.startswith("unknown_"):
            return self._not_found_result()

        return self._safe_fallback_result()

    @staticmethod
    def _extract_user_id(filename: str) -> str:
        # user_001_good.jpg -> user_001
        parts = filename.split("_")
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}"
        return "user_unknown"

    @staticmethod
    def _matched_result(user_id: str) -> RecognitionResult:
        return RecognitionResult(
            face_detected=True,
            faces_count=1,
            quality=QualityResult(
                is_acceptable=True,
                quality_score=0.88,
                blur_score=0.82,
                brightness_score=0.76,
                yaw_angle=8,
                pitch_angle=-5,
                roll_angle=2,
                reason="frame_accepted",
            ),
            liveness=LivenessResult(
                is_live=True,
                score=0.91,
                reason="liveness_passed",
            ),
            match=MatchResult(
                status="matched",
                user_id=user_id,
                similarity=0.87,
                is_ambiguous=False,
            ),
            embedding=None,
        )

    @staticmethod
    def _not_found_result() -> RecognitionResult:
        return RecognitionResult(
            face_detected=True,
            faces_count=1,
            quality=QualityResult(
                is_acceptable=True,
                quality_score=0.75,
                blur_score=0.70,
                brightness_score=0.72,
                yaw_angle=10,
                pitch_angle=-3,
                roll_angle=1,
                reason="frame_accepted",
            ),
            liveness=LivenessResult(
                is_live=True,
                score=0.85,
                reason="liveness_passed",
            ),
            match=MatchResult(
                status="not_found",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
            ),
            embedding=None,
        )

    @staticmethod
    def _low_quality_result() -> RecognitionResult:
        return RecognitionResult(
            face_detected=True,
            faces_count=1,
            quality=QualityResult(
                is_acceptable=False,
                quality_score=0.35,
                blur_score=0.20,
                brightness_score=0.40,
                yaw_angle=25,
                pitch_angle=15,
                roll_angle=5,
                reason="frame_too_blurry_and_poor_lighting",
            ),
            liveness=LivenessResult(
                is_live=True,
                score=0.60,
                reason="liveness_passed",
            ),
            match=MatchResult(
                status="skipped_due_to_quality",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
            ),
            embedding=None,
        )

    @staticmethod
    def _multiple_faces_result() -> RecognitionResult:
        return RecognitionResult(
            face_detected=True,
            faces_count=3,
            quality=QualityResult(
                is_acceptable=False,
                quality_score=0.50,
                blur_score=0.65,
                brightness_score=0.70,
                yaw_angle=5,
                pitch_angle=0,
                roll_angle=2,
                reason="multiple_faces_detected",
            ),
            liveness=LivenessResult(
                is_live=True,
                score=0.80,
                reason="liveness_passed",
            ),
            match=MatchResult(
                status="skipped_due_to_quality",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
            ),
            embedding=None,
        )

    @staticmethod
    def _spoof_result() -> RecognitionResult:
        return RecognitionResult(
            face_detected=True,
            faces_count=1,
            quality=QualityResult(
                is_acceptable=True,
                quality_score=0.80,
                blur_score=0.75,
                brightness_score=0.78,
                yaw_angle=3,
                pitch_angle=-2,
                roll_angle=1,
                reason="frame_accepted",
            ),
            liveness=LivenessResult(
                is_live=False,
                score=0.25,
                reason="liveness_failed_spoof_detected",
            ),
            match=MatchResult(
                status="not_found",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
            ),
            embedding=None,
        )

    @staticmethod
    def _low_similarity_result(user_id: str) -> RecognitionResult:
        return RecognitionResult(
            face_detected=True,
            faces_count=1,
            quality=QualityResult(
                is_acceptable=True,
                quality_score=0.75,
                blur_score=0.70,
                brightness_score=0.72,
                yaw_angle=10,
                pitch_angle=-3,
                roll_angle=1,
                reason="frame_accepted",
            ),
            liveness=LivenessResult(
                is_live=True,
                score=0.85,
                reason="liveness_passed",
            ),
            match=MatchResult(
                status="matched",
                user_id=user_id,
                similarity=0.55,
                is_ambiguous=False,
            ),
            embedding=None,
        )

    @staticmethod
    def _ambiguous_result(user_id: str) -> RecognitionResult:
        return RecognitionResult(
            face_detected=True,
            faces_count=1,
            quality=QualityResult(
                is_acceptable=True,
                quality_score=0.80,
                blur_score=0.75,
                brightness_score=0.78,
                yaw_angle=3,
                pitch_angle=-2,
                roll_angle=1,
                reason="frame_accepted",
            ),
            liveness=LivenessResult(
                is_live=True,
                score=0.88,
                reason="liveness_passed",
            ),
            match=MatchResult(
                status="ambiguous",
                user_id=user_id,
                similarity=0.82,
                is_ambiguous=True,
            ),
            embedding=None,
        )

    def _resolve_by_array(self, image: np.ndarray) -> RecognitionResult:
        """Handle numpy array images (from web UI, camera, etc)."""
        img_hash = self._image_hash(image)

        # For any non-empty image, return face_detected=True with deterministic embedding
        # This allows web UI enrollment/recognition to work without real face detection
        embedding = self._hash_to_embedding(img_hash)

        return RecognitionResult(
            face_detected=True,
            faces_count=1,
            quality=QualityResult(
                is_acceptable=True,
                quality_score=0.85,
                blur_score=0.80,
                brightness_score=0.78,
                yaw_angle=5,
                pitch_angle=-2,
                roll_angle=1,
                reason="frame_accepted",
            ),
            liveness=LivenessResult(
                is_live=True,
                score=0.90,
                reason="liveness_passed",
            ),
            match=MatchResult(
                status="not_found",  # Identity matching happens later
                user_id=None,
                similarity=None,
                is_ambiguous=False,
            ),
            embedding=embedding,
        )

    @staticmethod
    def _hash_to_embedding(hash_str: str, dim: int = 128) -> List[float]:
        """Convert a hex hash to a deterministic embedding vector."""
        embedding = [0.0] * dim
        chunk_size = dim
        for i in range(min(len(hash_str) // 2, chunk_size)):
            byte_val = int(hash_str[i * 2 : i * 2 + 2], 16)
            idx = i % dim
            embedding[idx] = (byte_val / 255.0) * 2.0 - 1.0  # scale to [-1, 1]
        return embedding

    @staticmethod
    def _safe_fallback_result() -> RecognitionResult:
        return RecognitionResult(
            face_detected=False,
            faces_count=0,
            quality=QualityResult(
                is_acceptable=False,
                quality_score=0.0,
                blur_score=0.0,
                brightness_score=0.0,
                yaw_angle=0,
                pitch_angle=0,
                roll_angle=0,
                reason="invalid_image_or_no_face",
            ),
            liveness=LivenessResult(
                is_live=False,
                score=0.0,
                reason="liveness_skipped_no_face",
            ),
            match=MatchResult(
                status="not_found",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
            ),
            embedding=None,
        )
