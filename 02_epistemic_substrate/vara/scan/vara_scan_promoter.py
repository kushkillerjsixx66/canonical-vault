from typing import Any
from .vara_scan_schema import VaraScanResult


class VaraScanPromoter:
    """
    Canonical promotion logic.

    Promotes a scan to Vault if:
    - It contains at least one weak signal OR anomaly
    - Lineage is valid
    """

    def should_promote(self, scan: VaraScanResult) -> bool:
        if not scan.lineage:
            return False
        if scan.weak_signals or scan.anomalies:
            return True
        return False
