class IdentityGuard:
    """
    Enforces identity and sovereignty invariants.
    """

    def verify(self, identity: dict) -> bool:
        operator_id = identity.get("operator_id")
        role = identity.get("role")
        sovereignty = identity.get("sovereignty")

        if not operator_id or not role or not sovereignty:
            return False

        if sovereignty not in ("root", "delegated", "observer"):
            return False

        return True
