from typing import Optional


class UserRegistry:
    """Mock user registry for access rights."""

    def __init__(self, allowed_users: Optional[set] = None):
        self._allowed = set(allowed_users) if allowed_users else set()

    def is_allowed(self, user_id: str) -> bool:
        return user_id in self._allowed

    def add(self, user_id: str) -> None:
        self._allowed.add(user_id)

    def remove(self, user_id: str) -> None:
        self._allowed.discard(user_id)


class AccessPolicy:
    """Access policy thresholds and settings."""

    def __init__(
        self,
        min_similarity: Optional[float] = None,
        allow_threshold: float = 0.72,
        review_threshold: float = 0.60,
        deny_below_threshold: Optional[float] = None,
        identification_margin: float = 0.05,
        min_quality_score: float = 0.50,
        ambiguous_behavior: str = "manual_check",  # "manual_check" or "deny"
        review_behavior: str = "manual_check",  # "manual_check" or "retry"
        user_registry: Optional[UserRegistry] = None,
    ):
        self.allow_threshold = (
            min_similarity if min_similarity is not None else allow_threshold
        )
        self.review_threshold = review_threshold
        self.deny_below_threshold = (
            review_threshold
            if deny_below_threshold is None
            else deny_below_threshold
        )
        self.identification_margin = identification_margin
        self.min_quality_score = min_quality_score
        self.ambiguous_behavior = ambiguous_behavior
        self.review_behavior = review_behavior
        self.user_registry = user_registry or UserRegistry()

        # Backward-compatible alias used by older tests/modules.
        self.min_similarity = self.allow_threshold

    def is_user_allowed(self, user_id: str) -> bool:
        return self.user_registry.is_allowed(user_id)
