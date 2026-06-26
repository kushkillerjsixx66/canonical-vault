from typing import Any, List
from .vara_scan_engine import VaraScanEngine
from .vara_scan_schema import VaraScanResult


class VaraScan:
    """
    Canonical Vara Scan.

    - Accepts an artifact (dict)
    - Accepts lineage from Vara
    - Produces a VaraScanResult
    """

    def __init__(self) -> None:
        self._engine = VaraScanEngine()

    def scan(self, artifact: dict, lineage: List[dict]) -> VaraScanResult:
        return self._engine.run(artifact, lineage)
