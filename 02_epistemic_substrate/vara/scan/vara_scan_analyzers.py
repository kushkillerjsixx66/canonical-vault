from typing import Any, List
from .vara_scan_schema import WeakSignal, EmergentTrend, Anomaly


class WeakSignalAnalyzer:
    def analyze(self, artifact: dict) -> List[WeakSignal]:
        signals = []
        for k, v in artifact.items():
            if isinstance(v, str) and len(v) > 120:
                signals.append(WeakSignal(
                    key=k,
                    description="Long textual field may hide latent structure.",
                    evidence=v[:80] + "..."
                ))
        return signals


class TrendAnalyzer:
    def analyze(self, signals: List[WeakSignal]) -> List[EmergentTrend]:
        if not signals:
            return []
        return [EmergentTrend(name="textual_density", signals=signals)]


class AnomalyAnalyzer:
    def analyze(self, artifact: dict) -> List[Anomaly]:
        anomalies = []
        for k, v in artifact.items():
            if v is None:
                anomalies.append(Anomaly(
                    field=k,
                    value=v,
                    reason="Field unexpectedly null."
                ))
        return anomalies
