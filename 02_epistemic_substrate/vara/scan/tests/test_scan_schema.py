from ..vara_scan_schema import VaraScanResult, WeakSignal


def test_schema_integrity():
    ws = WeakSignal(key="k", description="d", evidence="e")
    result = VaraScanResult(
        weak_signals=[ws],
        trends=[],
        anomalies=[],
        unspecified=[],
        lineage=[{"seq": 1}],
    )

    assert result.weak_signals[0].key == "k"
    assert result.lineage[0]["seq"] == 1
