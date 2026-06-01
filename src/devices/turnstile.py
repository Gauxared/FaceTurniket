from src.contracts.models import AccessDecision, TurnstileCommand


class MockTurnstile:
    """Mock turnstile that only opens when decision is 'allow'."""

    def __init__(self, turnstile_id: str = "turnstile_001"):
        self.turnstile_id = turnstile_id
        self.last_command: TurnstileCommand | None = None

    def process_decision(self, decision: AccessDecision) -> TurnstileCommand:
        if decision.decision == "allow":
            cmd = TurnstileCommand(
                turnstile_id=self.turnstile_id,
                command="open",
                reason="access_allowed",
            )
        else:
            cmd = TurnstileCommand(
                turnstile_id=self.turnstile_id,
                command="keep_closed",
                reason=f"access_{decision.decision}",
            )
        self.last_command = cmd
        return cmd
