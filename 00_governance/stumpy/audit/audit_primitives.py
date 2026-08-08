"""
audit_primitives.py
Stumpy Governance Engine — primitive audit types and violation model.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from bare stub — added AuditEntry, ViolationRecord,
             SeverityLevel enum, and helper constructors.
"""

from __future__ import annotations
import datetime
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

_SEVERITY_RANK = ["TRACE", "INFO", "WARNING", "VIOLATION", "CRITICAL"]


class SeverityLevel(str, Enum):
    TRACE     = "TRACE"
    INFO      = "INFO"
    WARNING   = "WARNING"
    VIOLATION = "VIOLATION"
    CRITICAL  = "CRITICAL"

    def rank(self) -> int:
        return _SEVERITY_RANK.index(self.value)

    def __lt__(self, other: "SeverityLevel") -> bool:
        return self.rank() < other.rank()

    def escalates(self) -> bool:
        """Return True if this severity level triggers operator escalation."""
        return self in (SeverityLevel.VIOLATION, SeverityLevel.CRITICAL)


@dataclass
class AuditEntry:
    """Immutable record of a single auditable event inside the Canon."""
    entry_id:   str            = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:  str            = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat()
    )
    subsystem:  str            = "unknown"
    event_type: str            = "GENERIC"
    severity:   SeverityLevel  = SeverityLevel.INFO
    message:    str            = ""
    metadata:   Dict[str, Any] = field(default_factory=dict)

    def is_violation(self) -> bool:
        return self.severity in (SeverityLevel.VIOLATION, SeverityLevel.CRITICAL)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id":   self.entry_id,
            "timestamp":  self.timestamp,
            "subsystem":  self.subsystem,
            "event_type": self.event_type,
            "severity":   self.severity.value,
            "message":    self.message,
            "metadata":   self.metadata,
        }


@dataclass
class ViolationRecord:
    """Structured record of an invariant or policy violation."""
    violation_id: str            = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:    str            = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat()
    )
    subsystem:    str            = "unknown"
    invariant:    str            = ""     # e.g. "I·SRC", "II·SCR"
    description:  str            = ""
    severity:     SeverityLevel  = SeverityLevel.VIOLATION
    evidence:     Dict[str, Any] = field(default_factory=dict)
    resolved:     bool           = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "timestamp":    self.timestamp,
            "subsystem":    self.subsystem,
            "invariant":    self.invariant,
            "description":  self.description,
            "severity":     self.severity.value,
            "evidence":     self.evidence,
            "resolved":     self.resolved,
        }


def make_violation(
    subsystem: str,
    invariant: str,
    description: str,
    severity: SeverityLevel = SeverityLevel.VIOLATION,
    evidence: Optional[Dict[str, Any]] = None,
) -> ViolationRecord:
    """Factory: create a ViolationRecord with defaults filled."""
    return ViolationRecord(
        subsystem=subsystem,
        invariant=invariant,
        description=description,
        severity=severity,
        evidence=evidence or {},
    )


def make_audit_entry(
    subsystem: str,
    event_type: str,
    message: str,
    severity: SeverityLevel = SeverityLevel.INFO,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditEntry:
    """Factory: create an AuditEntry with defaults filled."""
    return AuditEntry(
        subsystem=subsystem,
        event_type=event_type,
        severity=severity,
        message=message,
        metadata=metadata or {},
    )
