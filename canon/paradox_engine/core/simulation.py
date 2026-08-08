"""
PARADOX_ENGINE_1.0 — Simulation Lifecycle Manager
Canon Layer: CORE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE

Defines SimulationState and ParadoxSimulation — the stateful
wrapper that governs the full lifecycle of a single paradox run:

  INIT → RUNNING → BOUNDED | COMPLETED → DECAYING → ARCHIVED | DESTROYED
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, List, Optional

from paradox_engine.config import EngineConfig, DEFAULT_CONFIG
from paradox_engine.core.paradox import Paradox
from paradox_engine.core.resolver import ResolutionResult

if TYPE_CHECKING:
    from paradox_engine.governance.audit import AuditCluster
    from paradox_engine.governance.enforcement import EnforcementCluster
    from paradox_engine.governance.vault import VaultCluster


# ── State Machine ─────────────────────────────────────────────────────────────

class SimulationState(Enum):
    """
    Ordered lifecycle states for a ParadoxSimulation.
    Transitions are strictly linear; no state may be revisited.

    INIT        → Simulation object created; not yet started.
    RUNNING     → RecursiveResolver is actively exploring.
    BOUNDED     → Resolution halted by a containment constraint.
    COMPLETED   → Resolution terminated cleanly (all cycles closed).
    DECAYING    → Decay grace period in progress; memory being released.
    ARCHIVED    → Vaulted; read-only access permitted.
    DESTROYED   → Purged; no access.
    """
    INIT      = auto()
    RUNNING   = auto()
    BOUNDED   = auto()
    COMPLETED = auto()
    DECAYING  = auto()
    ARCHIVED  = auto()
    DESTROYED = auto()


_VALID_TRANSITIONS: dict[SimulationState, set[SimulationState]] = {
    SimulationState.INIT:      {SimulationState.RUNNING},
    SimulationState.RUNNING:   {SimulationState.BOUNDED, SimulationState.COMPLETED},
    SimulationState.BOUNDED:   {SimulationState.DECAYING},
    SimulationState.COMPLETED: {SimulationState.DECAYING},
    SimulationState.DECAYING:  {SimulationState.ARCHIVED, SimulationState.DESTROYED},
    SimulationState.ARCHIVED:  set(),   # Terminal: vault owns it
    SimulationState.DESTROYED: set(),   # Terminal: gone
}


class IllegalStateTransition(RuntimeError):
    pass


# ── State Change Event ────────────────────────────────────────────────────────

@dataclass
class StateTransitionEvent:
    simulation_id: str
    from_state:    SimulationState
    to_state:      SimulationState
    timestamp:     float = field(default_factory=time.time)
    reason:        str   = ""


# ── Simulation ────────────────────────────────────────────────────────────────

@dataclass
class ParadoxSimulation:
    """
    Stateful wrapper for a single paradox exploration run.

    Created by ParadoxEngine.spin_up(). Owns:
      - The source Paradox object
      - The current SimulationState
      - The ResolutionResult (available after RUNNING completes)
      - The full transition history
      - The containment signature (set by EnforcementCluster)

    External clusters (Audit, Vault, Enforcement) interact with
    simulations through the hooks registered on spin-up.
    """
    paradox:         Paradox
    config:          EngineConfig                   = field(default_factory=lambda: DEFAULT_CONFIG)
    simulation_id:   str                            = field(default_factory=lambda: str(uuid.uuid4()))
    created_at:      float                          = field(default_factory=time.time)

    # Runtime-populated fields
    _state:               SimulationState           = field(default=SimulationState.INIT, init=False, repr=False)
    _result:              Optional[ResolutionResult] = field(default=None,  init=False, repr=False)
    _containment_sig:     Optional[str]              = field(default=None,  init=False, repr=False)
    _transition_history:  List[StateTransitionEvent] = field(default_factory=list, init=False, repr=False)
    _transition_hooks:    List[Callable[[StateTransitionEvent], None]] = field(
        default_factory=list, init=False, repr=False
    )
    _start_time:          Optional[float]            = field(default=None, init=False, repr=False)
    _end_time:            Optional[float]            = field(default=None, init=False, repr=False)
    _decay_start:         Optional[float]            = field(default=None, init=False, repr=False)
    _vault_key:           Optional[str]              = field(default=None, init=False, repr=False)
    _altitude:            int                        = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._altitude = self.config.altitude.default

    # ── State Access ──────────────────────────────────────────────────────────

    @property
    def state(self) -> SimulationState:
        return self._state

    @property
    def result(self) -> Optional[ResolutionResult]:
        return self._result

    @property
    def containment_signature(self) -> Optional[str]:
        return self._containment_sig

    @property
    def vault_key(self) -> Optional[str]:
        return self._vault_key

    @property
    def altitude(self) -> int:
        return self._altitude

    @property
    def elapsed_seconds(self) -> Optional[float]:
        if self._start_time is None:
            return None
        end = self._end_time or time.monotonic()
        return end - self._start_time

    @property
    def is_terminal(self) -> bool:
        return self._state in (SimulationState.ARCHIVED, SimulationState.DESTROYED)

    @property
    def transition_history(self) -> List[StateTransitionEvent]:
        return list(self._transition_history)

    # ── State Transitions ─────────────────────────────────────────────────────

    def transition(self, to: SimulationState, reason: str = "") -> StateTransitionEvent:
        """
        Advance the simulation to *to*.
        Raises IllegalStateTransition if the move is not permitted.
        Fires all registered transition hooks synchronously.
        """
        allowed = _VALID_TRANSITIONS.get(self._state, set())
        if to not in allowed:
            raise IllegalStateTransition(
                f"Cannot transition {self._state.name} → {to.name} "
                f"for simulation {self.simulation_id[:8]}"
            )

        event = StateTransitionEvent(
            simulation_id=self.simulation_id,
            from_state=self._state,
            to_state=to,
            reason=reason,
        )
        self._state = to
        self._transition_history.append(event)

        # Side-effects per target state
        if to == SimulationState.RUNNING:
            self._start_time = time.monotonic()
        elif to in (SimulationState.BOUNDED, SimulationState.COMPLETED):
            self._end_time = time.monotonic()
        elif to == SimulationState.DECAYING:
            self._decay_start = time.time()

        for hook in self._transition_hooks:
            hook(event)

        return event

    def register_transition_hook(self, hook: Callable[[StateTransitionEvent], None]) -> None:
        """Register a callback that fires on every state transition."""
        self._transition_hooks.append(hook)

    # ── Result & Signature ────────────────────────────────────────────────────

    def attach_result(self, result: ResolutionResult) -> None:
        """Attach the ResolutionResult produced by the resolver."""
        if self._result is not None:
            raise RuntimeError("Result already attached to simulation.")
        self._result = result

    def sign_containment(self, signature: str) -> None:
        """
        Record the containment signature issued by EnforcementCluster.
        Required when config.governance.require_containment_signature = True.
        """
        self._containment_sig = signature

    def set_vault_key(self, key: str) -> None:
        self._vault_key = key

    def set_altitude(self, altitude: int) -> None:
        """
        Adjust the cognitive altitude for this simulation.
        Bounded to [config.altitude.floor, config.altitude.ceiling].
        """
        lo = self.config.altitude.floor
        hi = self.config.altitude.ceiling
        self._altitude = max(lo, min(hi, altitude))

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_record(self) -> dict:
        """
        Produce a JSON-serialisable dict suitable for vaulting.
        All mutable runtime state is captured at the moment of the call.
        """
        result_summary = self._result.summary() if self._result else None
        return {
            "simulation_id":       self.simulation_id,
            "paradox_id":          self.paradox.paradox_id,
            "paradox_label":       self.paradox.label,
            "paradox_seed":        self.paradox.seed_text,
            "state":               self._state.name,
            "altitude":            self._altitude,
            "created_at":          self.created_at,
            "start_time":          self._start_time,
            "end_time":            self._end_time,
            "decay_start":         self._decay_start,
            "elapsed_seconds":     self.elapsed_seconds,
            "containment_sig":     self._containment_sig,
            "vault_key":           self._vault_key,
            "result":              result_summary,
            "transition_count":    len(self._transition_history),
            "transitions": [
                {
                    "from":      e.from_state.name,
                    "to":        e.to_state.name,
                    "timestamp": e.timestamp,
                    "reason":    e.reason,
                }
                for e in self._transition_history
            ],
        }

    def __repr__(self) -> str:
        return (
            f"ParadoxSimulation(id={self.simulation_id[:8]}, "
            f"state={self._state.name}, "
            f"paradox={self.paradox.label!r})"
        )
