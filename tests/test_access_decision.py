import pytest

from src.access.decision import decide_access
from src.access.policies import AccessPolicy, UserRegistry
from src.contracts.models import (
    LivenessResult,
    MatchResult,
    QualityResult,
    RecognitionResult,
)


@pytest.fixture
def policy_with_access():
    registry = UserRegistry(allowed_users={"user_001", "user_002", "user_003"})
    return AccessPolicy(user_registry=registry)


@pytest.fixture
def policy_strict():
    registry = UserRegistry(allowed_users={"user_001"})
    return AccessPolicy(
        min_similarity=0.75,
        min_quality_score=0.50,
        ambiguous_behavior="deny",
        user_registry=registry,
    )


def create_recognition_result(
    face_detected=True,
    faces_count=1,
    quality_is_acceptable=True,
    quality_score=0.88,
    liveness_is_live=True,
    match_status="matched",
    user_id="user_001",
    similarity=0.87,
    is_ambiguous=False,
):
    return RecognitionResult(
        face_detected=face_detected,
        faces_count=faces_count,
        quality=QualityResult(
            is_acceptable=quality_is_acceptable,
            quality_score=quality_score,
            blur_score=0.82,
            brightness_score=0.76,
            yaw_angle=8,
            pitch_angle=-5,
            roll_angle=2,
            reason="frame_accepted" if quality_is_acceptable else "low_quality",
        ),
        liveness=LivenessResult(
            is_live=liveness_is_live,
            score=0.91 if liveness_is_live else 0.25,
            reason="liveness_passed" if liveness_is_live else "liveness_failed",
        ),
        match=MatchResult(
            status=match_status,
            user_id=user_id if match_status != "not_found" else None,
            similarity=similarity,
            is_ambiguous=is_ambiguous,
        ),
    )


def test_allow_matched_user_with_access(policy_with_access):
    result = create_recognition_result()
    decision = decide_access(result, policy_with_access)
    assert decision.decision == "allow"
    assert decision.open_turnstile is False
    assert decision.user_id == "user_001"
    assert decision.reason == "user_matched_and_access_allowed"


def test_deny_unknown_user(policy_with_access):
    result = create_recognition_result(
        match_status="not_found",
        user_id=None,
    )
    decision = decide_access(result, policy_with_access)
    assert decision.decision == "deny"
    assert decision.reason == "user_not_found"


def test_retry_low_quality(policy_with_access):
    result = create_recognition_result(
        quality_is_acceptable=False,
        quality_score=0.35,
        match_status="skipped_due_to_quality",
    )
    decision = decide_access(result, policy_with_access)
    assert decision.decision == "retry"
    assert "quality_not_acceptable" in decision.reason


def test_deny_spoof_attempt(policy_with_access):
    result = create_recognition_result(
        liveness_is_live=False,
        match_status="not_found",
    )
    decision = decide_access(result, policy_with_access)
    assert decision.decision == "deny"
    assert "liveness_failed" in decision.reason


def test_deny_user_without_access(policy_with_access):
    result = create_recognition_result(user_id="user_999", match_status="matched")
    decision = decide_access(result, policy_with_access)
    assert decision.decision == "deny"
    assert decision.reason == "user_not_allowed"


def test_deny_multiple_faces(policy_with_access):
    result = create_recognition_result(faces_count=3, quality_is_acceptable=False)
    decision = decide_access(result, policy_with_access)
    assert decision.decision == "deny"
    assert decision.reason == "multiple_faces_detected"


def test_deny_face_not_detected(policy_with_access):
    result = create_recognition_result(
        face_detected=False,
        faces_count=0,
        match_status="not_found",
        user_id=None,
    )
    decision = decide_access(result, policy_with_access)
    assert decision.decision == "deny"
    assert decision.reason == "face_not_detected"


def test_deny_low_similarity(policy_strict):
    result = create_recognition_result(similarity=0.55)
    decision = decide_access(result, policy_strict)
    assert decision.decision == "deny"
    assert "similarity_below_threshold" in decision.reason


def test_manual_check_in_review_zone(policy_with_access):
    result = create_recognition_result(similarity=0.66, match_status="matched")
    decision = decide_access(result, policy_with_access)
    assert decision.decision == "manual_check"
    assert "similarity_review_zone" in decision.reason


def test_retry_in_review_zone_when_policy_configured():
    registry = UserRegistry(allowed_users={"user_001"})
    policy = AccessPolicy(
        user_registry=registry,
        review_behavior="retry",
    )
    result = create_recognition_result(similarity=0.65, match_status="matched")
    decision = decide_access(result, policy)
    assert decision.decision == "retry"
    assert "similarity_review_zone" in decision.reason


def test_manual_check_ambiguous_match():
    registry = UserRegistry(allowed_users={"user_001"})
    policy = AccessPolicy(
        user_registry=registry,
        ambiguous_behavior="manual_check",
    )
    result = create_recognition_result(
        is_ambiguous=True,
        match_status="ambiguous",
        user_id="user_001",
    )
    decision = decide_access(result, policy)
    assert decision.decision == "manual_check"
    assert decision.reason == "ambiguous_match"


def test_deny_ambiguous_match_when_policy_is_deny():
    registry = UserRegistry(allowed_users={"user_001"})
    policy = AccessPolicy(
        user_registry=registry,
        ambiguous_behavior="deny",
    )
    result = create_recognition_result(
        is_ambiguous=True,
        match_status="ambiguous",
        user_id="user_001",
    )
    decision = decide_access(result, policy)
    assert decision.decision == "deny"
    assert decision.reason == "ambiguous_match"
