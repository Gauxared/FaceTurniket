from abc import ABC, abstractmethod
from typing import Any

from src.contracts.models import RecognitionResult


class FaceRecognitionProvider(ABC):
    """
    Interface for face recognition providers.

    A provider receives an image and returns a RecognitionResult.
    It does NOT make access decisions, open turnstiles, or write event logs.
    """

    @abstractmethod
    def recognize(self, image: Any) -> RecognitionResult:
        """Analyze image and return recognition result."""
        pass
