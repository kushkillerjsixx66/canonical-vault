"""
BaseHarvester — abstract domain harvester contract.

Every domain harvester inherits from this class. It enforces:
  - Domain ontology binding
  - Artifact ingestion → VaraScanResult production
  - DIP assembly from VaraScanResult
  - Async publish to CITL bus (canon.dip.raw.<DOMAIN>)
  - Per-harvester stats, lineage tracking, and error isolation

Architecture position:
    [External Source] → harvest() → VaraScanResult
                      → _build_dip() → DIP dict
                      → bus.publish(canon.dip.raw.<domain>, dip)
                      → DAL picks up and aligns
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from vara.domain_ontology import DomainOntology
from vara.vara_schema import (
    Anomaly, EmergentTrend, VaraScanResult, WeakSignal,
)

logger = logging.getLogger("cds.harvester")


class BaseHarvester(ABC):
    """
    Abstract base class for all domain-specific harvesters.

    Subclasses must implement:
      - domain_id   : str property
      - ontology    : DomainOntology property
      - fetch()     : async → raw artifact dict from data source
      - normalise() : raw dict → canonical artifact dict (keys = signal_types)

    The base class handles:
      - WeakSignalAnalyzer equivalent (ontology-guided)
      - TrendAnalyzer (pattern matching against trend_patterns)
      - AnomalyAnalyzer (ontology anomaly_rules)
      - DIP assembly
      - CITL publishing with lineage
      - Cadence management
      - Stat tracking
    """

    # ------------------------------------------------------------------ init

    def __init__(self, bus: Any) -> None:
        """
        Parameters
        ----------
        bus : CITLBus — the Canon Intelligence Transport Layer message bus.
        """
        self._bus = bus
        self._lineage: list[dict] = []
        self._stats = {
            "fetches":          0,
            "published":        0,
            "anomalies_raised": 0,
            "fetch_errors":     0,
        }
        self._last_run_at: datetime | None = None
        logger.info(
            "Harvester [%s] initialised — cadence=%ds",
            self.domain_id, self.ontology.cadence_s,
        )

    # -------------------------------------------------------- abstract surface

    @property
    @abstractmethod
    def domain_id(self) -> str:
        """Canonical domain identifier (e.g. 'ECON', 'CRYPTO')."""

    @property
    @abstractmethod
    def ontology(self) -> DomainOntology:
        """Bound domain ontology instance."""

    @abstractmethod
    async def fetch(self) -> dict[str, Any]:
        """
        Retrieve a raw data artifact from the domain source.
        Returns a dict of {field: value} — may contain raw / non-canonical keys.
        """

    @abstractmethod
    def normalise(self, raw: dict[str, Any]) -> dict[str, Any]:
        """
        Map raw artifact keys to canonical signal_type keys defined in ontology.
        Returns a clean artifact dict ready for scanning.
        """

    # --------------------------------------------------------- public API

    async def run_once(self) -> VaraScanResult | None:
        """
        Execute one full harvest cycle:
        fetch → normalise → scan → build DIP → publish.
        Returns VaraScanResult or None on error.
        """
        self._stats["fetches"] += 1
        try:
            raw      = await self.fetch()
            artifact = self.normalise(raw)
            result   = self._scan(artifact)
            dip      = self._build_dip(artifact, result)
            topic    = f"canon.dip.raw.{self.domain_id.upper()}"
            await self._bus.publish(topic, dip)
            self._stats["published"] += 1
            self._last_run_at = datetime.utcnow()
            logger.debug(
                "[%s] published DIP  conf=%.2f  weak_signals=%d  anomalies=%d",
                self.domain_id,
                dip["confidence_score"],
                len(result.weak_signals),
                len(result.anomalies),
            )
            return result
        except Exception as exc:
            self._stats["fetch_errors"] += 1
            logger.error("[%s] harvest error: %s", self.domain_id, exc, exc_info=True)
            return None

    @property
    def stats(self) -> dict[str, int | str]:
        return {**self._stats, "last_run": str(self._last_run_at)}

    # --------------------------------------------------------- scanning logic

    def _scan(self, artifact: dict[str, Any]) -> VaraScanResult:
        """
        Ontology-guided scan — mirrors the canonical VaraScanEngine pipeline:
          1. WeakSignalAnalyzer  → weak signals
          2. TrendAnalyzer       → emergent trends from weak signals
          3. AnomalyAnalyzer     → anomalies from raw artifact
          4. Unspecified fields  → empty-value keys
        """
        weak      = self._detect_weak_signals(artifact)
        trends    = self._detect_trends(weak)
        anomalies = self._detect_anomalies(artifact)
        unspecified = [
            k for k, v in artifact.items()
            if v == "" or v == {} or v == [] or v is None
        ]

        self._stats["anomalies_raised"] += len(anomalies)

        lineage_entry = {
            "harvester":  self.domain_id,
            "scan_id":    str(uuid.uuid4()),
            "timestamp":  datetime.utcnow().isoformat(),
            "artifact_keys": list(artifact.keys()),
        }
        self._lineage.append(lineage_entry)
        if len(self._lineage) > 100:
            self._lineage.pop(0)

        return VaraScanResult(
            weak_signals=weak,
            trends=trends,
            anomalies=anomalies,
            unspecified=unspecified,
            lineage=[lineage_entry],
        )

    def _detect_weak_signals(self, artifact: dict) -> list[WeakSignal]:
        """
        Probe ontology.weak_signal_keys for non-zero, non-None values.
        Any key that has a value and is flagged as a weak-signal key
        is returned as a WeakSignal.
        """
        signals = []
        for key in self.ontology.weak_signal_keys:
            val = artifact.get(key)
            if val is not None and val != "" and val != 0:
                signals.append(WeakSignal(
                    key=key,
                    description=f"[{self.domain_id}] weak signal detected on '{key}'",
                    evidence=val,
                ))
        return signals

    def _detect_trends(self, weak: list[WeakSignal]) -> list[EmergentTrend]:
        """
        Match weak signal sets against ontology.trend_patterns.
        A pattern fires when >= min_signals of its constituent keys
        appear in the weak signal set.
        """
        present_keys = {w.key for w in weak}
        trends = []
        for pattern in self.ontology.trend_patterns:
            matched_keys = [k for k in pattern.signal_keys if k in present_keys]
            if len(matched_keys) >= pattern.min_signals:
                matched_signals = [w for w in weak if w.key in matched_keys]
                trends.append(EmergentTrend(
                    name=pattern.name,
                    signals=matched_signals,
                ))
        return trends

    def _detect_anomalies(self, artifact: dict) -> list[Anomaly]:
        """
        Apply ontology.anomaly_rules against artifact values.
        """
        anomalies = []
        for rule in self.ontology.anomaly_rules:
            val = artifact.get(rule.field)
            if val is None:
                continue
            try:
                if rule.predicate(val):
                    anomalies.append(Anomaly(
                        field=rule.field,
                        value=val,
                        reason=rule.reason,
                    ))
            except (TypeError, ValueError):
                pass
        return anomalies

    # --------------------------------------------------------- DIP assembly

    def _build_dip(
        self, artifact: dict[str, Any], result: VaraScanResult
    ) -> dict:
        """
        Assemble a canonical DIP dict from the scanned artifact + VaraScanResult.
        Signal weights come from the ontology weight_map.
        Confidence score = mean of all present signal weights × (1 - anomaly penalty).
        """
        import math

        signal_set = []
        weight_vector = []

        for key, val in artifact.items():
            if val is None or val == "":
                continue
            weight = self.ontology.weight(key)
            # Confidence per signal: reduce if the field has an active anomaly
            field_anomalous = any(a.field == key for a in result.anomalies)
            conf = max(0.1, weight - (0.25 if field_anomalous else 0.0))
            signal_set.append({
                "signal_type": self._map_to_canonical_type(key),
                "value": float(val) if self._is_numeric(val) else 0.0,
                "weight": round(weight, 4),
                "confidence": round(conf, 4),
                "source": f"{self.domain_id.lower()}_harvester",
            })
            weight_vector.append(round(weight, 4))

        # Confidence score: weighted mean, penalised for anomalies
        if weight_vector:
            import numpy as np
            conf_scores = [s["confidence"] for s in signal_set]
            weights     = [s["weight"] for s in signal_set]
            base_conf   = float(np.average(conf_scores, weights=weights))
        else:
            base_conf = 0.5

        anomaly_penalty = min(0.40, len(result.anomalies) * 0.08)
        confidence_score = round(max(0.05, base_conf - anomaly_penalty), 4)

        # Drift indicators from trend patterns (proxy: use trend count as magnitude)
        drift_magnitude = min(1.0, len(result.trends) * 0.15 + len(result.anomalies) * 0.10)
        drift_direction = self._infer_drift_direction(artifact, result)

        drift_indicators = [{
            "vector": [round(drift_magnitude * self.ontology.escalation_bias, 4),
                       round(len(result.weak_signals) / max(1, len(self.ontology.weak_signal_keys)), 4)],
            "magnitude": round(drift_magnitude, 4),
            "direction": drift_direction,
            "volatility": round(min(1.0, len(result.anomalies) * 0.15), 4),
        }]

        # Anomaly flags
        anomaly_flags = [
            {
                "code": self._anomaly_code(a),
                "severity": self._anomaly_severity(a, result),
                "description": a.reason,
            }
            for a in result.anomalies
        ]

        return {
            "type": "DIP",
            "version": "1.0",
            "domain_id": self.domain_id,
            "timestamp": datetime.utcnow().isoformat(),
            "signal_set": signal_set,
            "weight_vector": weight_vector,
            "confidence_score": confidence_score,
            "drift_indicators": drift_indicators,
            "anomaly_flags": anomaly_flags,
            "metadata": {
                "harvester_version": "2.0",
                "weak_signal_count": len(result.weak_signals),
                "trend_count": len(result.trends),
                "trend_names": [t.name for t in result.trends],
                "unspecified_fields": result.unspecified,
                "lineage": result.lineage,
            },
        }

    # --------------------------------------------------------- helpers

    @staticmethod
    def _is_numeric(val: Any) -> bool:
        try:
            float(val)
            return True
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _map_to_canonical_type(key: str) -> str:
        """Best-effort mapping from domain-specific key to CDS SignalType."""
        _map = {
            "price": "PRICE", "rate": "RATE", "index": "INDEX",
            "flow": "FLOW", "volume": "VOLUME", "sentiment": "SENTIMENT",
            "volatility": "VOLATILITY", "policy": "POLICY",
        }
        key_lower = key.lower()
        for fragment, stype in _map.items():
            if fragment in key_lower:
                return stype
        return "INDICATOR"

    def _infer_drift_direction(
        self, artifact: dict, result: VaraScanResult
    ) -> str:
        """Heuristic: more anomalies + trends → CHAOTIC; single direction → UP/DOWN/FLAT."""
        n_anomalies = len(result.anomalies)
        n_trends    = len(result.trends)
        if n_anomalies >= 3 or (n_anomalies >= 1 and n_trends >= 2):
            return "CHAOTIC"
        if n_trends >= 2:
            return "UP"
        if n_anomalies == 1:
            return "DOWN"
        return "FLAT"

    @staticmethod
    def _anomaly_code(a: Anomaly) -> str:
        reason = a.reason.lower()
        if "spike" in reason or "shock" in reason:
            return "SPIKE"
        if "drop" in reason or "contraction" in reason or "decline" in reason:
            return "DROP"
        if "invert" in reason or "reversal" in reason or "pivot" in reason:
            return "REVERSAL"
        if "regime" in reason or "collapse" in reason or "backslid" in reason:
            return "REGIME_SHIFT"
        return "SPIKE"

    @staticmethod
    def _anomaly_severity(a: Anomaly, result: VaraScanResult) -> str:
        # Escalate severity when multiple anomalies co-occur
        n = len(result.anomalies)
        if n >= 3:
            return "CRITICAL"
        if n == 2:
            return "HIGH"
        reason = a.reason.lower()
        if any(w in reason for w in ["imminent", "systemic", "critical", "nuclear", "failed"]):
            return "CRITICAL"
        if any(w in reason for w in ["extreme", "hyperinfl", "invert", "gridlock"]):
            return "HIGH"
        return "MEDIUM"
