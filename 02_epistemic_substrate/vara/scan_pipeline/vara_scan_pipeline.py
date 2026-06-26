from typing import Any, List

from vara.scan.vara_scan import VaraScan
from vara.scan.vara_scan_schema import VaraScanResult
from vara.scan_trigger.vara_scan_trigger import VaraScanTrigger

from vault_pipeline.vara_scan_integration.vault_scan_store import VaultScanStore
from vault_pipeline.vara_scan_integration.vault_scan_promoter import VaultScanPromoter
from vault_pipeline.vara_scan_integration.vault_scan_integrity import VaultScanIntegrity


class VaraScanPipeline:
    """
    Canonical Vara Scan Pipeline.

    Responsibilities:
    - Accept scan requests from Vara or Veil
    - Trigger scan based on runtime state + lineage
    - Run Vara Scan
    - Validate integrity
    - Promote to Vault if allowed
    - Emit governance events to Stumpy
    """

    def __init__(self, stumpy_event_queue) -> None:
        self._trigger = VaraScanTrigger()
        self._store = VaultScanStore()
        self._promoter = VaultScanPromoter()
        self._integrity = VaultScanIntegrity()
        self._queue = stumpy_event_queue

    def run(
        self,
        artifact: dict[str, Any],
        lineage: List[dict[str, Any]],
        runtime_state: dict[str, Any],
    ) -> VaraScanResult | None:
        """
        Executes the full scan pipeline.

        Returns VaraScanResult if scan was run, else None.
        """

        result = self._trigger.maybe_scan(artifact, lineage, runtime_state)

        if result is None:
            return None

        # Integrity enforcement
        if not self._integrity.validate(result):
            self._emit_governance_violation("scan_integrity_failure", result)
            return result

        # Promotion
        if self._promoter.should_promote(result):
            path = self._store.save(result)
            self._emit_promotion_event(result, path)

        return result

    # ---- Governance Events ----------------------------------------------------

    def _emit_governance_violation(self, violation_type: str, scan: VaraScanResult) -> None:
        self._queue.put({
            "type": "epistemic_violation",
            "source": "vara_scan_pipeline",
            "payload": {
                "violation": violation_type,
                "lineage": scan.lineage,
            },
        })

    def _emit_promotion_event(self, scan: VaraScanResult, path) -> None:
        self._queue.put({
            "type": "vault_promotion",
            "source": "vara_scan_pipeline",
            "payload": {
                "path": str(path),
                "lineage": scan.lineage,
            },
        })
