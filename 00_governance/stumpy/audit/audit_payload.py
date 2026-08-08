"""
audit_payload.py
Stumpy Governance Engine — structured audit payload + violation summarization.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from bare summarize_violations() stub — added
             ViolationPayload dataclass, severity breakdown, counts per
             subsystem, and AuditPayload envelope.
"""

from __future__ import annotations
import datetime
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .audit_primitives import AuditEntry, ViolationRecord, SeverityLevel


@dataclass
class ViolationPayload:
    """
    Structured payload for a single audit violation — ready for bus emission
    or vault persistence.
    """
    payload_id:   str            = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:    str            = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat()
    )
    violation:    Optional[ViolationRecord] = None
    entry:        Optional[AuditEntry]      = None
    escalate:     bool           = False
    topic:        str            = "stumpy.audit.violation"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "payload_id": self.payload_id,
            "timestamp":  self.timestamp,
            "violation":  self.violation.to_dict() if self.violation else None,
            "entry":      self.entry.to_dict() if self.entry else None,
            "escalate":   self.escalate,
            "topic":      self.topic,
        }


@dataclass
class AuditSummary:
    """Aggregated summary across a set of violations."""
    total:         int                    = 0
    by_type:       Dict[str, int]         = field(default_factory=dict)
    by_severity:   Dict[str, int]         = field(default_factory=dict)
    by_subsystem:  Dict[str, int]         = field(default_factory=dict)
    violations:    List[Dict[str, Any]]   = field(default_factory=list)
    escalated:     int                    = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total":        self.total,
            "by_type":      self.by_type,
            "by_severity":  self.by_severity,
            "by_subsystem": self.by_subsystem,
            "escalated":    self.escalated,
            "violations":   self.violations,
        }


def summarize_violations(
    violations: List[Dict[str, Any]],
) -> AuditSummary:
    """
    Summarize a list of violation dicts into a structured AuditSummary.

    Preserves the original single-function contract while adding:
    - per-severity counts
    - per-subsystem counts
    - escalation count
    """
    by_type:      Dict[str, int] = {}
    by_severity:  Dict[str, int] = {}
    by_subsystem: Dict[str, int] = {}
    escalated = 0

    critical_sevs = {SeverityLevel.VIOLATION.value, SeverityLevel.CRITICAL.value}

    for v in violations:
        vtype     = v.get("type", "unknown")
        severity  = v.get("severity", "UNKNOWN")
        subsystem = v.get("subsystem", "unknown")

        by_type[vtype]         = by_type.get(vtype, 0) + 1
        by_severity[severity]  = by_severity.get(severity, 0) + 1
        by_subsystem[subsystem] = by_subsystem.get(subsystem, 0) + 1

        if severity in critical_sevs:
            escalated += 1

    return AuditSummary(
        total=len(violations),
        by_type=by_type,
        by_severity=by_severity,
        by_subsystem=by_subsystem,
        violations=violations,
        escalated=escalated,
    )


def build_violation_payload(
    record: ViolationRecord,
) -> ViolationPayload:
    """Wrap a ViolationRecord into a bus-ready ViolationPayload."""
    return ViolationPayload(
        violation=record,
        escalate=record.severity.escalates(),
    )
