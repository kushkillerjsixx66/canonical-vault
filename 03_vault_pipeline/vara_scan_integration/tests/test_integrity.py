from vara.scan.vara_scan_schema import VaraScanResult, WeakSignal, Anomaly
from ..vault_scan_integrity import VaultScanIntegrity


def test_integrity_validation():
    integrity = VaultScanIntegrity()

    scan = VaraScanResult(
        weak_signals=[WeakSignal("k", "d", "e")],
        trends=[],
        anomalies=[Anomaly("f", None, "missing")],
        unspecified=[],
        lineage=[{"seq": 1, "operator_id": "op", "role": "root", "altitude": "runtime"}],
    )

    assert integrity.validate(scan)
