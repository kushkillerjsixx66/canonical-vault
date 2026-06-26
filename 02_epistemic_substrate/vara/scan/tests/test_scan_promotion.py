from ..vara_scan_promoter import VaraScanPromoter
from ..vara_scan_schema import VaraScanResult, WeakSignal


def test_promotion_logic():
    promoter = VaraScanPromoter()

    scan = VaraScanResult(
        weak_signals=[WeakSignal("k", "d", "e")],
        trends=[],
        anomalies=[],
        unspecified=[],
        lineage=[{"seq": 1}],
    )

    assert promoter.should_promote(scan) is True
