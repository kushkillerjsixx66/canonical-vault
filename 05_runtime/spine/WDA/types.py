from dataclasses import dataclass
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime


@dataclass
class Capability:
    name: str
    risk_level: str
    requires_policy: bool


@dataclass
class Decision:
    decision_type: str
    label: str
    confidence: float
    requires_policy: bool
    criteria_ref: list


@dataclass
class Output:
    output_id: str
    output_type: str
    ref: str
    visibility: str
    downstream_targets: list


@dataclass
class DriftSignal:
    score: float
    threshold: float
    drift_type: str | None
    explanation: str | None


@dataclass
class Event:
    capability: Capability
    decision: Decision
    output: Output
    drift: DriftSignal
    modifies_or_depends_on_artifact: bool
    is_reversible: bool
    context: Dict[str, Any]
    actor: Dict[str, Any]
    raw_input_ref: str
    normalized_features_ref: str | None
    sensitivity_label: str
    governance_requires_audit: bool


@dataclass
class EAT:
    eat_id: str
    timestamp: str
    capability: str
    decision: str
    output: str
    verdict: str
    lineage: Dict[str, Any]
