"""
Canonical Vara Schema — mirrors kushkillerjsixx66/canonical-vault
02_epistemic_substrate/vara/scan/vara_scan_schema.py

Reproduced as a local stub so the domain layer can import without
the full Vault runtime present. All field names are identical to
the canonical source.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class WeakSignal:
    """A single low-amplitude epistemic signal detected inside an artifact."""
    key: str          # canonical signal key
    description: str  # human-readable explanation
    evidence: Any     # raw value / excerpt that triggered the signal


@dataclass
class EmergentTrend:
    """A cluster of weak signals that form a recognisable pattern."""
    name: str
    signals: List[WeakSignal]


@dataclass
class Anomaly:
    """A field value that violates domain expectations."""
    field: str
    value: Any
    reason: str


@dataclass
class VaraScanResult:
    """
    Full output of one VaraScanEngine.run() call.
    Passed upstream to VaraInterface → Vara → EpistemicBus → stumpy_event_queue.
    """
    weak_signals: List[WeakSignal]
    trends:       List[EmergentTrend]
    anomalies:    List[Anomaly]
    unspecified:  List[str]           # artifact keys with empty values
    lineage:      List[dict]          # provenance chain

    def to_dict(self) -> dict:
        return {
            "weak_signals": [
                {"key": w.key, "description": w.description, "evidence": w.evidence}
                for w in self.weak_signals
            ],
            "trends": [
                {"name": t.name, "signals": [
                    {"key": s.key, "description": s.description, "evidence": s.evidence}
                    for s in t.signals
                ]}
                for t in self.trends
            ],
            "anomalies": [
                {"field": a.field, "value": a.value, "reason": a.reason}
                for a in self.anomalies
            ],
            "unspecified": self.unspecified,
            "lineage": self.lineage,
        }
