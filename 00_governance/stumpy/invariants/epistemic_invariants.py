class EpistemicInvariants:
    """
    Epistemic‑layer invariants.
    """

    def check(self, payload: dict) -> bool:
        lineage = payload.get("lineage")
        if not lineage:
            return False
        if not isinstance(lineage, list):
            return False
        return True
