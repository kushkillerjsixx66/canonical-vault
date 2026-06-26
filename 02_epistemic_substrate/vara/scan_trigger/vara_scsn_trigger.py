from typing import Any, List

from vara.scan.vara_scan import VaraScan
from vara.scan.vara_scan_schema import VaraScanResult
from vault_pipeline.vara_scan_integration.vault_scan_store import VaultScanStore
from vault_pipeline.vara_scan_integration.vault_scan_promoter import VaultScanPromoter
from vault_pipeline.vara_scan_integration.vault_scan_integrity import VaultScanIntegrity


class VaraScanTrigger:
    """
    Canonical trigger for Vara Scan.

    Decides WHEN to run Vara Scan based on:
    - runtime altitude
    - operator posture
    - lineage presence
    """

    def __init__(self) -> None:
        self._scan = VaraScan()
        self._store = VaultScanStore()
        self._promoter = VaultScanPromoter()
        self._integrity = VaultScanIntegrity()

    def maybe_scan(
        self,
        artifact: dict[str, Any],
        lineage: List[dict[str, Any]],
        runtime_state: dict[str, Any],
    ) -> VaraScanResult | None:
        """
        Returns VaraScanResult if a scan is run, else None.
        """

        if not self._should_trigger(runtime_state, lineage):
            return None

        result = self._scan.scan(artifact, lineage)

        if not self._integrity.validate(result):
            return result  # scan exists but not promoted

        if self._promoter.should_promote(result):
            self._store.save(result)

        return result

    def _should_trigger(self, runtime_state: dict[str, Any], lineage: List[dict[str, Any]]) -> bool:
        altitude = runtime_state.get("altitude")
        posture = runtime_state.get("posture", "neutral")

        if not lineage:
            return False

        if altitude not in ("runtime", "epistemic", "governance"):
            return False

        if posture in ("focused", "elevated", "hostile"):
            return True

        return False
