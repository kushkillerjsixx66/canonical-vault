"""
CDS-Ω1 Canonical Data Models
Covers: DIP, SCP, CSP and all nested types.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import uuid


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class DomainID(str, Enum):
    ECON       = "ECON"
    COMM       = "COMM"
    STOCK      = "STOCK"
    CRYPTO     = "CRYPTO"
    GOV        = "GOV"
    GEO        = "GEO"
    SOCIAL     = "SOCIAL"
    ENERGY     = "ENERGY"
    TECH       = "TECH"
    HEALTH     = "HEALTH"
    # Vara Phase-2 domain channels
    GEOPOL     = "GEOPOL"
    WORLDPOL   = "WORLDPOL"
    INDUSTRIAL = "INDUSTRIAL"


class SignalType(str, Enum):
    INDEX      = "INDEX"
    PRICE      = "PRICE"
    POLICY     = "POLICY"
    FLOW       = "FLOW"
    VOLATILITY = "VOLATILITY"
    SENTIMENT  = "SENTIMENT"
    VOLUME     = "VOLUME"
    RATE       = "RATE"
    INDICATOR  = "INDICATOR"


class DriftDirection(str, Enum):
    UP      = "UP"
    DOWN    = "DOWN"
    FLAT    = "FLAT"
    CHAOTIC = "CHAOTIC"


class AnomalyCode(str, Enum):
    SPIKE        = "SPIKE"
    DROP         = "DROP"
    REVERSAL     = "REVERSAL"
    REGIME_SHIFT = "REGIME_SHIFT"
    OUTLIER      = "OUTLIER"
    DIVERGENCE   = "DIVERGENCE"


class Severity(str, Enum):
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"


class CorrelationType(str, Enum):
    TEMPORAL    = "TEMPORAL"
    CAUSAL      = "CAUSAL"
    LAGGED      = "LAGGED"
    REINFORCING = "REINFORCING"
    DIVERGENT   = "DIVERGENT"
    PREDICTIVE  = "PREDICTIVE"


class SynthesisType(str, Enum):
    MARKET_POLICY_FRACTURE  = "MARKET_POLICY_FRACTURE"
    CRYPTO_REG_CONVERGENCE  = "CRYPTO_REG_CONVERGENCE"
    SYSTEMIC_DRIFT          = "SYSTEMIC_DRIFT"
    CROSS_DOMAIN_AMPLIFY    = "CROSS_DOMAIN_AMPLIFY"
    LIQUIDITY_SHOCK         = "LIQUIDITY_SHOCK"
    REGULATORY_DIVERGENCE   = "REGULATORY_DIVERGENCE"
    SENTIMENT_FRACTURE      = "SENTIMENT_FRACTURE"
    BASELINE                = "BASELINE"


class IndicatorType(str, Enum):
    RISK        = "RISK"
    OPPORTUNITY = "OPPORTUNITY"
    INSTABILITY = "INSTABILITY"
    INFLECTION  = "INFLECTION"
    TREND       = "TREND"


class EscalationPath(str, Enum):
    NONE           = "NONE"
    PARADOX_ENGINE = "PARADOXENGINE"
    FIELD_INTEL    = "FIELDINTEL"
    OPERATOR_ALERT = "OPERATORALERT"


# ---------------------------------------------------------------------------
# Nested Types
# ---------------------------------------------------------------------------

@dataclass
class Signal:
    signal_type: SignalType
    value: float
    weight: float        # [0, 1]
    confidence: float    # [0, 1]
    source: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not 0.0 <= self.weight <= 1.0:
            errors.append(f"Signal weight out of range: {self.weight}")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append(f"Signal confidence out of range: {self.confidence}")
        return errors

    def to_dict(self) -> dict:
        return {
            "signal_type": self.signal_type.value,
            "value": self.value,
            "weight": self.weight,
            "confidence": self.confidence,
            "source": self.source,
        }


@dataclass
class DriftIndicator:
    vector: list[float]
    magnitude: float
    direction: DriftDirection
    volatility: float    # [0, 1]

    def to_dict(self) -> dict:
        return {
            "vector": self.vector,
            "magnitude": self.magnitude,
            "direction": self.direction.value,
            "volatility": self.volatility,
        }


@dataclass
class AnomalyFlag:
    code: AnomalyCode
    severity: Severity
    description: str

    def to_dict(self) -> dict:
        return {
            "code": self.code.value,
            "severity": self.severity.value,
            "description": self.description,
        }


@dataclass
class ReinforcementCluster:
    signals: list[Signal]
    domain_origin: DomainID
    weight: float        # aggregate weight

    def to_dict(self) -> dict:
        return {
            "signals": [s.to_dict() for s in self.signals],
            "domain_origin": self.domain_origin.value,
            "weight": self.weight,
        }


@dataclass
class PredictiveIndicator:
    indicator_type: IndicatorType
    value: float
    confidence: float    # [0, 1]

    def to_dict(self) -> dict:
        return {
            "indicator_type": self.indicator_type.value,
            "value": self.value,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# Packet Types
# ---------------------------------------------------------------------------

@dataclass
class DIP:
    """Domain Intelligence Packet — raw domain signal payload."""
    domain_id: DomainID
    timestamp: datetime
    signal_set: list[Signal]
    weight_vector: list[float]
    confidence_score: float              # [0, 1]
    drift_indicators: list[DriftIndicator]
    anomaly_flags: list[AnomalyFlag]
    metadata: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not 0.0 <= self.confidence_score <= 1.0:
            errors.append(f"DIP confidence_score out of range: {self.confidence_score}")
        if len(self.weight_vector) != len(self.signal_set):
            errors.append(
                f"weight_vector length {len(self.weight_vector)} != "
                f"signal_set length {len(self.signal_set)}"
            )
        for sig in self.signal_set:
            errors.extend(sig.validate())
        return errors

    def to_dict(self) -> dict:
        return {
            "type": "DIP",
            "version": self.version,
            "domain_id": self.domain_id.value,
            "timestamp": self.timestamp.isoformat(),
            "signal_set": [s.to_dict() for s in self.signal_set],
            "weight_vector": self.weight_vector,
            "confidence_score": self.confidence_score,
            "drift_indicators": [d.to_dict() for d in self.drift_indicators],
            "anomaly_flags": [a.to_dict() for a in self.anomaly_flags],
            "metadata": self.metadata,
        }


@dataclass
class SCP:
    """Synthesis Correlation Packet — pairwise domain correlation."""
    domain_a: DomainID
    domain_b: DomainID
    correlation_type: CorrelationType
    correlation_strength: float          # [-1, 1]
    lag: float                           # seconds / arbitrary units
    predictive_value: float              # [0, 1]
    reinforcement_signals: list[Signal]
    divergence_signals: list[Signal]
    contradiction_score: float           # [0, 1]
    metadata: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not -1.0 <= self.correlation_strength <= 1.0:
            errors.append(f"correlation_strength out of range: {self.correlation_strength}")
        if not 0.0 <= self.contradiction_score <= 1.0:
            errors.append(f"contradiction_score out of range: {self.contradiction_score}")
        if not 0.0 <= self.predictive_value <= 1.0:
            errors.append(f"predictive_value out of range: {self.predictive_value}")
        return errors

    def to_dict(self) -> dict:
        return {
            "type": "SCP",
            "version": self.version,
            "domain_a": self.domain_a.value,
            "domain_b": self.domain_b.value,
            "correlation_type": self.correlation_type.value,
            "correlation_strength": self.correlation_strength,
            "lag": self.lag,
            "predictive_value": self.predictive_value,
            "reinforcement_signals": [s.to_dict() for s in self.reinforcement_signals],
            "divergence_signals": [s.to_dict() for s in self.divergence_signals],
            "contradiction_score": self.contradiction_score,
            "metadata": self.metadata,
        }


@dataclass
class CSP:
    """Canon Synthesis Packet — final synthesized cross-domain intelligence."""
    synthesis_id: str
    timestamp: datetime
    domains_involved: list[DomainID]
    synthesis_type: SynthesisType
    insight: str
    reinforcement_clusters: list[ReinforcementCluster]
    contradiction_matrix: list[list[float]]
    drift_vector: list[float]
    predictive_indicators: list[PredictiveIndicator]
    confidence_score: float              # [0, 1]
    escalation_path: EscalationPath
    metadata: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not 0.0 <= self.confidence_score <= 1.0:
            errors.append(f"CSP confidence_score out of range: {self.confidence_score}")
        n = len(self.domains_involved)
        if len(self.contradiction_matrix) != n:
            errors.append(f"contradiction_matrix rows {len(self.contradiction_matrix)} != domains {n}")
        for row in self.contradiction_matrix:
            if len(row) != n:
                errors.append(f"contradiction_matrix column mismatch")
                break
        return errors

    def to_dict(self) -> dict:
        return {
            "type": "CSP",
            "version": self.version,
            "synthesis_id": self.synthesis_id,
            "timestamp": self.timestamp.isoformat(),
            "domains_involved": [d.value for d in self.domains_involved],
            "synthesis_type": self.synthesis_type.value,
            "insight": self.insight,
            "reinforcement_clusters": [c.to_dict() for c in self.reinforcement_clusters],
            "contradiction_matrix": self.contradiction_matrix,
            "drift_vector": self.drift_vector,
            "predictive_indicators": [p.to_dict() for p in self.predictive_indicators],
            "confidence_score": self.confidence_score,
            "escalation_path": self.escalation_path.value,
            "metadata": self.metadata,
        }
