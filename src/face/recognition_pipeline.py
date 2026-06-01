from typing import Any, Optional, Tuple

from src.contracts.models import RecognitionResult
from src.face.providers.base import FaceRecognitionProvider
from src.face.quality_gate import QualityGate


class RecognitionPipeline:
    """
    Orchestrates face recognition by delegating to a provider.

    The pipeline does not make access decisions.
    It only returns the RecognitionResult from the provider.

    Supports both single-image processing and series processing with quality gate.
    """

    def __init__(
        self, provider: FaceRecognitionProvider, quality_gate: Optional[QualityGate] = None
    ):
        self.provider = provider
        self.quality_gate = quality_gate or QualityGate(provider)
        self._last_selected_frame: Optional[str] = None

    def process(self, image: Any) -> RecognitionResult:
        return self.provider.recognize(image)

    def process_series(
        self, frames: list[Any]
    ) -> Tuple[Optional[str], RecognitionResult]:
        """
        Process a series of frames and select the best acceptable one.

        Returns:
            (selected_frame_id, recognition_result)
            selected_frame_id is None if no acceptable frame was found.
        """
        frame_ids = [f if isinstance(f, str) else str(f) for f in frames]
        selected_frame, recognition = self.quality_gate.evaluate_series(frame_ids)
        self._last_selected_frame = selected_frame
        return selected_frame, recognition

    @property
    def last_selected_frame(self) -> Optional[str]:
        return self._last_selected_frame
