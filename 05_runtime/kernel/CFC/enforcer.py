class ConstraintEnforcer:
    """
    Applies posture-based constraint enforcement.
    """

    def enforce(self, posture: str):
        if posture == "blocked":
            return {"allowed": False, "reason": "Load too high"}
        if posture == "degraded":
            return {"allowed": True, "limits": ["no_external_calls"]}
        if posture == "cautious":
            return {"allowed": True, "limits": ["rate_limit"]}
        return {"allowed": True}
