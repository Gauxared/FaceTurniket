from src.contracts.models import AccessDecision, RecognitionResult
from src.access.policies import AccessPolicy


def decide_access(
    recognition_result: RecognitionResult, policy: AccessPolicy
) -> AccessDecision:
    """
    Convert RecognitionResult into AccessDecision based on policy rules.

    Priority order:
    1. face not detected -> deny
    2. multiple faces -> deny
    3. low quality -> retry
    4. liveness failed -> deny
    5. match not found -> deny
    6. ambiguous match -> manual_check or deny
    7. user not allowed -> deny
    8. high-confidence matched -> allow
    9. review-zone similarity -> manual_check/retry
    10. low-confidence similarity -> deny
    """

    match = recognition_result.match
    user_id = match.user_id

    # 1. face not detected
    if not recognition_result.face_detected or recognition_result.faces_count == 0:
        return AccessDecision(
            decision="deny",
            reason="face_not_detected",
            user_id=user_id,
            open_turnstile=False,
        )

    # 2. multiple faces
    if recognition_result.faces_count > 1:
        return AccessDecision(
            decision="deny",
            reason="multiple_faces_detected",
            user_id=user_id,
            open_turnstile=False,
        )

    # 3. low quality
    if not recognition_result.quality.is_acceptable:
        return AccessDecision(
            decision="retry",
            reason=f"quality_not_acceptable: {recognition_result.quality.reason}",
            user_id=user_id,
            open_turnstile=False,
        )

    # 4. liveness failed
    if not recognition_result.liveness.is_live:
        return AccessDecision(
            decision="deny",
            reason=f"liveness_failed: {recognition_result.liveness.reason}",
            user_id=user_id,
            open_turnstile=False,
        )

    # 5. match not found
    if match.status == "not_found":
        return AccessDecision(
            decision="deny",
            reason="user_not_found",
            user_id=user_id,
            open_turnstile=False,
        )

    # 6. ambiguous match
    if match.status == "ambiguous" or match.is_ambiguous:
        if policy.ambiguous_behavior == "manual_check":
            return AccessDecision(
                decision="manual_check",
                reason="ambiguous_match",
                user_id=user_id,
                open_turnstile=False,
            )
        return AccessDecision(
            decision="deny",
            reason="ambiguous_match",
            user_id=user_id,
            open_turnstile=False,
        )

    # 7. user not allowed
    if user_id is not None and not policy.is_user_allowed(user_id):
        return AccessDecision(
            decision="deny",
            reason="user_not_allowed",
            user_id=user_id,
            open_turnstile=False,
        )

    similarity = match.similarity
    if similarity is None:
        return AccessDecision(
            decision="deny",
            reason="similarity_not_available",
            user_id=user_id,
            open_turnstile=False,
        )

    # 8. high-confidence matched and access allowed
    if (
        match.status == "matched"
        and user_id is not None
        and similarity >= policy.allow_threshold
    ):
        return AccessDecision(
            decision="allow",
            reason="user_matched_and_access_allowed",
            user_id=user_id,
            open_turnstile=False,  # turnstile is NOT opened by decision module
        )

    # 9. review-zone similarity
    if similarity >= policy.review_threshold:
        if policy.review_behavior == "retry":
            return AccessDecision(
                decision="retry",
                reason=(
                    f"similarity_review_zone: {similarity:.3f} in "
                    f"[{policy.review_threshold}, {policy.allow_threshold})"
                ),
                user_id=user_id,
                open_turnstile=False,
            )
        return AccessDecision(
            decision="manual_check",
            reason=(
                f"similarity_review_zone: {similarity:.3f} in "
                f"[{policy.review_threshold}, {policy.allow_threshold})"
            ),
            user_id=user_id,
            open_turnstile=False,
        )

    # 10. low-confidence similarity
    if similarity < policy.deny_below_threshold:
        return AccessDecision(
            decision="deny",
            reason=(
                f"similarity_below_threshold: {similarity:.3f} < "
                f"{policy.deny_below_threshold}"
            ),
            user_id=user_id,
            open_turnstile=False,
        )

    return AccessDecision(
        decision="deny",
        reason=(
            f"similarity_below_review_threshold: {similarity:.3f} < "
            f"{policy.review_threshold}"
        ),
        user_id=user_id,
        open_turnstile=False,
    )
