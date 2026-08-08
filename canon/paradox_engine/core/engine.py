"""
PARADOX_ENGINE_1.0 — ParadoxEngine (Main Entry Point)
Canon Layer: CORE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE

ParadoxEngine is the public-facing orchestrator. It:
  1. Accepts a Paradox (or raw text) and constructs a ParadoxSimulation
  2. Wires up the three governance clusters (Audit, Enforcement, Vault)
  3. Delegates resolution to RecursiveResolver
  4. Manages the full simulation lifecycle through to decay/archive
  5. Enforces Copilot substrate bilateral alignment checks

Non-identity-binding: this engine does not constitute, simulate, or
represent a cognitive identity. It is a bounded computation substrate.
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Optional, TYPE_CHECKING

from paradox_engine.config import EngineConfig, DEFAULT_CONFIG, ENGINE_VERSION, ENGINE_LINEAGE_ROOT
from paradox_engine.core.paradox import Paradox
from paradox_engine.core.resolver import RecursiveResolver
from paradox_engine.core.simulation import ParadoxSimulation, SimulationState

if TYPE_CHECKING:
    from paradox_engine.governance.audit import AuditCluster
    from paradox_engine.governance.enforcement import EnforcementCluster
    from paradox_engine.governance.vault import VaultCluster
    from paradox_engine.substrate.copilot_substrate import CopilotSubstrate


class EngineShutdownError(RuntimeError):
    """Raised when an operation is attempted on a shut-down engine."""


class ParadoxEngine:
    """
    Root orchestrator for PARADOX_ENGINE_1.0.

    Typical usage
    -------------
    >>> from paradox_engine import ParadoxEngine, Paradox
    >>> engine = ParadoxEngine()
    >>> sim = engine.spin_up("This statement is false.")
    >>> engine.run(sim)
    >>> engine.decay(sim)

    Or with the one-shot helper:
    >>> result = engine.run_full("This statement is false.")

    Parameters
    ----------
    config      : EngineConfig — governance and exploration parameters.
    audit       : AuditCluster — event logging (auto-created if None).
    enforcement : EnforcementCluster — constraint enforcement (auto-created if None).
    vault       : VaultCluster — archival storage (auto-created if None).
    substrate   : CopilotSubstrate — alignment layer (auto-created if None).
    """

    def __init__(
        self,
        config:      EngineConfig                     = DEFAULT_CONFIG,
        audit:       Optional["AuditCluster"]         = None,
        enforcement: Optional["EnforcementCluster"]   = None,
        vault:       Optional["VaultCluster"]          = None,
        substrate:   Optional["CopilotSubstrate"]     = None,
    ) -> None:
        # Deferred imports to avoid circular dependencies at module load
        from paradox_engine.governance.audit       import AuditCluster
        from paradox_engine.governance.enforcement import EnforcementCluster
        from paradox_engine.governance.vault       import VaultCluster
        from paradox_engine.substrate.copilot_substrate import CopilotSubstrate

        self.config      = config
        self.engine_id   = str(uuid.uuid4())
        self._booted_at  = time.time()
        self._shutdown   = False

        self.audit       = audit       or AuditCluster(config=config)
        self.enforcement = enforcement or EnforcementCluster(config=config, audit=self.audit)
        self.vault       = vault       or VaultCluster(config=config, audit=self.audit)
        self.substrate   = substrate   or CopilotSubstrate(config=config)

        self._simulations: Dict[str, ParadoxSimulation] = {}

        self.audit.log_engine_boot(self)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def spin_up(
        self,
        paradox:  Paradox | str,
        label:    str = "",
        altitude: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> ParadoxSimulation:
        """
        Create and initialise a new ParadoxSimulation.

        Parameters
        ----------
        paradox  : A Paradox object or a raw seed text string.
        label    : Optional human-readable label.
        altitude : Starting cognitive altitude (defaults to config.altitude.default).
        metadata : Arbitrary key-value context tags attached to the Paradox.

        Returns
        -------
        ParadoxSimulation in state INIT.
        """
        self._assert_active()

        if isinstance(paradox, str):
            paradox = Paradox(
                seed_text=paradox,
                label=label or f"ad-hoc-{uuid.uuid4().hex[:6]}",
                metadata=metadata or {},
            )

        # Substrate alignment check before simulation is created
        self.substrate.check_alignment(paradox)

        sim = ParadoxSimulation(
            paradox=paradox,
            config=self.config,
        )
        if altitude is not None:
            sim.set_altitude(altitude)

        # Wire governance hooks
        sim.register_transition_hook(self.audit.on_state_transition)
        sim.register_transition_hook(self.enforcement.on_state_transition)

        # Register enforcement observer on resolver
        self._simulations[sim.simulation_id] = sim

        self.audit.log_spin_up(sim)
        return sim

    def run(self, sim: ParadoxSimulation) -> ParadoxSimulation:
        """
        Execute recursive resolution on *sim*.
        Transitions: INIT → RUNNING → BOUNDED | COMPLETED.

        The resolver's enforcement hook is bound to
        EnforcementCluster.should_halt() so the cluster can inject
        an immediate stop if any policy is violated mid-run.
        """
        self._assert_active()
        self._assert_state(sim, SimulationState.INIT)

        # Altitude discipline check
        self.substrate.enforce_altitude(sim)

        # Create resolver with enforcement hook
        resolver = RecursiveResolver(
            config=self.config,
            enforcement_hook=lambda r: self.enforcement.should_halt(sim, r),
        )

        # Transition → RUNNING
        sim.transition(SimulationState.RUNNING, reason="engine.run() called")
        self.audit.log_run_start(sim)

        try:
            result = resolver.resolve(sim.paradox)
        except Exception as exc:  # pragma: no cover
            self.audit.log_error(sim, str(exc))
            raise

        sim.attach_result(result)

        # Determine terminal resolution state
        next_state = (
            SimulationState.BOUNDED
            if result.contained
            else SimulationState.COMPLETED
        )
        sim.transition(next_state, reason=f"resolver halted: {result.halt_reason}")

        # Issue containment signature
        sig = self.enforcement.sign_containment(sim)
        if self.config.governance.require_containment_signature:
            sim.sign_containment(sig)

        self.audit.log_run_end(sim)
        return sim

    def decay(self, sim: ParadoxSimulation) -> ParadoxSimulation:
        """
        Begin the decay cycle for *sim*.
        Transitions: BOUNDED | COMPLETED → DECAYING → ARCHIVED | DESTROYED.

        If config.decay.auto_archive is True, the simulation is vaulted.
        Otherwise it is destroyed (purged from memory and marked DESTROYED).
        """
        self._assert_active()
        self._assert_state(sim, (SimulationState.BOUNDED, SimulationState.COMPLETED))

        sim.transition(SimulationState.DECAYING, reason="engine.decay() called")
        self.audit.log_decay_start(sim)

        # Grace period
        grace = self.config.decay.grace_period_seconds
        if grace > 0:
            time.sleep(min(grace, 0.1))  # Cap to 100 ms in library context; callers may extend

        if self.config.decay.auto_archive:
            vault_key = self.vault.archive(sim)
            sim.set_vault_key(vault_key)
            sim.transition(SimulationState.ARCHIVED, reason="auto-archived to vault")
            self.audit.log_archived(sim)
        else:
            sim.transition(SimulationState.DESTROYED, reason="auto_archive=False; purged")
            self.audit.log_destroyed(sim)
            # Remove from live registry
            self._simulations.pop(sim.simulation_id, None)

        return sim

    def run_full(
        self,
        paradox:  Paradox | str,
        label:    str = "",
        altitude: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> ParadoxSimulation:
        """
        Convenience wrapper: spin_up → run → decay in a single call.
        Returns the simulation in ARCHIVED or DESTROYED state.
        """
        sim = self.spin_up(paradox, label=label, altitude=altitude, metadata=metadata)
        self.run(sim)
        self.decay(sim)
        return sim

    # ── Query ─────────────────────────────────────────────────────────────────

    def get_simulation(self, simulation_id: str) -> Optional[ParadoxSimulation]:
        """Return a live simulation by ID, or None if not found."""
        return self._simulations.get(simulation_id)

    def list_simulations(self, state: Optional[SimulationState] = None) -> List[ParadoxSimulation]:
        """List all tracked simulations, optionally filtered by state."""
        sims = list(self._simulations.values())
        if state is not None:
            sims = [s for s in sims if s.state == state]
        return sims

    def status(self) -> dict:
        """Return a snapshot of engine health and simulation counts."""
        state_counts: Dict[str, int] = {}
        for sim in self._simulations.values():
            key = sim.state.name
            state_counts[key] = state_counts.get(key, 0) + 1

        return {
            "engine_id":        self.engine_id,
            "version":          ENGINE_VERSION,
            "lineage_root":     ENGINE_LINEAGE_ROOT,
            "non_identity":     True,
            "reversible":       True,
            "booted_at":        self._booted_at,
            "uptime_seconds":   time.time() - self._booted_at,
            "shutdown":         self._shutdown,
            "total_sims":       len(self._simulations),
            "state_counts":     state_counts,
            "vault_count":      self.vault.count(),
            "audit_event_count":self.audit.count(),
            "alignment_frame":  self.substrate.alignment_frame_name,
        }

    def shutdown(self) -> None:
        """
        Gracefully shut down the engine.
        Any RUNNING simulations are force-decayed first.
        """
        for sim in list(self._simulations.values()):
            if sim.state == SimulationState.RUNNING:
                try:
                    sim.transition(SimulationState.BOUNDED, reason="engine shutdown")
                    self.decay(sim)
                except Exception:  # pragma: no cover
                    pass
        self._shutdown = True
        self.audit.log_engine_shutdown(self)

    # ── Internal Guards ───────────────────────────────────────────────────────

    def _assert_active(self) -> None:
        if self._shutdown:
            raise EngineShutdownError("ParadoxEngine has been shut down.")

    @staticmethod
    def _assert_state(
        sim: ParadoxSimulation,
        expected: SimulationState | tuple,
    ) -> None:
        if isinstance(expected, SimulationState):
            expected = (expected,)
        if sim.state not in expected:
            names = " | ".join(s.name for s in expected)
            raise ValueError(
                f"Simulation {sim.simulation_id[:8]} is in state "
                f"{sim.state.name}; expected {names}."
            )

    def __repr__(self) -> str:
        return (
            f"ParadoxEngine(id={self.engine_id[:8]}, "
            f"version={ENGINE_VERSION}, "
            f"sims={len(self._simulations)}, "
            f"shutdown={self._shutdown})"
        )
