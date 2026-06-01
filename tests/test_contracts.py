import pytest

from src.contracts.models import (
    AccessDecision,
    EventLogEntry,
    LivenessResult,
    MatchResult,
    QualityResult,
    RecognitionResult,
    TurnstileCommand,
)


def test_quality_result_creation():
    qr = QualityResult(
        is_acceptable=True,
        quality_score=0.88,
        blur_score=0.82,
        brightness_score=0.76,
        yaw_angle=8,
        pitch_angle=-5,
        roll_angle=2,
        reason="frame_accepted",
    )
    assert qr.is_acceptable is True
    assert qr.quality_score == 0.88
    assert qr.reason == "frame_accepted"


def test_liveness_result_creation():
    lr = LivenessResult(is_live=True, score=0.91, reason="liveness_passed")
    assert lr.is_live is True
    assert lr.score == 0.91


def test_match_result_creation():
    mr = MatchResult(
        status="matched", user_id="user_001", similarity=0.87, is_ambiguous=False
    )
    assert mr.status == "matched"
    assert mr.user_id == "user_001"
    assert mr.similarity == 0.87
    assert mr.is_ambiguous is False


def test_recognition_result_creation():
    rr = RecognitionResult(
        face_detected=True,
        faces_count=1,
        quality=QualityResult(
            is_acceptable=True,
            quality_score=0.88,
            blur_score=0.82,
            brightness_score=0.76,
            yaw_angle=8,
            pitch_angle=-5,
            roll_angle=2,
            reason="frame_accepted",
        ),
        liveness=LivenessResult(is_live=True, score=0.91, reason="liveness_passed"),
        match=MatchResult(
            status="matched",
            user_id="user_001",
            similarity=0.87,
            is_ambiguous=False,
        ),
    )
    assert rr.face_detected is True
    assert rr.faces_count == 1
    assert rr.match.status == "matched"


def test_access_decision_creation():
    ad = AccessDecision(
        decision="allow",
        reason="user_matched_and_access_allowed",
        user_id="user_001",
        open_turnstile=True,
    )
    assert ad.decision == "allow"
    assert ad.open_turnstile is True
    assert ad.user_id == "user_001"


def test_event_log_entry_creation():
    el = EventLogEntry(
        event_id="event_001",
        timestamp="2026-05-30T10:00:00",
        user_id="user_001",
        turnstile_id="turnstile_001",
        decision="allow",
        reason="user_matched_and_access_allowed",
        similarity=0.87,
        quality_score=0.88,
        turnstile_command="open",
    )
    assert el.event_id == "event_001"
    assert el.decision == "allow"
    assert el.turnstile_command == "open"


def test_turnstile_command_creation():
    tc = TurnstileCommand(
        turnstile_id="turnstile_001", command="open", reason="access_allowed"
    )
    assert tc.command == "open"
    assert tc.turnstile_id == "turnstile_001"
