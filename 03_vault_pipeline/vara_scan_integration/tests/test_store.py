from vara.scan.vara_scan_schema import VaraScanResult, WeakSignal
from ..vault_scan_store import VaultScanStore


def test_store_saves_file(tmp_path):
    store = VaultScanStore(root=tmp_path)

    scan = VaraScanResult(
        weak_signals=[WeakSignal("k", "desc", "ev")],
        trends=[],
        anomalies=[],
        unspecified=[],
        lineage=[{"seq": 1, "operator_id": "op", "role": "root", "altitude": "runtime"}],
    )

    path = store.save(scan)
    assert path.exists()
