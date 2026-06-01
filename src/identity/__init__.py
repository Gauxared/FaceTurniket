"""Identity layer: enrollment, template store, and matching."""

from src.identity.models import (
    EnrollmentResult,
    FaceTemplate,
    IdentitySearchResult,
    UserProfile,
)
from src.identity.template_store import InMemoryTemplateStore

__all__ = [
    "UserProfile",
    "FaceTemplate",
    "EnrollmentResult",
    "IdentitySearchResult",
    "InMemoryTemplateStore",
]
