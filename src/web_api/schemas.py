"""Pydantic models for web API request/response."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RecognizeRequest(BaseModel):
    """Request to recognize a single image."""
    image: str  # base64-encoded image
    mode: str = "1toN"  # "1toN" or "1to1"
    claimed_user_id: Optional[str] = None  # required for 1to1 mode


class RecognizeVideoRequest(BaseModel):
    """Request to recognize video."""
    video: str  # base64-encoded video
    max_frames: int = 30
    mode: str = "1toN"  # "1toN" or "1to1"
    claimed_user_id: Optional[str] = None  # required for 1to1 mode


class EnrollRequest(BaseModel):
    """Request to enroll a user."""
    user_id: Optional[str] = None
    full_name: Optional[str] = None
    image: Optional[str] = None  # backward-compatible single image
    images: Optional[List[str]] = None  # multiple base64-encoded images


class EnrollVideoRequest(BaseModel):
    """Request to enroll a user from video."""
    user_id: Optional[str] = None
    full_name: Optional[str] = None
    video: str  # base64-encoded video
    max_frames: int = 30
    max_templates: int = 5


class RecognitionResultResponse(BaseModel):
    """Recognition result details for response."""
    face_detected: bool
    faces_count: int
    quality_score: float
    blur_score: float
    brightness_score: float
    yaw_angle: int
    pitch_angle: int
    roll_angle: int
    liveness_is_live: bool
    liveness_score: float
    match_status: str
    match_user_id: Optional[str]
    similarity: Optional[float]


class AccessDecisionResponse(BaseModel):
    """Access decision details for response."""
    decision: str  # allow, deny, retry, manual_check
    reason: str
    user_id: Optional[str]


class RecognizeResponse(BaseModel):
    """Response for single image recognition."""
    success: bool
    recognition_result: RecognitionResultResponse
    decision: AccessDecisionResponse
    similarity: Optional[float]
    quality_score: float
    image_display: Optional[str] = None  # base64 image with annotations


class VideoFrame(BaseModel):
    """Single frame from video processing."""
    frame_index: int
    selected: bool
    quality_score: float
    blur_score: float
    brightness_score: float
    face_detected: bool
    faces_count: int
    reason: Optional[str] = None


class RecognizeVideoResponse(BaseModel):
    """Response for video recognition."""
    success: bool
    total_frames: int
    processed_frames: int
    results: List[VideoFrame]
    final_result: Optional[RecognitionResultResponse]
    final_decision: Optional[AccessDecisionResponse]
    best_frame_index: Optional[int]


class EnrollResponse(BaseModel):
    """Response for enrollment."""
    success: bool
    user_id: str
    full_name: Optional[str] = None
    template_id: Optional[str]
    template_ids: List[str] = Field(default_factory=list)
    enrolled_images: int = 0
    message: str


class EnrollVideoResponse(BaseModel):
    """Response for video enrollment."""
    success: bool
    user_id: str
    full_name: Optional[str] = None
    frames_processed: int
    accepted_frames: int
    templates_created: int
    template_ids: List[str]
    rejected_reasons: List[str]
    message: str


class UserInfo(BaseModel):
    """Information about an enrolled user."""
    user_id: str
    full_name: Optional[str] = None
    templates_count: int
    access_allowed: bool


class UsersListResponse(BaseModel):
    """Response listing all users."""
    users: List[UserInfo]


class EventInfo(BaseModel):
    """Single event in log."""
    event_id: str
    timestamp: str
    user_id: Optional[str]
    decision: str
    reason: str
    similarity: Optional[float]
    quality_score: Optional[float]


class EventsListResponse(BaseModel):
    """Response listing events."""
    events: List[EventInfo]
    total_count: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    provider: str
    users_enrolled: int
    version: str = "1.0.0"
