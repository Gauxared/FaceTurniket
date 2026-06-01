"""InsightFace provider adapter with lazy import and graceful fallback."""

import os
from pathlib import Path
from typing import Any, List, Optional

import cv2
import numpy as np

from src.contracts.models import (
    LivenessResult,
    MatchResult,
    QualityResult,
    RecognitionResult,
)
from src.face.providers.base import FaceRecognitionProvider


def _import_insightface():
    """Lazy import InsightFace to avoid mandatory dependency."""
    try:
        import insightface
        from insightface.app import FaceAnalysis
        return insightface, FaceAnalysis
    except ImportError as e:
        raise ImportError(
            "InsightFace is not installed. "
            "Install it with: pip install insightface onnxruntime "
            "or use provider_name='mock'"
        ) from e


def _load_image_to_numpy(image: Any) -> Optional[np.ndarray]:
    """
    Load image to numpy array (BGR format for InsightFace).

    Accepts:
    - str: path to image file
    - Path: path to image file
    - np.ndarray: already loaded image

    Returns None if loading fails.
    """
    if isinstance(image, (str, Path)):
        if not os.path.exists(image):
            return None
        img = cv2.imread(str(image))
        return img
    if isinstance(image, np.ndarray):
        return image
    # Try to handle objects with .name attribute
    if hasattr(image, "name"):
        try:
            return cv2.imread(str(image.name))
        except Exception:
            return None
    return None


class InsightFaceProvider(FaceRecognitionProvider):
    """
    Real face recognition provider using InsightFace library.

    This is an optional provider. InsightFace must be installed separately.
    When not available, the provider raises ImportError with instructions.

    Uses the buffalo_l model package for detection and recognition.
    Does NOT use gender, age, race, or emotion for access decisions.
    """

    def __init__(
        self,
        model_name: str = "buffalo_l",
        providers: Optional[list] = None,
        det_size: tuple = (640, 640),
    ):
        insightface, FaceAnalysis = _import_insightface()
        providers = providers or ["CPUExecutionProvider"]
        self._app = FaceAnalysis(name=model_name, providers=providers)
        self._app.prepare(ctx_id=-1, det_size=det_size)

    def recognize(self, image: Any) -> RecognitionResult:
        """
        Analyze image with InsightFace and return RecognitionResult.

        Args:
            image: Path to image file (str or Path) or numpy array (BGR).
        """
        # Load image if it's a path
        img_array = _load_image_to_numpy(image)
        if img_array is None:
            return self._error_result(f"failed to load image: {image}")

        try:
            faces = self._app.get(img_array)
        except Exception as e:
            return self._error_result(str(e))

        if not faces:
            return self._no_face_result()

        faces_count = len(faces)
        if faces_count > 1:
            return self._multiple_faces_result()

        face = faces[0]

        # Quality: use detection score as proxy
        det_score = float(getattr(face, "det_score", 0.5))
        quality_score = min(1.0, max(0.0, det_score))
        is_acceptable = quality_score >= 0.5

        # Pose angles if available
        yaw = int(getattr(face, "pose", [0, 0, 0])[1]) if hasattr(face, "pose") else 0
        pitch = int(getattr(face, "pose", [0, 0, 0])[0]) if hasattr(face, "pose") else 0
        roll = int(getattr(face, "pose", [0, 0, 0])[2]) if hasattr(face, "pose") else 0

        # Embedding for identity layer
        embedding = getattr(face, "embedding", None)
        if embedding is not None:
            embedding = list(embedding)

        return RecognitionResult(
            face_detected=True,
            faces_count=1,
            quality=QualityResult(
                is_acceptable=is_acceptable,
                quality_score=quality_score,
                blur_score=quality_score,  # proxy
                brightness_score=0.7,  # neutral default
                yaw_angle=yaw,
                pitch_angle=pitch,
                roll_angle=roll,
                reason="frame_accepted" if is_acceptable else "quality_below_threshold",
            ),
            liveness=LivenessResult(
                is_live=True,  # InsightFace does not provide liveness
                score=0.5,
                reason="liveness_not_available",
            ),
            match=MatchResult(
                status="not_found",  # matching is done by identity layer
                user_id=None,
                similarity=None,
                is_ambiguous=False,
            ),
            embedding=embedding,
        )

    @staticmethod
    def _no_face_result() -> RecognitionResult:
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
                reason="no_face_detected",
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

    @staticmethod
    def _multiple_faces_result() -> RecognitionResult:
        return RecognitionResult(
            face_detected=True,
            faces_count=2,
            quality=QualityResult(
                is_acceptable=False,
                quality_score=0.5,
                blur_score=0.5,
                brightness_score=0.5,
                yaw_angle=0,
                pitch_angle=0,
                roll_angle=0,
                reason="multiple_faces_detected",
            ),
            liveness=LivenessResult(
                is_live=True,
                score=0.5,
                reason="liveness_not_available",
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
    def _error_result(error_message: str) -> RecognitionResult:
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
                reason=f"provider_error: {error_message}",
            ),
            liveness=LivenessResult(
                is_live=False,
                score=0.0,
                reason="liveness_skipped_error",
            ),
            match=MatchResult(
                status="not_found",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
            ),
            embedding=None,
        )
