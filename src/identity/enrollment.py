"""Enrollment service for registering users and creating face templates."""

import hashlib
from typing import Any, List, Optional

from src.contracts.models import RecognitionResult
from src.face.recognition_pipeline import RecognitionPipeline
from src.identity.models import EnrollmentResult, FaceTemplate
from src.identity.template_store import InMemoryTemplateStore


def generate_mock_embedding(seed: str, dim: int = 128) -> List[float]:
    """
    Generate a deterministic mock embedding from a seed string.

    Creates a sparse vector where a few positions are set based on the seed,
    making embeddings for different seeds more orthogonal.
    """
    h = hashlib.md5(seed.encode()).hexdigest()
    embedding = [0.0] * dim
    for i in range(4):
        pos = int(h[i * 8 : i * 8 + 8], 16) % dim
        val = (int(h[i], 16) + 1) / 16.0
        embedding[pos] = val
    return embedding


class EnrollmentService:
    """
    Handles user enrollment: image -> recognition -> template storage.

    Does not store real images or biometric data.
    Uses real embedding from provider if available, otherwise mock embedding.
    """

    def __init__(
        self, pipeline: RecognitionPipeline, store: InMemoryTemplateStore
    ):
        self.pipeline = pipeline
        self.store = store

    def enroll(self, image: Any, user_id: str) -> EnrollmentResult:
        """
        Enroll a user by processing an image and creating a face template.

        Args:
            image: Image identifier (path/filename) for provider.
            user_id: The user's unique identifier.

        Returns:
            EnrollmentResult with success status and template_id.
        """
        recognition = self.pipeline.process(image)

        if not recognition.face_detected:
            return EnrollmentResult(
                success=False,
                user_id=user_id,
                reason="face_not_detected",
            )

        if not recognition.quality.is_acceptable:
            return EnrollmentResult(
                success=False,
                user_id=user_id,
                reason=f"quality_not_acceptable: {recognition.quality.reason}",
            )

        if not recognition.liveness.is_live:
            return EnrollmentResult(
                success=False,
                user_id=user_id,
                reason=f"liveness_failed: {recognition.liveness.reason}",
            )

        embedding = recognition.embedding
        if embedding is None:
            embedding = generate_mock_embedding(user_id)

        existing_count = len(self.store.get_templates_for_user(user_id))
        template_id = f"tpl_{user_id}_{existing_count}"

        template = FaceTemplate(
            template_id=template_id,
            user_id=user_id,
            embedding=embedding,
            source_image_id=str(image) if isinstance(image, str) else None,
        )

        self.store.add_template(template)

        return EnrollmentResult(
            success=True,
            user_id=user_id,
            template_id=template_id,
            reason="enrolled",
        )
