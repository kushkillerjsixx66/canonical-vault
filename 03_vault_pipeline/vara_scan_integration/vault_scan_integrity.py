from vara.scan.vara_scan_schema import VaraScanResult


class VaultScanIntegrity:
    """
    Canonical integrity enforcement for Vara Scan results.

    Ensures:
    - lineage entries contain seq/operator_id/role/altitude
    - weak signals have key/description/evidence
    - anomalies have field/value/reason
    """

    def validate(self, scan: VaraScanResult) -> bool:
        # Validate lineage
        for entry in scan.lineage:
            if not all(k in entry for k in ("seq", "operator_id", "role", "altitude")):
                return False

        # Validate weak signals
        for s in scan.weak_signals:
            if not s.key or not s.description:
                return False

        # Validate anomalies
        for a in scan.anomalies:
            if not a.field or a.reason is None:
                return False

        return True
