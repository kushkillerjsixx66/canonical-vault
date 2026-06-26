import json
from pathlib import Path
from typing import Any
from vara.scan.vara_scan_schema import VaraScanResult


class VaultScanStore:
    """
    Canonical storage layer for Vara Scan results.

    Stores:
    - weak signals
    - trends
    - anomalies
    - unspecified fields
    - lineage

    Storage format: JSON
    """

    def __init__(self, root: str = "vault/vara_scans") -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, scan: VaraScanResult) -> Path:
        seq = scan.lineage[-1]["seq"]
        path = self._root / f"scan_{seq}.json"

        data = {
            "weak_signals": [s.__dict__ for s in scan.weak_signals],
            "trends": [
                {"name": t.name, "signals": [s.__dict__ for s in t.signals]}
                for t in scan.trends
            ],
            "anomalies": [a.__dict__ for a in scan.anomalies],
            "unspecified": scan.unspecified,
            "lineage": scan.lineage,
        }

        with path.open("w") as f:
            json.dump(data, f, indent=2)

        return path
