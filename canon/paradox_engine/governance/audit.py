"""
PARADOX_ENGINE_1.0 — Audit Cluster
Canon Layer: GOVERNANCE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE

AuditCluster is the observability backbone of the engine.
It records every significant event — engine boot, simulation
lifecycle transitions, resolver completions, enforcement actions,
vault operations, and errors — as structured AuditEvent objects.

Events are held in an in-memory ring buffer (configurable) and
can be exported as JSON for persistent storage or external audit
systems.
"""

from __future__ import annotations

import json
import time
import uuid
from collections import deque
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from typing import TYPE_CHECKING, Deque, Dict, List, Optional, Any

from paradox_engine.config import EngineConfig, DEFAULT_CONFIG

if TYPE_CHECKING:
    from paradox_engine.core.simulation import ParadoxSimulation, StateTransitionEvent


# ── Event Taxonomy ─────────────────────────────────────────────────────────────

class AuditEventType(Enum):
    ENGINE_BOOT          = auto()
    ENGINE_SHUTDOWN      = auto()
    SIMULATION_SPIN_UP   = auto()
    SIMULATION_RUN_START = auto()
    SIMULATION_RUN_END   = auto()
    SIMULATION_DECAY     = auto()
    SIMULATION_ARCHIVED  = auto()
    SIMULATION_DESTROYED = auto()
    STATE_TRANSITION     = auto()
    ENFORCEMENT_ACTION   = auto()
    VAULT_WRITE          = auto()
    VAULT_READ           = auto()
    ALIGNMENT_CHECK      = auto()
    ALTITUDE_CHECK       = auto()
    ERROR                = auto()
    GENERIC              = auto()


# ── Audit Event ────────────────────────────────────────────────────────────────

@dataclass
class AuditEvent:
    """
    An immutable record of a single significant engine event.

    Attributes
    ----------
    event_id        : UUID of this event.
    event_type      : AuditEventType enum value.
    timestamp       : Unix epoch float.
    simulation_id   : Associated simulation, if applicable.
    engine_id       : Originating engine instance.
    payload         : Arbitrary structured data dict.
    message         : Human-readable description.
    """
    event_id:      str
    event_type:    AuditEventType
    timestamp:     float
    engine_id:     str
    simulation_id: Optional[str]
    message:       str
    payload:       Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_id":      self.event_id,
            "event_type":    self.event_type.name,
            "timestamp":     self.timestamp,
            "engine_id":     self.engine_id,
            "simulation_id": self.simulation_id,
            "message":       self.message,
            "payload":       self.payload,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    def __repr__(self) -> str:
        sim = f" sim={self.simulation_id[:8]}" if self.simulation_id else ""
        return f"AuditEvent({self.event_type.name}{sim} @ {self.timestamp:.3f})"


def _make_event(
    event_type:    AuditEventType,
    engine_id:     str,
    message:       str,
    simulation_id: Optional[str] = None,
    payload:       Optional[dict] = None,
) -> AuditEvent:
    return AuditEvent(
        event_id      = str(uuid.uuid4()),
        event_type    = event_type,
        timestamp     = time.time(),
        engine_id     = engine_id,
        simulation_id = simulation_id,
        message       = message,
        payload       = payload or {},
    )


# ── Audit Cluster ──────────────────────────────────────────────────────────────

class AuditCluster:
    """
    Central event log for a ParadoxEngine instance.

    Stores events in a capped deque (ring buffer).  When the buffer
    is full, the oldest events are silently dropped (FIFO).
    All events can be exported as a list of dicts or a newline-
    delimited JSON string for downstream ingestion.

    Parameters
    ----------
    config      : EngineConfig
    max_events  : Maximum events held in memory. Default 10 000.
    """

    DEFAULT_MAX_EVENTS = 10_000

    def __init__(
        self,
        config:     EngineConfig = DEFAULT_CONFIG,
        max_events: int          = DEFAULT_MAX_EVENTS,
    ) -> None:
        self._config    = config
        self._max       = max_events
        self._buffer:   Deque[AuditEvent] = deque(maxlen=max_events)
        self._engine_id = "UNBOUND"   # Set on engine boot

    # ── Engine Lifecycle Events ────────────────────────────────────────────────

    def log_engine_boot(self, engine: Any) -> AuditEvent:
        self._engine_id = engine.engine_id
        ev = _make_event(
            AuditEventType.ENGINE_BOOT,
            self._engine_id,
            f"ParadoxEngine {engine.engine_id[:8]} booted.",
            payload={
                "version":      engine.config.__class__.__name__,
                "config_label": engine.config.deployment_label,
            },
        )
        return self._record(ev)

    def log_engine_shutdown(self, engine: Any) -> AuditEvent:
        ev = _make_event(
            AuditEventType.ENGINE_SHUTDOWN,
            self._engine_id,
            f"ParadoxEngine {engine.engine_id[:8]} shut down.",
        )
        return self._record(ev)

    # ── Simulation Lifecycle Events ────────────────────────────────────────────

    def log_spin_up(self, sim: "ParadoxSimulation") -> AuditEvent:
        ev = _make_event(
            AuditEventType.SIMULATION_SPIN_UP,
            self._engine_id,
            f"Simulation {sim.simulation_id[:8]} spun up for paradox '{sim.paradox.label}'.",
            simulation_id=sim.simulation_id,
            payload={
                "paradox_id":   sim.paradox.paradox_id,
                "paradox_label": sim.paradox.label,
                "seed_text":    sim.paradox.seed_text[:120],
                "altitude":     sim.altitude,
            },
        )
        return self._record(ev)

    def log_run_start(self, sim: "ParadoxSimulation") -> AuditEvent:
        ev = _make_event(
            AuditEventType.SIMULATION_RUN_START,
            self._engine_id,
            f"Simulation {sim.simulation_id[:8]} resolver started.",
            simulation_id=sim.simulation_id,
        )
        return self._record(ev)

    def log_run_end(self, sim: "ParadoxSimulation") -> AuditEvent:
        result = sim.result
        payload: dict = {"state": sim.state.name}
        if result:
            payload.update(result.summary())
        ev = _make_event(
            AuditEventType.SIMULATION_RUN_END,
            self._engine_id,
            f"Simulation {sim.simulation_id[:8]} resolver finished: {sim.state.name}.",
            simulation_id=sim.simulation_id,
            payload=payload,
        )
        return self._record(ev)

    def log_decay_start(self, sim: "ParadoxSimulation") -> AuditEvent:
        ev = _make_event(
            AuditEventType.SIMULATION_DECAY,
            self._engine_id,
            f"Simulation {sim.simulation_id[:8]} entering decay.",
            simulation_id=sim.simulation_id,
        )
        return self._record(ev)

    def log_archived(self, sim: "ParadoxSimulation") -> AuditEvent:
        ev = _make_event(
            AuditEventType.SIMULATION_ARCHIVED,
            self._engine_id,
            f"Simulation {sim.simulation_id[:8]} archived (vault key: {sim.vault_key}).",
            simulation_id=sim.simulation_id,
            payload={"vault_key": sim.vault_key},
        )
        return self._record(ev)

    def log_destroyed(self, sim: "ParadoxSimulation") -> AuditEvent:
        ev = _make_event(
            AuditEventType.SIMULATION_DESTROYED,
            self._engine_id,
            f"Simulation {sim.simulation_id[:8]} destroyed (purged).",
            simulation_id=sim.simulation_id,
        )
        return self._record(ev)

    def log_error(self, sim: "ParadoxSimulation", error: str) -> AuditEvent:
        ev = _make_event(
            AuditEventType.ERROR,
            self._engine_id,
            f"Error in simulation {sim.simulation_id[:8]}: {error}",
            simulation_id=sim.simulation_id,
            payload={"error": error},
        )
        return self._record(ev)

    # ── Transition Hook ────────────────────────────────────────────────────────

    def on_state_transition(self, event: "StateTransitionEvent") -> None:
        """Registered as a transition hook on every simulation."""
        ev = _make_event(
            AuditEventType.STATE_TRANSITION,
            self._engine_id,
            (
                f"Simulation {event.simulation_id[:8]} transitioned "
                f"{event.from_state.name} → {event.to_state.name}."
            ),
            simulation_id=event.simulation_id,
            payload={
                "from_state": event.from_state.name,
                "to_state":   event.to_state.name,
                "reason":     event.reason,
            },
        )
        self._record(ev)

    # ── Governance Events ──────────────────────────────────────────────────────

    def log_enforcement_action(
        self,
        sim:    "ParadoxSimulation",
        action: str,
        detail: Optional[dict] = None,
    ) -> AuditEvent:
        ev = _make_event(
            AuditEventType.ENFORCEMENT_ACTION,
            self._engine_id,
            f"Enforcement action on simulation {sim.simulation_id[:8]}: {action}.",
            simulation_id=sim.simulation_id,
            payload={"action": action, **(detail or {})},
        )
        return self._record(ev)

    def log_vault_write(self, vault_key: str, sim_id: str) -> AuditEvent:
        ev = _make_event(
            AuditEventType.VAULT_WRITE,
            self._engine_id,
            f"Vault write: key={vault_key}, sim={sim_id[:8]}.",
            simulation_id=sim_id,
            payload={"vault_key": vault_key},
        )
        return self._record(ev)

    def log_vault_read(self, vault_key: str) -> AuditEvent:
        ev = _make_event(
            AuditEventType.VAULT_READ,
            self._engine_id,
            f"Vault read: key={vault_key}.",
            payload={"vault_key": vault_key},
        )
        return self._record(ev)

    def log_alignment_check(self, passed: bool, detail: str) -> AuditEvent:
        ev = _make_event(
            AuditEventType.ALIGNMENT_CHECK,
            self._engine_id,
            f"Bilateral alignment check {'PASSED' if passed else 'FAILED'}: {detail}",
            payload={"passed": passed, "detail": detail},
        )
        return self._record(ev)

    def log_altitude_check(
        self, sim: "ParadoxSimulation", altitude: int, ceiling: int
    ) -> AuditEvent:
        ev = _make_event(
            AuditEventType.ALTITUDE_CHECK,
            self._engine_id,
            f"Altitude check for sim {sim.simulation_id[:8]}: {altitude}/{ceiling}.",
            simulation_id=sim.simulation_id,
            payload={"altitude": altitude, "ceiling": ceiling},
        )
        return self._record(ev)

    def log_generic(self, message: str, payload: Optional[dict] = None) -> AuditEvent:
        ev = _make_event(
            AuditEventType.GENERIC,
            self._engine_id,
            message,
            payload=payload or {},
        )
        return self._record(ev)

    # ── Query ──────────────────────────────────────────────────────────────────

    def count(self) -> int:
        return len(self._buffer)

    def all_events(self) -> List[AuditEvent]:
        return list(self._buffer)

    def events_for_simulation(self, simulation_id: str) -> List[AuditEvent]:
        return [e for e in self._buffer if e.simulation_id == simulation_id]

    def events_by_type(self, event_type: AuditEventType) -> List[AuditEvent]:
        return [e for e in self._buffer if e.event_type == event_type]

    def export_json(self) -> str:
        """Export all events as newline-delimited JSON."""
        return "\n".join(e.to_json() for e in self._buffer)

    def export_dicts(self) -> List[dict]:
        return [e.to_dict() for e in self._buffer]

    def clear(self) -> int:
        """Purge all events. Returns count purged."""
        n = len(self._buffer)
        self._buffer.clear()
        return n

    # ── Internal ───────────────────────────────────────────────────────────────

    def _record(self, event: AuditEvent) -> AuditEvent:
        self._buffer.append(event)
        return event

    def __repr__(self) -> str:
        return f"AuditCluster(events={len(self._buffer)}, max={self._max})"
