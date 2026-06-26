from vara.scan.vara_scan_schema import VaraScanResult


class VaultScanPromoter:
    """
    Canonical promotion logic for Vault.

    A scan is promoted if:
    - lineage exists
    - AND (weak signals OR anomalies exist)
    """

    def should_promote(self, scan: VaraScanResult) -> bool:
        if not scan.lineage:
            return False
        if scan.weak_signals or scan.anomalies:
            return True
        return False
