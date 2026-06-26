from dataclasses import dataclass
from typing import Any, List


@dataclass
class WeakSignal:
    key: str
    description: str
    evidence: Any


@dataclass
class EmergentTrend:
    name: str
    signals: List[WeakSignal]


@dataclass
class Anomaly:
    field: str
    value: Any
    reason: str


@dataclass
class VaraScanResult:
    weak_signals: List[WeakSignal]
    trends: List[EmergentTrend]
    anomalies: List[Anomaly]
    unspecified: List[str]
    lineage: List[dict]
