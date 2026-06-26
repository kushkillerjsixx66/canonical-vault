class RuntimeInvariants:
    """
    Runtime‑layer invariants.
    """

    def check(self, payload: dict) -> bool:
        altitude = payload.get("altitude")
        if altitude not in ("runtime", "epistemic", "governance", "operator"):
            return False
        return True
