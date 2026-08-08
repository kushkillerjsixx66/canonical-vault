"""
PARADOX_ENGINE_1.0 — Enforcement Cluster
Canon Layer: GOVERNANCE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE

EnforcementCluster is the constraint authority for the engine.
It can:
  - Inspect a running RecursiveResolver and demand an immediate halt
  - React to state transitions and raise policy violations
  - Issue containment signatures for resolved simulations
  - Track and report all violations

Enforcement is non-negotiable. When should_halt() returns True,
the resolver stops on the next iteration — no override path exists.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from paradox_engine.config import EngineConfig, DEFAULT_CONFIG

if TYPE_CHECKING:
    from paradox_engine.core.resolver import RecursiveResolver
    from paradox_engine.core.simulation import ParadoxSimulation, StateTransitionEvent
    from paradox_engine.governance.audit import AuditCluster


# ── Violation ─────────────────────────────────────────────────────────────────

class ViolationCode(Enum):
    DEPTH_OVERFLOW       = auto()
    ITERATION_OVERFLOW   = auto()
    BRANCH_OVERFLOW      = auto()
    RUNTIME_OVERFLOW     = auto()
    DRIFT_EXCEEDED       = auto()
    INFLATION_EXCEEDED   = auto()
    ALTITUDE_VIOLATION   = auto()
    ALIGNMENT_FAILURE    = auto()
    ILLEGAL_TRANSITION   = auto()


@dataclass
class ConstraintViolation:
    """A record of a single policy violation detected by EnforcementCluster."""
    violation_id:   str            = field(default_factory=lambda: str(uuid.uuid4()))
    code:           ViolationCode  = ViolationCode.DEPTH_OVERFLOW
    simulation_id:  Optional[str]  = None
    detected_at:    float          = field(default_factory=time.time)
    detail:         str            = ""
    halt_issued:    bool           = False

    def to_dict(self) -> dict:
        return {
            "violation_id":  self.violation_id,
            "code":          self.code.name,
            "simulation_id": self.simulation_id,
            "detected_at":   self.detected_at,
            "detail":        self.detail,
            "halt_issued":   self.halt_issued,
        }


# ── Containment Signature ─────────────────────────────────────────────────────

def _make_signature(sim: "ParadoxSimulation") -> str:
    """
    Produce a deterministic containment signature for a simulation.
    SHA-256 over (simulation_id + paradox_id + halt_reason + timestamp).
    """
    result = sim.result
    halt   = result.halt_reason if result else "NO_RESULT"
    raw    = f"{sim.simulation_id}:{sim.paradox.paradox_id}:{halt}:{sim.created_at}"
    return "CSIG:" + hashlib.sha256(raw.encode()).hexdigest()[:48]


# ── Enforcement Cluster ───────────────────────────────────────────────────────

class EnforcementCluster:
    """
    Governance authority that observes and constrains active simulations.

    should_halt() is called by RecursiveResolver on every iteration
    as an enforcement hook. When it returns True, the resolver halts
    immediately with HaltReason.ENFORCEMENT_HALT.

    Parameters
    ----------
    config  : EngineConfig
    audit   : AuditCluster — receives violation events.
    """

    def __init__(
        self,
        config: EngineConfig               = DEFAULT_CONFIG,
        audit:  Optional["AuditCluster"]   = None,
    ) -> None:
        self._config     = config
        self._audit      = audit
        self._violations: List[ConstraintViolation] = []
        self._halt_flags: Dict[str, bool]            = {}  # sim_id → halt requested
        self._signatures: Dict[str, str]             = {}  # sim_id → containment sig

    # ── Resolver Hook ─────────────────────────────────────────────────────────

    def should_halt(
        self,
        sim:      "ParadoxSimulation",
        resolver: "RecursiveResolver",
    ) -> bool:
        """
        Called by the resolver on every iteration.
        Returns True to demand an immediate halt.

        Checks (in order):
          1. Manual halt flag set externally
          2. Altitude ceiling violation
        The resolver itself checks depth/time/drift/inflation limits
        natively — this hook adds governance-layer checks on top.
        """
        sim_id = sim.simulation_id

        # External halt flag
        if self._halt_flags.get(sim_id):
            self._record_violation(
                ViolationCode.ILLEGAL_TRANSITION,
                sim_id,
                "External halt flag set.",
                halt_issued=True,
            )
            return True

        # Altitude ceiling
        if sim.altitude > self._config.altitude.ceiling:
            self._record_violation(
                ViolationCode.ALTITUDE_VIOLATION,
                sim_id,
                f"Altitude {sim.altitude} exceeds ceiling {self._config.altitude.ceiling}.",
                halt_issued=True,
            )
            return True

        return False

    def request_halt(self, sim: "ParadoxSimulation", reason: str = "") -> None:
        """
        Externally request an immediate halt for *sim* on the next
        resolver iteration.
        """
        self._halt_flags[sim.simulation_id] = True
        self._record_violation(
            ViolationCode.ILLEGAL_TRANSITION,
            sim.simulation_id,
            f"Manual halt requested: {reason}",
            halt_issued=True,
        )

    def clear_halt(self, sim: "ParadoxSimulation") -> None:
        """Clear a previously set halt flag (e.g. after the sim has stopped)."""
        self._halt_flags.pop(sim.simulation_id, None)

    # ── State Transition Hook ─────────────────────────────────────────────────

    def on_state_transition(self, event: "StateTransitionEvent") -> None:
        """
        Registered as a transition hook on every simulation.
        Validates that transitions are governance-compliant.
        Currently a no-op policy check (override to extend).
        """
        # Future: add policy assertions per transition pair here.
        pass

    # ── Containment Signing ───────────────────────────────────────────────────

    def sign_containment(self, sim: "ParadoxSimulation") -> str:
        """
        Issue and record a containment signature for a completed or
        bounded simulation. Idempotent — returns the same sig if already
        signed.
        """
        if sim.simulation_id in self._signatures:
            return self._signatures[sim.simulation_id]

        sig = _make_signature(sim)
        self._signatures[sim.simulation_id] = sig

        if self._audit:
            self._audit.log_enforcement_action(
                sim,
                "CONTAINMENT_SIGNED",
                {"signature": sig},
            )
        return sig

    def verify_signature(self, sim: "ParadoxSimulation") -> bool:
        """
        Verify that the containment signature stored on *sim* matches
        what this cluster would issue. Returns False if unsigned or tampered.
        """
        stored = sim.containment_signature
        if not stored:
            return False
        expected = _make_signature(sim)
        return stored == expected

    # ── Policy Checks ─────────────────────────────────────────────────────────

    def assert_altitude(self, sim: "ParadoxSimulation") -> None:
        """
        Raise ValueError if the simulation's altitude is outside bounds.
        Called by the substrate before resolution begins.
        """
        lo = self._config.altitude.floor
        hi = self._config.altitude.ceiling
        alt = sim.altitude
        if not (lo <= alt <= hi):
            v = self._record_violation(
                ViolationCode.ALTITUDE_VIOLATION,
                sim.simulation_id,
                f"Altitude {alt} out of bounds [{lo}, {hi}].",
                halt_issued=False,
            )
            raise ValueError(
                f"Altitude violation ({v.code.name}): {v.detail}"
            )

    # ── Query ─────────────────────────────────────────────────────────────────

    def violations(
        self,
        simulation_id: Optional[str] = None,
    ) -> List[ConstraintViolation]:
        if simulation_id:
            return [v for v in self._violations if v.simulation_id == simulation_id]
        return list(self._violations)

    def violation_count(self, simulation_id: Optional[str] = None) -> int:
        return len(self.violations(simulation_id))

    def halts_issued(self) -> int:
        return sum(1 for v in self._violations if v.halt_issued)

    def report(self) -> dict:
        return {
            "total_violations": len(self._violations),
            "halts_issued":     self.halts_issued(),
            "signatures_issued": len(self._signatures),
            "violations_by_code": {
                code.name: sum(1 for v in self._violations if v.code == code)
                for code in ViolationCode
            },
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    def _record_violation(
        self,
        code:          ViolationCode,
        simulation_id: Optional[str],
        detail:        str,
        halt_issued:   bool = False,
    ) -> ConstraintViolation:
        v = ConstraintViolation(
            code=code,
            simulation_id=simulation_id,
            detail=detail,
            halt_issued=halt_issued,
        )
        self._violations.append(v)

        if self._audit and simulation_id:
            # We need a minimal sim-like object for the audit signature;
            # use a lightweight proxy approach
            class _SimProxy:
                def __init__(self, sid: str) -> None:
                    self.simulation_id = sid
                    self.result        = None

            self._audit.log_enforcement_action(
                _SimProxy(simulation_id),  # type: ignore[arg-type]
                code.name,
                {"detail": detail, "halt_issued": halt_issued},
            )
        return v

    def __repr__(self) -> str:
        return (
            f"EnforcementCluster("
            f"violations={len(self._violations)}, "
            f"halts={self.halts_issued()}, "
            f"signatures={len(self._signatures)})"
        )
