from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class QualityResult:
    is_acceptable: bool
    quality_score: float
    blur_score: float
    brightness_score: float
    yaw_angle: int
    pitch_angle: int
    roll_angle: int
    reason: str


@dataclass
class LivenessResult:
    is_live: bool
    score: float
    reason: str


@dataclass
class MatchResult:
    status: str  # matched, not_found, low_similarity, ambiguous, skipped_due_to_quality
    user_id: Optional[str] = None
    similarity: Optional[float] = None
    is_ambiguous: bool = False


@dataclass
class RecognitionResult:
    face_detected: bool
    faces_count: int
    quality: QualityResult
    liveness: LivenessResult
    match: MatchResult
    embedding: Optional[List[float]] = None


@dataclass
class AccessDecision:
    decision: str  # allow, deny, retry, manual_check
    reason: str
    user_id: Optional[str] = None
    open_turnstile: bool = False


@dataclass
class EventLogEntry:
    event_id: str
    timestamp: str
    user_id: Optional[str]
    turnstile_id: str
    decision: str
    reason: str
    similarity: Optional[float]
    quality_score: Optional[float]
    turnstile_command: str  # open, keep_closed


@dataclass
class TurnstileCommand:
    turnstile_id: str
    command: str  # open, keep_closed
    reason: str
