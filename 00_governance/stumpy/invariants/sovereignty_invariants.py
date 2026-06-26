class SovereigntyInvariants:
    """
    Sovereignty invariants on identity.
    """

    def check(self, identity: dict) -> bool:
        sovereignty = identity.get("sovereignty")
        if sovereignty not in ("root", "delegated", "observer"):
            return False
        return True
