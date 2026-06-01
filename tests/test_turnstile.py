import pytest

from src.contracts.models import AccessDecision
from src.devices.turnstile import MockTurnstile


@pytest.fixture
def turnstile():
    return MockTurnstile(turnstile_id="turnstile_test_001")


def test_turnstile_opens_on_allow(turnstile):
    decision = AccessDecision(
        decision="allow", reason="user_matched", user_id="user_001"
    )
    cmd = turnstile.process_decision(decision)
    assert cmd.command == "open"
    assert cmd.reason == "access_allowed"
    assert cmd.turnstile_id == "turnstile_test_001"


def test_turnstile_keeps_closed_on_deny(turnstile):
    decision = AccessDecision(
        decision="deny", reason="user_not_found", user_id=None
    )
    cmd = turnstile.process_decision(decision)
    assert cmd.command == "keep_closed"
    assert cmd.reason == "access_deny"


def test_turnstile_keeps_closed_on_retry(turnstile):
    decision = AccessDecision(
        decision="retry", reason="low_quality", user_id=None
    )
    cmd = turnstile.process_decision(decision)
    assert cmd.command == "keep_closed"
    assert cmd.reason == "access_retry"


def test_turnstile_keeps_closed_on_manual_check(turnstile):
    decision = AccessDecision(
        decision="manual_check", reason="ambiguous_match", user_id="user_001"
    )
    cmd = turnstile.process_decision(decision)
    assert cmd.command == "keep_closed"
    assert cmd.reason == "access_manual_check"
