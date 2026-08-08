"""
vara_bridge.py
Stumpy Governance Engine — Vara epistemic bus bridge interface.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from single emit_epistemic_event() stub — added
             EpistemicEventEnvelope, topic routing, and connection to
             the stumpy_event_queue used by vara_epistemic_bus.py.
"""

from __future__ import annotations
import datetime
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:
    from stumpy_governance_bus import stumpy_event_queue  # type: ignore
except ImportError:
    # Fallback: local in-memory queue when bus is not yet wired up.
    import queue
    stumpy_event_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()  # type: ignore


# ── Envelope ──────────────────────────────────────────────────────────────── #

@dataclass
class EpistemicEventEnvelope:
    """
    Standard envelope for events emitted onto the stumpy/vara shared bus.
    Mirrors the schema used by vara_epistemic_bus.emit_epistemic_context().
    """
    envelope_id:  str            = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:    str            = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat()
    )
    source:       str            = "stumpy"
    event_type:   str            = "generic"
    topic:        str            = "stumpy.vara.bridge"
    payload:      Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "timestamp":   self.timestamp,
            "type":        self.event_type,
            "source":      self.source,
            "topic":       self.topic,
            "payload":     self.payload,
        }


# ── Routing table (topic per event_type) ─────────────────────────────────── #

_TOPIC_MAP: Dict[str, str] = {
    "epistemic_state":             "stumpy.vara.epistemic",
    "operator_boundary_crossing":  "stumpy.vara.operator_boundary",
    "vault_integrity_check":       "stumpy.vara.vault_integrity",
    "veil_supervision":            "stumpy.vara.veil",
    "audit_violation":             "stumpy.audit.violation",
}


def _resolve_topic(event_type: str) -> str:
    return _TOPIC_MAP.get(event_type, "stumpy.vara.bridge")


# ── Public API ────────────────────────────────────────────────────────────── #

def emit_epistemic_event(
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    source: str = "stumpy",
) -> EpistemicEventEnvelope:
    """
    Emit an epistemic event onto the shared stumpy/vara governance bus.

    Preserved original function signature; now wraps into a typed envelope,
    resolves the correct topic, and puts the message on stumpy_event_queue.
    """
    topic = _resolve_topic(event_type)
    envelope = EpistemicEventEnvelope(
        source=source,
        event_type=event_type,
        topic=topic,
        payload=payload or {},
    )
    try:
        stumpy_event_queue.put_nowait(envelope.to_dict())
    except Exception:
        pass  # bus unavailability must never crash the caller
    return envelope
