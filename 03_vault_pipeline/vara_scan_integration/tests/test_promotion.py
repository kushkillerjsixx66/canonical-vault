from vara.scan.vara_scan_schema import VaraScanResult, WeakSignal
from ..vault_scan_promoter import VaultScanPromoter


def test_promotion_logic():
    promoter = VaultScanPromoter()

    scan = VaraScanResult(
        weak_signals=[WeakSignal("k", "d", "e")],
        trends=[],
        anomalies=[],
        unspecified=[],
        lineage=[{"seq": 1, "operator_id": "op", "role": "root", "altitude": "runtime"}],
    )

    assert promoter.should_promote(scan)
