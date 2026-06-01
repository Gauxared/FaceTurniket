"""Service layer for web API: integration with core system."""

from typing import List, Optional, Tuple

import numpy as np

from src.access.decision import decide_access
from src.access.policies import AccessPolicy, UserRegistry
from src.contracts.models import RecognitionResult
from src.devices.turnstile import MockTurnstile
from src.events.event_log import EventLog
from src.face.providers.factory import ProviderFactory
from src.face.recognition_pipeline import RecognitionPipeline
from src.identity.enrollment import EnrollmentService
from src.identity.enrollment import generate_mock_embedding
from src.identity.models import FaceTemplate, UserProfile
from src.identity.matcher import IdentityMatcher, identity_search_result_to_match_result
from src.identity.template_store import InMemoryTemplateStore


class RecognitionService:
    """Manages recognition pipeline and decision making."""

    def __init__(self, provider_name: str = "mock"):
        """Initialize service with specified provider."""
        self.provider = ProviderFactory.create(provider_name=provider_name)
        self.pipeline = RecognitionPipeline(self.provider)
        self.template_store = InMemoryTemplateStore()
        self.enrollment_service = EnrollmentService(self.pipeline, self.template_store)

        # Access policy
        self.policy = AccessPolicy()
        self.matcher = IdentityMatcher(
            self.template_store,
            threshold=self.policy.review_threshold,
            ambiguity_margin=self.policy.identification_margin,
        )
        self.policy.user_registry.add("user_001")
        self.policy.user_registry.add("user_002")
        self.policy.user_registry.add("user_003")

        # Mock turnstile and event log
        self.turnstile = MockTurnstile(turnstile_id="web_turnstile")
        self.event_log = EventLog(log_path="reports/web_events.jsonl")

        # Pre-enroll test users for demo
        self._pre_enroll_demo_users()

        self.provider_name = provider_name
        self._full_name_to_user_id = {}
        self._next_user_seq = 4

    def _resolve_user_identity(
        self,
        full_name: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Tuple[str, Optional[str]]:
        """Resolve internal user_id and optional full_name for enrollment."""
        clean_user_id = (user_id or "").strip()
        clean_full_name = (full_name or "").strip() or None

        if clean_user_id:
            return clean_user_id, clean_full_name

        if not clean_full_name:
            raise ValueError("full_name or user_id is required")

        existing = self._full_name_to_user_id.get(clean_full_name)
        if existing:
            return existing, clean_full_name

        generated = f"user_{self._next_user_seq:03d}"
        self._next_user_seq += 1
        self._full_name_to_user_id[clean_full_name] = generated
        return generated, clean_full_name

    def _pre_enroll_demo_users(self):
        """Pre-enroll test users from mock provider."""
        try:
            test_images = [
                ("user_001_good.jpg", "user_001"),
                ("user_002_good.jpg", "user_002"),
                ("user_003_good.jpg", "user_003"),
            ]

            for image_id, user_id in test_images:
                result = self.enrollment_service.enroll(image_id, user_id)
                if result.success:
                    print(f"Pre-enrolled {user_id}")
        except Exception as e:
            print(f"Warning: Could not pre-enroll demo users: {e}")

    def recognize_image(self, image: np.ndarray, mode: str = "1toN",
                       claimed_user_id: Optional[str] = None) -> Tuple[RecognitionResult, dict]:
        """
        Recognize a single image.

        Returns:
            (recognition_result, additional_data)
        """
        # Process image through pipeline
        recognition = self.pipeline.process(image)

        # Apply identity matching if needed
        if mode == "1to1" and claimed_user_id:
            search_result = self.matcher.verify_1to1(recognition, claimed_user_id)
            from src.identity.matcher import identity_search_result_to_match_result
            recognition = RecognitionResult(
                face_detected=recognition.face_detected,
                faces_count=recognition.faces_count,
                quality=recognition.quality,
                liveness=recognition.liveness,
                match=identity_search_result_to_match_result(search_result),
                embedding=recognition.embedding,
            )
        elif mode == "1toN":
            search_result = self.matcher.identify_1toN(recognition)
            from src.identity.matcher import identity_search_result_to_match_result
            recognition = RecognitionResult(
                face_detected=recognition.face_detected,
                faces_count=recognition.faces_count,
                quality=recognition.quality,
                liveness=recognition.liveness,
                match=identity_search_result_to_match_result(search_result),
                embedding=recognition.embedding,
            )

        # Make access decision
        decision = decide_access(recognition, self.policy)

        # Log event
        event_id = f"web_evt_{id(image)}"
        self.event_log.append(
            event_id=event_id,
            recognition=recognition,
            decision=decision,
            turnstile_command=self.turnstile.process_decision(decision),
        )

        additional_data = {
            "decision": decision,
            "similarity": recognition.match.similarity,
            "quality_score": recognition.quality.quality_score,
        }

        return recognition, additional_data

    def recognize_video(self, frames: List[np.ndarray], max_frames: int = 30,
                       mode: str = "1toN", claimed_user_id: Optional[str] = None) -> Tuple[List[dict], Optional[RecognitionResult], dict]:
        """
        Recognize a video by processing frames.

        Returns:
            (frame_results, final_recognition, final_data)
        """
        frame_results = []
        best_recognition = None
        selected_frame_index: Optional[int] = None
        best_acceptable_quality = float("-inf")
        best_fallback_quality = float("-inf")

        processed_frames = frames[:max_frames]
        if not processed_frames:
            return [], None, {}

        for i, frame in enumerate(processed_frames):
            recognition = self.pipeline.process(frame)

            match_status = recognition.match.status
            similarity = recognition.match.similarity

            frame_results.append({
                "frame_index": i,
                "selected": False,
                "quality_score": recognition.quality.quality_score,
                "blur_score": recognition.quality.blur_score,
                "brightness_score": recognition.quality.brightness_score,
                "face_detected": recognition.face_detected,
                "faces_count": recognition.faces_count,
                "reason": recognition.quality.reason if not recognition.quality.is_acceptable else "good",
                "match_status": match_status,
                "similarity": similarity,
            })

            if recognition.quality.is_acceptable:
                if recognition.quality.quality_score > best_acceptable_quality:
                    best_acceptable_quality = recognition.quality.quality_score
                    selected_frame_index = i
                    best_recognition = recognition
            elif selected_frame_index is None and recognition.quality.quality_score > best_fallback_quality:
                best_fallback_quality = recognition.quality.quality_score
                selected_frame_index = i
                best_recognition = recognition

        if selected_frame_index is not None:
            frame_results[selected_frame_index]["selected"] = True
        else:
            return frame_results, None, {}

        # Apply matching on the same selected frame used for decisioning.
        if mode == "1to1" and claimed_user_id:
            search_result = self.matcher.verify_1to1(best_recognition, claimed_user_id)
            best_recognition = RecognitionResult(
                face_detected=best_recognition.face_detected,
                faces_count=best_recognition.faces_count,
                quality=best_recognition.quality,
                liveness=best_recognition.liveness,
                match=identity_search_result_to_match_result(search_result),
                embedding=best_recognition.embedding,
            )
        elif mode == "1toN":
            search_result = self.matcher.identify_1toN(best_recognition)
            best_recognition = RecognitionResult(
                face_detected=best_recognition.face_detected,
                faces_count=best_recognition.faces_count,
                quality=best_recognition.quality,
                liveness=best_recognition.liveness,
                match=identity_search_result_to_match_result(search_result),
                embedding=best_recognition.embedding,
            )

        # Make final decision on best frame
        final_decision = None
        final_data = {}
        if best_recognition:
            final_decision = decide_access(best_recognition, self.policy)
            final_data = {
                "decision": final_decision,
                "similarity": best_recognition.match.similarity,
                "quality_score": best_recognition.quality.quality_score,
            }

            # Log event
            event_id = f"web_video_evt_{id(frames)}"
            self.event_log.append(
                event_id=event_id,
                recognition=best_recognition,
                decision=final_decision,
                turnstile_command=self.turnstile.process_decision(final_decision),
            )

        return frame_results, best_recognition, final_data

    def enroll_user(self, user_id: str, image: np.ndarray, full_name: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Enroll a new user.

        Returns:
            (success, message, template_id)
        """
        try:
            # Process image directly (numpy array) through pipeline
            recognition = self.pipeline.process(image)

            if not recognition.face_detected:
                return False, "No face detected in image", None

            if not recognition.quality.is_acceptable:
                return False, f"Quality not acceptable: {recognition.quality.reason}", None

            if not recognition.liveness.is_live:
                return False, f"Liveness check failed: {recognition.liveness.reason}", None

            embedding = recognition.embedding or generate_mock_embedding(user_id)
            template = FaceTemplate(
                template_id=f"tmpl_{user_id}_{id(image)}",
                user_id=user_id,
                embedding=embedding,
            )

            # Add to store
            if not self.template_store.user_exists(user_id):
                user_profile = UserProfile(user_id=user_id, name=full_name)
                self.template_store.add_user(user_profile)
            elif full_name:
                user_profile = self.template_store.get_user(user_id)
                if user_profile and not user_profile.name:
                    user_profile.name = full_name

            self.template_store.add_template(template)

            # Add to access policy if not already there
            self.policy.user_registry.add(user_id)

            return True, f"User {user_id} enrolled successfully", template.template_id

        except Exception as e:
            return False, f"Enrollment failed: {str(e)}", None

    def enroll_user_images(
        self,
        images: List[np.ndarray],
        full_name: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> dict:
        """Enroll a user from one or multiple images."""
        resolved_user_id, resolved_full_name = self._resolve_user_identity(
            full_name=full_name,
            user_id=user_id,
        )

        if not images:
            return {
                "success": False,
                "user_id": resolved_user_id,
                "full_name": resolved_full_name,
                "template_ids": [],
                "enrolled_images": 0,
                "message": "No images provided",
            }

        template_ids: List[str] = []
        failures: List[str] = []
        for idx, image in enumerate(images):
            success, message, template_id = self.enroll_user(
                resolved_user_id,
                image,
                full_name=resolved_full_name,
            )
            if success and template_id:
                template_ids.append(template_id)
            else:
                failures.append(f"image_{idx + 1}: {message}")

        success_count = len(template_ids)
        if success_count > 0:
            msg = f"User {resolved_user_id} enrolled with {success_count}/{len(images)} images"
            if failures:
                msg += f"; skipped: {len(failures)}"
            return {
                "success": True,
                "user_id": resolved_user_id,
                "full_name": resolved_full_name,
                "template_ids": template_ids,
                "enrolled_images": success_count,
                "message": msg,
            }

        return {
            "success": False,
            "user_id": resolved_user_id,
            "full_name": resolved_full_name,
            "template_ids": [],
            "enrolled_images": 0,
            "message": "; ".join(failures) if failures else "Enrollment failed for all images",
        }

    def enroll_user_video(
        self,
        user_id: Optional[str],
        frames: List[np.ndarray],
        full_name: Optional[str] = None,
        max_templates: int = 5,
    ) -> dict:
        """Enroll a user from multiple video frames."""
        resolved_user_id, resolved_full_name = self._resolve_user_identity(
            full_name=full_name,
            user_id=user_id,
        )
        if not frames:
            return {
                "success": False,
                "user_id": resolved_user_id,
                "full_name": resolved_full_name,
                "frames_processed": 0,
                "accepted_frames": 0,
                "templates_created": 0,
                "template_ids": [],
                "rejected_reasons": ["no_frames"],
                "message": "No frames to process",
            }

        processed = []
        rejected_reasons: List[str] = []

        for idx, frame in enumerate(frames):
            recognition = self.pipeline.process(frame)

            if not recognition.face_detected or recognition.faces_count == 0:
                rejected_reasons.append(f"frame_{idx}: face_not_detected")
                continue
            if recognition.faces_count > 1:
                rejected_reasons.append(f"frame_{idx}: multiple_faces_detected")
                continue
            if not recognition.quality.is_acceptable:
                rejected_reasons.append(
                    f"frame_{idx}: quality_not_acceptable: {recognition.quality.reason}"
                )
                continue
            if not recognition.liveness.is_live:
                rejected_reasons.append(
                    f"frame_{idx}: liveness_failed: {recognition.liveness.reason}"
                )
                continue

            embedding = recognition.embedding or generate_mock_embedding(f"{resolved_user_id}_{idx}")
            processed.append((recognition.quality.quality_score, embedding, idx))

        if not processed:
            return {
                "success": False,
                "user_id": resolved_user_id,
                "full_name": resolved_full_name,
                "frames_processed": len(frames),
                "accepted_frames": 0,
                "templates_created": 0,
                "template_ids": [],
                "rejected_reasons": rejected_reasons,
                "message": "No acceptable frames for enrollment",
            }

        processed.sort(key=lambda item: item[0], reverse=True)

        if not self.template_store.user_exists(resolved_user_id):
            self.template_store.add_user(UserProfile(user_id=resolved_user_id, name=resolved_full_name))
        elif resolved_full_name:
            user_profile = self.template_store.get_user(resolved_user_id)
            if user_profile and not user_profile.name:
                user_profile.name = resolved_full_name

        existing_count = len(self.template_store.get_templates_for_user(resolved_user_id))
        selected_embeddings = set()
        template_ids: List[str] = []

        for quality_score, embedding, frame_idx in processed:
            key = tuple(round(x, 6) for x in embedding)
            if key in selected_embeddings:
                continue
            selected_embeddings.add(key)

            template_id = f"tmpl_{resolved_user_id}_{existing_count}"
            existing_count += 1
            template = FaceTemplate(
                template_id=template_id,
                user_id=resolved_user_id,
                embedding=embedding,
                source_image_id=f"video_frame_{frame_idx}",
            )
            self.template_store.add_template(template)
            template_ids.append(template_id)
            if len(template_ids) >= max_templates:
                break

        if not template_ids and processed:
            _, embedding, frame_idx = processed[0]
            template_id = f"tmpl_{resolved_user_id}_{existing_count}"
            template = FaceTemplate(
                template_id=template_id,
                user_id=resolved_user_id,
                embedding=embedding,
                source_image_id=f"video_frame_{frame_idx}",
            )
            self.template_store.add_template(template)
            template_ids.append(template_id)

        self.policy.user_registry.add(resolved_user_id)

        return {
            "success": len(template_ids) > 0,
            "user_id": resolved_user_id,
            "full_name": resolved_full_name,
            "frames_processed": len(frames),
            "accepted_frames": len(processed),
            "templates_created": len(template_ids),
            "template_ids": template_ids,
            "rejected_reasons": rejected_reasons,
            "message": (
                f"User {resolved_user_id} enrolled from video with {len(template_ids)} templates"
                if template_ids
                else "No templates created"
            ),
        }

    def get_enrolled_users(self) -> List[dict]:
        """Get list of all enrolled users."""
        users = []
        for profile in self.template_store._users.values():
            templates = self.template_store.get_templates_for_user(profile.user_id)
            users.append({
                "user_id": profile.user_id,
                "full_name": profile.name,
                "templates_count": len(templates),
                "access_allowed": self.policy.is_user_allowed(profile.user_id),
            })
        return users

    def get_recent_events(self, limit: int = 50) -> List[dict]:
        """Get recent events from log."""
        try:
            events = self.event_log.get_recent_entries(limit)
            return events
        except Exception:
            return []

    def get_health_status(self) -> dict:
        """Get health status of the service."""
        return {
            "status": "ok",
            "provider": self.provider_name,
            "users_enrolled": len(self.template_store._users),
        }
