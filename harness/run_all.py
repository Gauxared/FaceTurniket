#!/usr/bin/env python3
"""Integration harness: run all scenario cases end to end."""

import json
import os
import sys
from pathlib import Path

# Add repo root to PYTHONPATH so imports like `src.access...` work
repo_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(repo_root))

from src.access.decision import decide_access
from src.access.policies import AccessPolicy, UserRegistry
from src.camera.mock_camera import MockCamera
from src.devices.turnstile import MockTurnstile
from src.events.event_log import EventLog
from src.face.providers.mock_provider import MockFaceRecognitionProvider
from src.face.recognition_pipeline import RecognitionPipeline
from src.identity.enrollment import EnrollmentService
from src.identity.matcher import (
    IdentityMatcher,
    identity_search_result_to_match_result,
)
from src.identity.template_store import InMemoryTemplateStore


CASES_DIR = Path(__file__).parent / "cases"

# Users allowed in the harness scenario
HARNESS_USERS = {"user_001", "user_002", "user_003"}


def load_cases() -> list[dict]:
    cases = []
    if not CASES_DIR.exists():
        print(f"ERROR: cases directory not found: {CASES_DIR}")
        sys.exit(1)

    for path in sorted(CASES_DIR.glob("*.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                case = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: malformed JSON in {path.name}: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: could not read {path.name}: {e}")
            sys.exit(1)

        case["_source"] = path.name
        cases.append(case)

    if not cases:
        print("ERROR: no case files found in harness/cases/")
        sys.exit(1)

    return cases


def run_case(
    case: dict,
    pipeline: RecognitionPipeline,
    policy: AccessPolicy,
    turnstile: MockTurnstile,
    event_log: EventLog,
    matcher: IdentityMatcher,
    case_index: int,
) -> dict:
    input_data = case["input"]
    if isinstance(input_data, list):
        selected_frame, recognition = pipeline.process_series(input_data)
    else:
        selected_frame = None
        recognition = pipeline.process(input_data)

    # Apply identity matching if mode is specified
    mode = case.get("mode")
    if mode == "1to1":
        claimed_user_id = case.get("claimed_user_id")
        search_result = matcher.verify_1to1(recognition, claimed_user_id)
        recognition = recognition.__class__(
            face_detected=recognition.face_detected,
            faces_count=recognition.faces_count,
            quality=recognition.quality,
            liveness=recognition.liveness,
            match=identity_search_result_to_match_result(search_result),
        )
    elif mode == "1toN":
        search_result = matcher.identify_1toN(recognition)
        recognition = recognition.__class__(
            face_detected=recognition.face_detected,
            faces_count=recognition.faces_count,
            quality=recognition.quality,
            liveness=recognition.liveness,
            match=identity_search_result_to_match_result(search_result),
        )

    decision = decide_access(recognition, policy)
    turnstile_cmd = turnstile.process_decision(decision)

    event_id = f"harness_evt_{case_index:03d}"
    event_log.append(
        event_id=event_id,
        recognition=recognition,
        decision=decision,
        turnstile_command=turnstile_cmd,
    )

    expected_decision = case.get("expected_decision")
    expected_reason = case.get("expected_reason")
    expected_reason_prefix = case.get("expected_reason_prefix")
    expected_turnstile = case.get("expected_turnstile_command")
    expected_selected_frame = case.get("expected_selected_frame")

    errors = []

    if expected_decision is not None and decision.decision != expected_decision:
        errors.append(
            f"decision mismatch: got '{decision.decision}', expected '{expected_decision}'"
        )

    if expected_reason is not None and decision.reason != expected_reason:
        errors.append(
            f"reason mismatch: got '{decision.reason}', expected '{expected_reason}'"
        )

    if expected_reason_prefix is not None:
        if not decision.reason.startswith(expected_reason_prefix):
            errors.append(
                f"reason prefix mismatch: got '{decision.reason}', expected to start with '{expected_reason_prefix}'"
            )

    if expected_turnstile is not None and turnstile_cmd.command != expected_turnstile:
        errors.append(
            f"turnstile mismatch: got '{turnstile_cmd.command}', expected '{expected_turnstile}'"
        )

    if expected_selected_frame is not None and selected_frame != expected_selected_frame:
        errors.append(
            f"selected frame mismatch: got '{selected_frame}', expected '{expected_selected_frame}'"
        )

    return {
        "case_name": case["case_name"],
        "source": case["_source"],
        "passed": len(errors) == 0,
        "errors": errors,
        "actual_decision": decision.decision,
        "actual_reason": decision.reason,
        "actual_turnstile": turnstile_cmd.command,
        "actual_selected_frame": selected_frame,
    }


def main() -> int:
    print("=== Harness Runner ===")
    cases = load_cases()
    print(f"Loaded {len(cases)} case(s)\n")

    provider = MockFaceRecognitionProvider()
    pipeline = RecognitionPipeline(provider)
    registry = UserRegistry(allowed_users=HARNESS_USERS)
    policy = AccessPolicy(user_registry=registry)
    turnstile = MockTurnstile(turnstile_id="turnstile_harness_001")
    event_log = EventLog(log_path="reports/harness_events.jsonl")

    # Identity store and enrollment
    store = InMemoryTemplateStore()
    enrollment_service = EnrollmentService(pipeline, store)
    matcher = IdentityMatcher(store, threshold=policy.min_similarity)

    # Pre-enroll harness users
    for user_id in HARNESS_USERS:
        result = enrollment_service.enroll(f"{user_id}_good.jpg", user_id=user_id)
        if not result.success:
            print(f"WARNING: Failed to enroll {user_id}: {result.reason}")

    results = []
    for idx, case in enumerate(cases):
        result = run_case(case, pipeline, policy, turnstile, event_log, matcher, idx)
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {result['case_name']:<25} (decision={result['actual_decision']}, turnstile={result['actual_turnstile']}, reason={result['actual_reason']})")
        for err in result["errors"]:
            print(f"       -> {err}")

    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])

    print(f"\n=== Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nSome cases FAILED")
        return 1

    print("\nAll cases PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
