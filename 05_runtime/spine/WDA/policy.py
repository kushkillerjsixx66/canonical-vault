class AuditPolicy:
    """
    Evaluates whether an event requires audit based on simple rules.
    """

    def should_audit(self, event) -> bool:
        if event.governance_requires_audit:
            return True

        if event.capability.risk_level == "HIGH":
            return True

        if event.output.visibility == "EXTERNAL":
            return True

        if not event.is_reversible:
            return True

        if event.drift.score >= event.drift.threshold:
            return True

        return False
