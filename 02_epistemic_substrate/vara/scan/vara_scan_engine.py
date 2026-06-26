from typing import Any, List
from .vara_scan_schema import VaraScanResult
from .vara_scan_analyzers import WeakSignalAnalyzer, TrendAnalyzer, AnomalyAnalyzer


class VaraScanEngine:
    """
    Canonical Vara Scan Engine.

    Runs analyzers, assembles results, attaches lineage.
    """

    def __init__(self) -> None:
        self._weak = WeakSignalAnalyzer()
        self._trend = TrendAnalyzer()
        self._anomaly = AnomalyAnalyzer()

    def run(self, artifact: dict, lineage: List[dict]) -> VaraScanResult:
        weak = self._weak.analyze(artifact)
        trends = self._trend.analyze(weak)
        anomalies = self._anomaly.analyze(artifact)

        unspecified = [
            k for k, v in artifact.items()
            if v == "" or v == {} or v == []
        ]

        return VaraScanResult(
            weak_signals=weak,
            trends=trends,
            anomalies=anomalies,
            unspecified=unspecified,
            lineage=lineage,
        )
