"""Identity models: UserProfile, FaceTemplate, EnrollmentResult, IdentitySearchResult."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UserProfile:
    """User profile in the identity store."""

    user_id: str
    name: Optional[str] = None


@dataclass
class FaceTemplate:
    """Face template with deterministic mock embedding."""

    template_id: str
    user_id: str
    embedding: List[float]
    source_image_id: Optional[str] = None


@dataclass
class EnrollmentResult:
    """Result of an enrollment attempt."""

    success: bool
    user_id: str
    template_id: Optional[str] = None
    reason: str = ""


@dataclass
class IdentitySearchResult:
    """Result of identity verification/search."""

    status: str  # matched, not_found, low_similarity, ambiguous
    user_id: Optional[str] = None
    similarity: Optional[float] = None
    is_ambiguous: bool = False
    second_best_similarity: Optional[float] = None
    top2_margin: Optional[float] = None
