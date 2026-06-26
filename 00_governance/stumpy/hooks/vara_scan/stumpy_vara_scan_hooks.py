from typing import Any, List


class StumpyVaraScanHooks:
    """
    Canonical governance hooks for Vara Scan.

    Stumpy uses this module to:
    - validate lineage continuity
    - detect epistemic drift
    - detect invalid promotions
    - enforce constitutional invariants on scan results
    """

    def __init__(self, vault_chain, violation_queue):
        self._chain = vault_chain
        self._violations = violation_queue

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def handle_vault_promotion(self, event: dict[str, Any]) -> None:
        """
        Called when Vara Scan Pipeline emits a vault_promotion event.
        """
        lineage = event["payload"]["lineage"]

        if not self._verify_lineage(lineage):
            self._emit_violation("lineage_corruption", lineage)
            return

        if not self._chain.verify_continuity():
            self._emit_violation("lineage_continuity_break", lineage)
            return

    def handle_epistemic_violation(self, event: dict[str, Any]) -> None:
        """
        Called when Vara Scan Pipeline emits an epistemic_violation event.
        """
        payload = event["payload"]
        self._emit_violation(payload["violation"], payload["lineage"])

    # ------------------------------------------------------------------
    # INTERNAL CHECKS
    # ------------------------------------------------------------------

    def _verify_lineage(self, lineage: List[dict[str, Any]]) -> bool:
        """
        Verify lineage entries contain required fields.
        """
        required = ("seq", "operator_id", "role", "altitude")
        for entry in lineage:
            if not all(k in entry for k in required):
                return False
        return True

    # ------------------------------------------------------------------
    # VIOLATION EMISSION
    # ------------------------------------------------------------------

    def _emit_violation(self, violation_type: str, lineage: List[dict[str, Any]]) -> None:
        self._violations.put({
            "type": "vara_scan_violation",
            "source": "stumpy_vara_scan_hooks",
            "payload": {
                "violation": violation_type,
                "lineage": lineage,
            },
        })
