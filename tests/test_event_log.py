import json
import tempfile
from pathlib import Path

import pytest

from src.contracts.models import (
    AccessDecision,
    LivenessResult,
    MatchResult,
    QualityResult,
    RecognitionResult,
    TurnstileCommand,
)
from src.events.event_log import EventLog


@pytest.fixture
def temp_log():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        path = f.name
    yield path
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def sample_recognition():
    return RecognitionResult(
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
            status="matched", user_id="user_001", similarity=0.87, is_ambiguous=False
        ),
    )


@pytest.fixture
def sample_decision():
    return AccessDecision(
        decision="allow",
        reason="user_matched_and_access_allowed",
        user_id="user_001",
    )


@pytest.fixture
def sample_turnstile_command():
    return TurnstileCommand(
        turnstile_id="turnstile_001", command="open", reason="access_allowed"
    )


def test_event_is_written(temp_log, sample_recognition, sample_decision, sample_turnstile_command):
    log = EventLog(log_path=temp_log)
    entry = log.append(
        event_id="evt_001",
        recognition=sample_recognition,
        decision=sample_decision,
        turnstile_command=sample_turnstile_command,
    )
    assert entry.event_id == "evt_001"
    assert entry.user_id == "user_001"
    assert entry.decision == "allow"
    assert entry.turnstile_command == "open"


def test_jsonl_line_can_be_parsed(temp_log, sample_recognition, sample_decision, sample_turnstile_command):
    log = EventLog(log_path=temp_log)
    log.append(
        event_id="evt_002",
        recognition=sample_recognition,
        decision=sample_decision,
        turnstile_command=sample_turnstile_command,
    )
    lines = log.read_all()
    assert len(lines) == 1
    assert lines[0]["event_id"] == "evt_002"
    assert lines[0]["decision"] == "allow"
    assert lines[0]["similarity"] == 0.87
    assert lines[0]["quality_score"] == 0.88
    assert lines[0]["turnstile_command"] == "open"


def test_multiple_events_appended(temp_log, sample_recognition, sample_decision, sample_turnstile_command):
    log = EventLog(log_path=temp_log)
    for i in range(3):
        log.append(
            event_id=f"evt_{i}",
            recognition=sample_recognition,
            decision=sample_decision,
            turnstile_command=sample_turnstile_command,
        )
    lines = log.read_all()
    assert len(lines) == 3
    assert lines[2]["event_id"] == "evt_2"
