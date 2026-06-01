Назначение

Этот файл описывает публичные контракты между модулями.

Агент не должен менять эти структуры без обновления тестов, harness-сценариев и документации.

RecognitionResult

Результат работы face recognition provider.

{
  "face_detected": true,
  "faces_count": 1,
  "quality": {
    "is_acceptable": true,
    "quality_score": 0.88,
    "blur_score": 0.82,
    "brightness_score": 0.76,
    "yaw_angle": 8,
    "pitch_angle": -5,
    "roll_angle": 2,
    "reason": "frame_accepted"
  },
  "liveness": {
    "is_live": true,
    "score": 0.91,
    "reason": "liveness_passed"
  },
  "match": {
    "status": "matched",
    "user_id": "user_001",
    "similarity": 0.87,
    "is_ambiguous": false
  },
  "embedding": [0.12, 0.34, ...]  // Optional[float]: real embedding from provider, or null for mock
}

**embedding**: Опциональное поле. Если provider возвращает реальное embedding (например, InsightFace),
оно записывается в RecognitionResult. Для Mock provider поле всегда `null`.
Используется для dataset evaluation и дальнейшей 1:1/1:N проверки.
QualityResult
{
  "is_acceptable": true,
  "quality_score": 0.88,
  "blur_score": 0.82,
  "brightness_score": 0.76,
  "yaw_angle": 8,
  "pitch_angle": -5,
  "roll_angle": 2,
  "reason": "frame_accepted"
}
LivenessResult
{
  "is_live": true,
  "score": 0.91,
  "reason": "liveness_passed"
}
MatchResult
{
  "status": "matched",
  "user_id": "user_001",
  "similarity": 0.87,
  "is_ambiguous": false
}

Возможные status:

matched
not_found
low_similarity
ambiguous
skipped_due_to_quality
AccessDecision
{
  "decision": "allow",
  "reason": "user_matched_and_access_allowed",
  "user_id": "user_001",
  "open_turnstile": true
}

Возможные decision:

allow
deny
retry
manual_check
EventLogEntry
{
  "event_id": "event_001",
  "timestamp": "2026-05-30T10:00:00",
  "user_id": "user_001",
  "turnstile_id": "turnstile_001",
  "decision": "allow",
  "reason": "user_matched_and_access_allowed",
  "similarity": 0.87,
  "quality_score": 0.88,
  "turnstile_command": "open"
}
TurnstileCommand
{
  "turnstile_id": "turnstile_001",
  "command": "open",
  "reason": "access_allowed"
}

Возможные command:

open
keep_closed
Важное правило

Face recognition provider возвращает только RecognitionResult.

Он не должен:

проверять права доступа;
открывать турникет;
писать итоговое событие прохода;
принимать бизнес-решение allow/deny.

Итоговое решение принимает только access decision module.