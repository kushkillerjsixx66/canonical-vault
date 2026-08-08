"""
veil_supervision.py
Stumpy Governance Engine — Veil runtime supervision interface.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from single emit_veil_event() stub — added
             VeilSupervisionEvent, supervision state tracking, alignment
             check, and Vara epistemic bus cross-notification.
"""

from __future__ import annotations
import datetime
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .vara_bridge import emit_epistemic_event


# ── Supervision state enum ────────────────────────────────────────────────── #

class VeilSupervisionState(str, Enum):
    NOMINAL    = "NOMINAL"      # Veil operating within bounds
    DRIFT      = "DRIFT"        # Veil drifting from expected state
    MISALIGNED = "MISALIGNED"   # Veil identity or posture misaligned
    HALTED     = "HALTED"       # Veil halted by governance enforcement
    RECOVERING = "RECOVERING"   # Veil executing realignment sequence


# ── Event schema ─────────────────────────────────────────────────────────── #

@dataclass
class VeilSupervisionEvent:
    """
    Emitted by Stumpy whenever the Veil runtime is observed or assessed.
    Consumed by Vara epistemic bus and the Stumpy audit cluster.
    """
    event_id:   str                  = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:  str                  = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat()
    )
    identity:   str                  = "unknown"
    state:      VeilSupervisionState = VeilSupervisionState.NOMINAL
    drift_score: float               = 0.0        # 0.0 = none, 1.0 = max
    flags:      List[str]            = field(default_factory=list)
    metadata:   Dict[str, Any]       = field(default_factory=dict)

    def is_anomalous(self) -> bool:
        return self.state in (
            VeilSupervisionState.DRIFT,
            VeilSupervisionState.MISALIGNED,
            VeilSupervisionState.HALTED,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id":   self.event_id,
            "timestamp":  self.timestamp,
            "identity":   self.identity,
            "state":      self.state.value,
            "drift_score": self.drift_score,
            "flags":      self.flags,
            "metadata":   self.metadata,
        }


# ── Supervision state store (in-memory last-known state per identity) ─────── #

_LAST_STATE: Dict[str, VeilSupervisionEvent] = {}


def get_last_supervision_state(identity: str) -> Optional[VeilSupervisionEvent]:
    """Return the most recent supervision event for a given Veil identity."""
    return _LAST_STATE.get(identity)


# ── Public API ────────────────────────────────────────────────────────────── #

def emit_veil_event(
    identity: str,
    state: str = "NOMINAL",
    drift_score: float = 0.0,
    flags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> VeilSupervisionEvent:
    """
    Emit a Veil supervision event.

    Preserved original function signature; now wraps into a typed
    VeilSupervisionEvent, updates the last-known state cache, and
    cross-notifies the Vara epistemic bus.
    """
    try:
        vss = VeilSupervisionState(state)
    except ValueError:
        vss = VeilSupervisionState.NOMINAL

    event = VeilSupervisionEvent(
        identity=identity,
        state=vss,
        drift_score=max(0.0, min(1.0, drift_score)),
        flags=flags or [],
        metadata=metadata or {},
    )

    _LAST_STATE[identity] = event

    emit_epistemic_event(
        event_type="veil_supervision",
        payload=event.to_dict(),
    )

    return event
