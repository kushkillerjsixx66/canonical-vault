"""
operator_boundary_hooks.py
Stumpy Governance Engine — operator boundary event hooks.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from single emit_operator_event() stub — added
             OperatorBoundaryEvent dataclass, structured emission, and
             pre/post-action hook pair for operator boundary crossing.
"""

from __future__ import annotations
import datetime
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .vara_bridge import emit_epistemic_event


# ── Event schema ─────────────────────────────────────────────────────────── #

@dataclass
class OperatorBoundaryEvent:
    """
    Emitted whenever a Canon subsystem crosses into the operator boundary —
    either surfacing a construct (VI·BND) or requesting an operator decision.
    """
    event_id:    str            = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:   str            = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat()
    )
    subsystem:   str            = "unknown"
    action:      str            = "SURFACE"      # SURFACE | DECISION_REQUEST | ALERT
    payload:     Dict[str, Any] = field(default_factory=dict)
    requires_ack: bool          = False           # True → operator must acknowledge

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id":    self.event_id,
            "timestamp":   self.timestamp,
            "subsystem":   self.subsystem,
            "action":      self.action,
            "payload":     self.payload,
            "requires_ack": self.requires_ack,
        }


# ── Hook registry ─────────────────────────────────────────────────────────── #

_PRE_HOOKS:  List[Callable[[OperatorBoundaryEvent], None]] = []
_POST_HOOKS: List[Callable[[OperatorBoundaryEvent], None]] = []


def register_pre_hook(fn: Callable[[OperatorBoundaryEvent], None]) -> None:
    """Register a callback to run *before* operator boundary emission."""
    _PRE_HOOKS.append(fn)


def register_post_hook(fn: Callable[[OperatorBoundaryEvent], None]) -> None:
    """Register a callback to run *after* operator boundary emission."""
    _POST_HOOKS.append(fn)


# ── Emission ──────────────────────────────────────────────────────────────── #

def emit_operator_event(
    subsystem: str,
    action: str = "SURFACE",
    payload: Optional[Dict[str, Any]] = None,
    requires_ack: bool = False,
) -> OperatorBoundaryEvent:
    """
    Emit an operator boundary event.

    Preserved original function signature; now wraps into a structured
    OperatorBoundaryEvent and runs pre/post hooks before returning.
    """
    event = OperatorBoundaryEvent(
        subsystem=subsystem,
        action=action,
        payload=payload or {},
        requires_ack=requires_ack,
    )

    for hook in _PRE_HOOKS:
        try:
            hook(event)
        except Exception:
            pass  # hooks must never crash the emission pipeline

    # Cross-notify Vara epistemic bus so the event is epistemically tracked
    emit_epistemic_event(
        event_type="operator_boundary_crossing",
        payload=event.to_dict(),
    )

    for hook in _POST_HOOKS:
        try:
            hook(event)
        except Exception:
            pass

    return event
