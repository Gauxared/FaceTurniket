"""Quality gate: select the best acceptable frame from a series."""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from src.contracts.models import RecognitionResult
from src.face.providers.base import FaceRecognitionProvider


@dataclass
class FrameEvaluation:
    """Evaluation of a single frame."""

    frame_id: str
    recognition: RecognitionResult
    is_acceptable: bool


class QualityGate:
    """
    Evaluates a series of candidate frames and selects the best acceptable one.

    Acceptability criteria:
    - face_detected is True
    - exactly one face (faces_count == 1)
    - quality.is_acceptable is True
    - liveness.is_live is True

    Among acceptable frames, the one with the highest quality_score is chosen.
    If no frame is acceptable, returns None for the selected frame.
    """

    def __init__(self, provider: FaceRecognitionProvider):
        self.provider = provider

    @staticmethod
    def _is_acceptable(result: RecognitionResult) -> bool:
        return (
            result.face_detected
            and result.faces_count == 1
            and result.quality.is_acceptable
            and result.liveness.is_live
        )

    def evaluate_series(
        self, frames: List[str]
    ) -> Tuple[Optional[str], RecognitionResult]:
        """
        Evaluate a series of frames and select the best acceptable one.

        Returns:
            (selected_frame_id, recognition_result)
            If no acceptable frame exists, selected_frame_id is None and
            recognition_result is the best rejected frame (highest quality_score).
        """
        if not frames:
            raise ValueError("Frame series must not be empty")

        evaluations: List[FrameEvaluation] = []
        for frame_id in frames:
            recognition = self.provider.recognize(frame_id)
            is_acceptable = self._is_acceptable(recognition)
            evaluations.append(
                FrameEvaluation(
                    frame_id=frame_id,
                    recognition=recognition,
                    is_acceptable=is_acceptable,
                )
            )

        acceptable = [e for e in evaluations if e.is_acceptable]
        if acceptable:
            best = max(acceptable, key=lambda e: e.recognition.quality.quality_score)
            return best.frame_id, best.recognition

        # No acceptable frame: return the best rejected by quality_score
        best_rejected = max(
            evaluations, key=lambda e: e.recognition.quality.quality_score
        )
        return None, best_rejected.recognition
