import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.contracts.models import AccessDecision, EventLogEntry, RecognitionResult, TurnstileCommand


class EventLog:
    """Append-only JSONL event log for access attempts."""

    def __init__(self, log_path: Optional[str] = None):
        if log_path is None:
            log_path = "reports/events.jsonl"
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        event_id: str,
        recognition: RecognitionResult,
        decision: AccessDecision,
        turnstile_command: TurnstileCommand,
    ) -> EventLogEntry:
        entry = EventLogEntry(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=decision.user_id,
            turnstile_id=turnstile_command.turnstile_id,
            decision=decision.decision,
            reason=decision.reason,
            similarity=recognition.match.similarity,
            quality_score=recognition.quality.quality_score,
            turnstile_command=turnstile_command.command,
        )
        self._write(entry)
        return entry

    def _write(self, entry: EventLogEntry) -> None:
        line = json.dumps(
            {
                "event_id": entry.event_id,
                "timestamp": entry.timestamp,
                "user_id": entry.user_id,
                "turnstile_id": entry.turnstile_id,
                "decision": entry.decision,
                "reason": entry.reason,
                "similarity": entry.similarity,
                "quality_score": entry.quality_score,
                "turnstile_command": entry.turnstile_command,
            },
            ensure_ascii=False,
        )
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def read_all(self) -> list[dict]:
        if not self.log_path.exists():
            return []
        with open(self.log_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
