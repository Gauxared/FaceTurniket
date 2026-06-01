"""Identity matcher for 1:1 verification and 1:N identification."""

import math
from typing import List, Optional

from src.contracts.models import MatchResult, RecognitionResult
from src.identity.enrollment import generate_mock_embedding
from src.identity.models import IdentitySearchResult
from src.identity.template_store import InMemoryTemplateStore


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def identity_search_result_to_match_result(
    result: IdentitySearchResult,
) -> MatchResult:
    """Convert IdentitySearchResult to MatchResult."""
    return MatchResult(
        status=result.status,
        user_id=result.user_id,
        similarity=result.similarity,
        is_ambiguous=result.is_ambiguous,
    )


class IdentityMatcher:
    """
    Performs identity verification and identification against stored templates.

    Uses real embeddings from provider when available, otherwise falls back
    to deterministic mock embeddings for backward compatibility.
    Does not make access decisions or interact with turnstile.
    """

    def __init__(
        self,
        store: InMemoryTemplateStore,
        threshold: float = 0.70,
        ambiguity_margin: float = 0.05,
    ):
        self.store = store
        self.threshold = threshold
        self.ambiguity_margin = ambiguity_margin

    @staticmethod
    def _probe_embedding_from_recognition(
        recognition: RecognitionResult,
    ) -> Optional[List[float]]:
        """
        Get probe embedding from recognition result.

        Uses real embedding from provider if available.
        Falls back to generating mock embedding from match user_id
        for filename-based mock scenarios.
        """
        # Use real embedding from provider if available
        if recognition.embedding is not None:
            return recognition.embedding

        # Fallback to mock embedding for harness scenarios where provider
        # returns filename-based results without embeddings
        user_id = recognition.match.user_id
        if user_id is None:
            return None
        return generate_mock_embedding(user_id)

    def verify_1to1(
        self, recognition: RecognitionResult, claimed_user_id: str
    ) -> IdentitySearchResult:
        """
        1:1 verification: compare the probe against claimed user's templates.

        Returns IdentitySearchResult with status matched/low_similarity/not_found.
        """
        probe_embedding = self._probe_embedding_from_recognition(recognition)
        if probe_embedding is None:
            return IdentitySearchResult(
                status="not_found",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
                second_best_similarity=None,
                top2_margin=None,
            )

        templates = self.store.get_templates_for_user(claimed_user_id)
        if not templates:
            return IdentitySearchResult(
                status="not_found",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
                second_best_similarity=None,
                top2_margin=None,
            )

        best_sim = max(
            cosine_similarity(probe_embedding, t.embedding)
            for t in templates
        )

        if best_sim >= self.threshold:
            return IdentitySearchResult(
                status="matched",
                user_id=claimed_user_id,
                similarity=best_sim,
                is_ambiguous=False,
                second_best_similarity=None,
                top2_margin=None,
            )

        return IdentitySearchResult(
            status="low_similarity",
            user_id=claimed_user_id,
            similarity=best_sim,
            is_ambiguous=False,
            second_best_similarity=None,
            top2_margin=None,
        )

    def identify_1toN(
        self, recognition: RecognitionResult
    ) -> IdentitySearchResult:
        """
        1:N identification: compare the probe against all stored templates.

        Returns IdentitySearchResult with status matched/not_found/ambiguous.
        """
        probe_embedding = self._probe_embedding_from_recognition(recognition)
        if probe_embedding is None:
            return IdentitySearchResult(
                status="not_found",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
                second_best_similarity=None,
                top2_margin=None,
            )

        all_templates = self.store.get_all_templates()
        if not all_templates:
            return IdentitySearchResult(
                status="not_found",
                user_id=None,
                similarity=None,
                is_ambiguous=False,
                second_best_similarity=None,
                top2_margin=None,
            )

        matches = []
        for template in all_templates:
            sim = cosine_similarity(probe_embedding, template.embedding)
            matches.append((sim, template.user_id))

        # Sort by similarity descending
        matches.sort(key=lambda x: x[0], reverse=True)

        best_sim, best_user_id = matches[0]
        second_best_sim = matches[1][0] if len(matches) > 1 else None
        top2_margin = (
            abs(best_sim - second_best_sim)
            if second_best_sim is not None
            else None
        )

        if best_sim < self.threshold:
            return IdentitySearchResult(
                status="not_found",
                user_id=None,
                similarity=best_sim,
                is_ambiguous=False,
                second_best_similarity=second_best_sim,
                top2_margin=top2_margin,
            )

        # Check ambiguity: if top two are close
        if (
            second_best_sim is not None
            and top2_margin is not None
            and top2_margin < self.ambiguity_margin
        ):
            return IdentitySearchResult(
                status="ambiguous",
                user_id=best_user_id,
                similarity=best_sim,
                is_ambiguous=True,
                second_best_similarity=second_best_sim,
                top2_margin=top2_margin,
            )

        return IdentitySearchResult(
            status="matched",
            user_id=best_user_id,
            similarity=best_sim,
            is_ambiguous=False,
            second_best_similarity=second_best_sim,
            top2_margin=top2_margin,
        )
