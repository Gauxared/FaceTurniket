"""Factory for creating face recognition providers by configuration."""

import os
from typing import Optional

from src.face.providers.base import FaceRecognitionProvider
from src.face.providers.mock_provider import MockFaceRecognitionProvider


class ProviderFactory:
    """
    Factory that creates FaceRecognitionProvider instances.

    Selection priority:
    1. Environment variable FACE_PROVIDER (insightface, mock)
    2. Explicit config passed to create()
    3. Default: mock

    When requesting a real provider and its dependency is missing,
    an ImportError with clear instructions is raised.
    """

    @classmethod
    def create(
        cls,
        provider_name: Optional[str] = None,
        **kwargs,
    ) -> FaceRecognitionProvider:
        """
        Create a provider instance.

        Args:
            provider_name: 'mock', 'insightface', or None to use env/config default.
            **kwargs: Additional args passed to provider constructor.

        Returns:
            FaceRecognitionProvider instance.
        """
        name = provider_name or os.environ.get("FACE_PROVIDER", "mock").lower()

        if name == "mock":
            return MockFaceRecognitionProvider()

        if name == "insightface":
            from src.face.providers.insightface_provider import InsightFaceProvider
            return InsightFaceProvider(**kwargs)

        raise ValueError(
            f"Unknown provider '{name}'. "
            "Supported: 'mock', 'insightface'. "
            "Set FACE_PROVIDER environment variable or pass provider_name."
        )

    @staticmethod
    def available_providers() -> list[str]:
        """Return list of available provider names."""
        providers = ["mock"]
        try:
            import insightface  # noqa: F401
            providers.append("insightface")
        except ImportError:
            pass
        return providers
