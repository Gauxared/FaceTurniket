"""Demo execution for diploma presentation."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import cv2

from src.access.decision import decide_access
from src.access.policies import AccessPolicy
from src.devices.turnstile import MockTurnstile
from src.events.event_log import EventLog
from src.face.providers.mock_provider import MockFaceRecognitionProvider
from src.face.providers.factory import ProviderFactory
from src.face.recognition_pipeline import RecognitionPipeline
from src.identity.enrollment import EnrollmentService
from src.identity.matcher import (
    IdentityMatcher,
    identity_search_result_to_match_result,
)
from src.identity.template_store import InMemoryTemplateStore

from .config import DemoConfig, load_demo_config, validate_demo_config


def _read_image(path: str):
    image = cv2.imread(path)
    return image


def _read_video_frames(path: str, max_frames: int = 30):
    cap = cv2.VideoCapture(path)
    frames = []
    try:
        while cap.isOpened() and len(frames) < max_frames:
            ok, frame = cap.read()
            if not ok:
                break
            frames.append(frame)
    finally:
        cap.release()
    return frames


def _recognition_summary(recognition) -> dict[str, Any]:
    return {
        "face_detected": recognition.face_detected,
        "faces_count": recognition.faces_count,
        "quality_score": recognition.quality.quality_score,
        "quality_reason": recognition.quality.reason,
        "liveness_is_live": recognition.liveness.is_live,
        "liveness_reason": recognition.liveness.reason,
        "match_status": recognition.match.status,
        "match_user_id": recognition.match.user_id,
        "similarity": recognition.match.similarity,
    }


class DemoRunner:
    def __init__(self, config: DemoConfig):
        self.config = config
        self.provider = ProviderFactory.create(provider_name=config.provider)
        self.pipeline = RecognitionPipeline(self.provider)
        self.template_store = InMemoryTemplateStore()
        self.enrollment = EnrollmentService(self.pipeline, self.template_store)
        self.matcher = IdentityMatcher(
            self.template_store, threshold=config.thresholds.verification_threshold
        )
        self.policy = AccessPolicy()
        self.policy.user_registry.add(config.demo_user.user_id)
        self.turnstile = MockTurnstile(turnstile_id="demo_turnstile")
        self.event_log = EventLog(log_path="reports/demo_events.jsonl")
        self._ensure_demo_user_access()

    def _ensure_demo_user_access(self) -> None:
        self.policy.user_registry.add(self.config.demo_user.user_id)

    def _enroll_demo_user(self) -> dict[str, Any]:
        enrolled = []
        template_ids = []
        for image_path in self.config.demo_user.enroll_images:
            image = _read_image(image_path)
            if image is None:
                raise ValueError(f"Could not read enrollment image: {image_path}")
            result = self.enrollment.enroll(image, self.config.demo_user.user_id)
            if not result.success:
                raise ValueError(result.reason)
            enrolled.append(image_path)
            template_ids.append(result.template_id)

        return {
            "enrollment_images": enrolled,
            "template_ids": template_ids,
        }

    def _run_photo_case(
        self, image_path: str, mode: str = "1to1", use_filename: bool = False
    ) -> dict[str, Any]:
        if use_filename:
            source = image_path
        else:
            image = _read_image(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            source = image

        recognition = self.pipeline.process(source)
        if mode == "1to1":
            matched = self.matcher.verify_1to1(recognition, self.config.demo_user.user_id)
            recognition = recognition.__class__(
                face_detected=recognition.face_detected,
                faces_count=recognition.faces_count,
                quality=recognition.quality,
                liveness=recognition.liveness,
                match=identity_search_result_to_match_result(matched),
                embedding=recognition.embedding,
            )
        else:
            matched = self.matcher.identify_1toN(recognition)
            recognition = recognition.__class__(
                face_detected=recognition.face_detected,
                faces_count=recognition.faces_count,
                quality=recognition.quality,
                liveness=recognition.liveness,
                match=identity_search_result_to_match_result(matched),
                embedding=recognition.embedding,
            )

        decision = decide_access(recognition, self.policy)
        turnstile_command = self.turnstile.process_decision(decision)
        event_id = f"demo_evt_{Path(image_path).stem}"
        self.event_log.append(
            event_id=event_id,
            recognition=recognition,
            decision=decision,
            turnstile_command=turnstile_command,
        )
        return {
            "image": image_path,
            "recognition": _recognition_summary(recognition),
            "decision": {
                "decision": decision.decision,
                "reason": decision.reason,
                "user_id": decision.user_id,
            },
            "turnstile_command": {
                "turnstile_id": turnstile_command.turnstile_id,
                "command": turnstile_command.command,
                "reason": turnstile_command.reason,
            },
            "event_id": event_id,
        }

    def _run_video_case(self, video_path: str) -> dict[str, Any]:
        frames = _read_video_frames(video_path)
        if not frames:
            raise ValueError(f"Could not read frames from video: {video_path}")
        frame_results = []
        best_recognition = None
        best_score = (-1.0, -1.0)
        best_index = None
        for i, frame in enumerate(frames):
            recognition = self.pipeline.process(frame)
            similarity = None
            if recognition.quality.is_acceptable:
                matched = self.matcher.verify_1to1(
                    recognition, self.config.demo_user.user_id
                )
                recognition = recognition.__class__(
                    face_detected=recognition.face_detected,
                    faces_count=recognition.faces_count,
                    quality=recognition.quality,
                    liveness=recognition.liveness,
                    match=identity_search_result_to_match_result(matched),
                    embedding=recognition.embedding,
                )
                similarity = recognition.match.similarity or 0.0

            frame_results.append(
                {
                    "frame_index": i,
                    "selected": False,
                    "quality_score": recognition.quality.quality_score,
                    "face_detected": recognition.face_detected,
                    "reason": recognition.quality.reason,
                    "similarity": similarity,
                }
            )
            score = (recognition.quality.quality_score, similarity or 0.0)
            if recognition.quality.is_acceptable and score > best_score:
                best_score = score
                best_recognition = recognition
                best_index = i

        if best_recognition is None and frame_results:
            best_index = max(range(len(frame_results)), key=lambda idx: frame_results[idx]["quality_score"])
            frame_results[best_index]["selected"] = True
            best_recognition = self.pipeline.process(frames[best_index])
        elif best_recognition is not None and best_index is not None:
            frame_results[best_index]["selected"] = True

        final_decision = None
        turnstile_command = None
        event_id = None
        if best_recognition:
            final_decision = decide_access(best_recognition, self.policy)
            turnstile_command = self.turnstile.process_decision(final_decision)
            event_id = f"demo_video_evt_{Path(video_path).stem}"
            self.event_log.append(
                event_id=event_id,
                recognition=best_recognition,
                decision=final_decision,
                turnstile_command=turnstile_command,
            )

        return {
            "video": video_path,
            "frames": frame_results,
            "final_recognition": _recognition_summary(best_recognition)
            if best_recognition
            else None,
            "final_decision": {
                "decision": final_decision.decision,
                "reason": final_decision.reason,
                "user_id": final_decision.user_id,
            }
            if final_decision
            else None,
            "turnstile_command": {
                "turnstile_id": turnstile_command.turnstile_id,
                "command": turnstile_command.command,
                "reason": turnstile_command.reason,
            }
            if turnstile_command
            else None,
            "event_id": event_id,
        }

    def run(self) -> dict[str, Any]:
        errors = validate_demo_config(self.config)
        if errors:
            raise ValueError("; ".join(errors))

        timestamp = datetime.now(timezone.utc).isoformat()
        enrollment_info = self._enroll_demo_user()

        positive_photo = None
        if self.config.demo_user.pass_photo:
            positive_photo = self._run_photo_case(self.config.demo_user.pass_photo)
        else:
            raise ValueError("demo_user.pass_photo is required for the demo")

        unknown_photo = None
        if self.config.demo_user.denied_photo:
            try:
                unknown_photo = self._run_photo_case(
                    self.config.demo_user.denied_photo, mode="1toN"
                )
            except Exception as exc:
                unknown_photo = {"skipped": True, "reason": str(exc)}

        low_quality_photo = None
        if self.config.demo_user.low_quality_photo:
            try:
                use_filename = isinstance(self.provider, MockFaceRecognitionProvider)
                low_quality_photo = self._run_photo_case(
                    self.config.demo_user.low_quality_photo,
                    mode="1toN",
                    use_filename=use_filename,
                )
            except Exception as exc:
                low_quality_photo = {"skipped": True, "reason": str(exc)}

        video_result = None
        if self.config.demo_user.pass_video:
            try:
                video_result = self._run_video_case(self.config.demo_user.pass_video)
            except Exception as exc:
                video_result = {"skipped": True, "reason": str(exc)}

        report = {
            "timestamp": timestamp,
            "provider": self.config.provider,
            "thresholds": asdict(self.config.thresholds),
            "demo_user": {
                "user_id": self.config.demo_user.user_id,
                "display_name": self.config.demo_user.display_name,
                "access_allowed": self.config.demo_user.access_allowed,
            },
            "enrollment": enrollment_info,
            "positive_photo": positive_photo,
            "unknown_photo": unknown_photo,
            "low_quality_photo": low_quality_photo,
            "video_result": video_result,
            "event_log_path": str(self.event_log.log_path),
        }
        return report


def load_runner_from_path(config_path: str | Path) -> DemoRunner:
    return DemoRunner(load_demo_config(config_path))


def save_demo_report(report: dict[str, Any], report_path: str | Path) -> Path:
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report_path
