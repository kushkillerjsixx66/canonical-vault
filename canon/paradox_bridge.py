"""
paradox_bridge.py
CDS-Ω1 ↔ Paradox Engine Integration Bridge

Wires the ParadoxEngine into the CDS-Ω1 CITL bus:

  • Subscribes to  canon.paradox.intake
  • For each CSP arriving on that topic:
      1. Extracts the dominant contradiction pair from the CMX
      2. Builds a seed proposition from the operator contradiction template
      3. Spins up a ParadoxSimulation (fast-config for operational use)
      4. Attaches the resolution result to a ParadoxIntelPacket (PIP)
      5. Publishes the PIP to canon.operator.dashboard for inspection
      6. Calls router.request_recursive_synthesis() to trigger
         constrained re-synthesis on the flagged domain pair

Subsystem ID : CDS-Ω1:PARADOX_BRIDGE
Lineage Root : CANON:LATTICE:PARADOX_ENGINE
"""

from __future__ import annotations

import asyncio
import logging
import sys
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

# ── CDS imports ─────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from citl import CITLBus, Message, Topic
from models import CSP, DomainID, EscalationPath, SynthesisType
from router import Router, RecursiveRequest
from canon_constants import (
    contradiction_template,
    expected_direction,
    DOMAIN_ID_MAP,
)

# ── Paradox Engine imports ───────────────────────────────────────────────────
# paradox_engine is a sub-package of cds/
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from paradox_engine import (
    ParadoxEngine,
    EngineConfig,
    ExplorationBounds,
    DecayPolicy,
    GovernancePolicy,
    SimulationState,
)

logger = logging.getLogger("cds.paradox_bridge")


# ── Operational Paradox Engine Config ────────────────────────────────────────

def _make_operational_config() -> EngineConfig:
    """
    Fast config for operational (non-test) use inside Canon.
    Tight runtime bounds so the bridge never stalls the CITL loop.
    """
    cfg = EngineConfig()
    cfg.exploration.max_depth           = 12
    cfg.exploration.max_iterations      = 64
    cfg.exploration.max_runtime_seconds = 8.0
    cfg.exploration.max_branches        = 64
    cfg.decay.grace_period_seconds      = 0.0   # no wait in pipeline context
    cfg.decay.auto_archive              = True
    cfg.governance.audit_all_branches   = True
    cfg.governance.require_containment_signature = True
    return cfg


def _make_test_config() -> EngineConfig:
    """Ultra-fast config for tests."""
    cfg = EngineConfig()
    cfg.exploration.max_depth           = 8
    cfg.exploration.max_iterations      = 32
    cfg.exploration.max_runtime_seconds = 5.0
    cfg.decay.grace_period_seconds      = 0.0
    cfg.decay.auto_archive              = True
    return cfg


# ── Paradox Intel Packet ─────────────────────────────────────────────────────

@dataclass
class ParadoxIntelPacket:
    """
    Output record produced by the bridge for each processed CSP.

    Carries the resolution metadata from the Paradox Engine back
    into the Canon operator dashboard.
    """
    type:              str   = "PIP"
    version:           str   = "1.0"
    subsystem_id:      str   = "CDS-Ω1:PARADOX_BRIDGE"

    # Source CSP context
    synthesis_id:      str   = ""
    source_domains:    list  = field(default_factory=list)
    contradiction_pair: tuple = field(default_factory=tuple)
    max_contradiction:  float = 0.0

    # Paradox seed
    seed_label:        str   = ""
    seed_text:         str   = ""

    # Engine resolution result
    simulation_id:     str   = ""
    simulation_state:  str   = ""
    halt_reason:       str   = ""
    contained:         bool  = False
    cycle_count:       int   = 0
    drift_score:       float = 0.0
    inflation_ratio:   float = 0.0
    elapsed_seconds:   float = 0.0
    containment_sig:   str   = ""
    vault_key:         str   = ""

    # Timestamps
    processed_at:      str   = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "type":              self.type,
            "version":           self.version,
            "subsystem_id":      self.subsystem_id,
            "synthesis_id":      self.synthesis_id,
            "source_domains":    self.source_domains,
            "contradiction_pair": list(self.contradiction_pair),
            "max_contradiction": self.max_contradiction,
            "seed_label":        self.seed_label,
            "seed_text":         self.seed_text,
            "simulation_id":     self.simulation_id,
            "simulation_state":  self.simulation_state,
            "halt_reason":       self.halt_reason,
            "contained":         self.contained,
            "cycle_count":       self.cycle_count,
            "drift_score":       round(self.drift_score, 4),
            "inflation_ratio":   round(self.inflation_ratio, 4),
            "elapsed_seconds":   round(self.elapsed_seconds, 6),
            "containment_sig":   self.containment_sig,
            "vault_key":         self.vault_key,
            "processed_at":      self.processed_at,
        }


# ── Bridge ───────────────────────────────────────────────────────────────────

class ParadoxBridge:
    """
    CDS-Ω1 ↔ Paradox Engine CITL integration bridge.

    Usage
    -----
    bridge = ParadoxBridge(bus=bus, router=router)
    # The bridge self-subscribes to canon.paradox.intake on construction.
    # It processes CSPs async as they arrive on that topic.
    # Shutdown: bridge.shutdown()
    """

    SUBSYSTEM_ID = "CDS-Ω1:PARADOX_BRIDGE"

    def __init__(
        self,
        bus:    CITLBus,
        router: Router,
        config: Optional[EngineConfig] = None,
    ) -> None:
        self.bus    = bus
        self.router = router
        self._engine = ParadoxEngine(config=config or _make_operational_config())
        self._processed: list[ParadoxIntelPacket] = []
        self._error_count: int = 0

        # Subscribe to the paradox intake topic
        bus.subscribe(
            Topic.PARADOX_INTAKE,
            self._handle_paradox_intake,
            "ParadoxBridge",
        )
        logger.info("ParadoxBridge initialised — subscribed to %s", Topic.PARADOX_INTAKE)

    # ── Handler ──────────────────────────────────────────────────────────────

    async def _handle_paradox_intake(self, msg: Message) -> None:
        """
        Called by CITL whenever a CSP arrives on canon.paradox.intake.
        Runs paradox exploration synchronously in the event loop
        (engine is CPU-bound; kept fast via tight config bounds).
        """
        raw = msg.packet
        try:
            csp = self._extract_csp(raw)
        except Exception as exc:
            logger.error("ParadoxBridge: failed to deserialise CSP: %s", exc)
            self._error_count += 1
            return

        logger.info(
            "ParadoxBridge: processing CSP %s  type=%s  conf=%.2f",
            csp.synthesis_id[:12], csp.synthesis_type.value, csp.confidence_score,
        )

        pip = await self._process_csp(csp)
        self._processed.append(pip)

        # Publish PIP to operator dashboard
        await self.bus.publish(Topic.OPERATOR_DASHBOARD, pip.to_dict())

        # Trigger recursive re-synthesis if resolution was meaningful
        if pip.cycle_count > 0 or pip.contained:
            await self._trigger_recursive(csp, pip)

    async def _process_csp(self, csp: CSP) -> ParadoxIntelPacket:
        """
        Core processing: build paradox seed from CMX contradiction data,
        run the Paradox Engine, and return a filled ParadoxIntelPacket.
        """
        pip = ParadoxIntelPacket(synthesis_id=csp.synthesis_id)
        pip.source_domains = [d.value for d in csp.domains_involved]

        # ── Identify dominant contradiction pair ──────────────────────────────
        cmx_data = csp.contradiction_matrix
        domain_ids = csp.domains_involved
        max_c = 0.0
        dom_a: Optional[DomainID] = None
        dom_b: Optional[DomainID] = None

        if cmx_data and len(domain_ids) >= 2:
            for i, row in enumerate(cmx_data):
                for j, val in enumerate(row):
                    if i != j and float(val) > max_c:
                        max_c = float(val)
                        if i < len(domain_ids) and j < len(domain_ids):
                            dom_a = domain_ids[i]
                            dom_b = domain_ids[j]

        pip.max_contradiction = round(max_c, 4)
        pip.contradiction_pair = (
            dom_a.value if dom_a else "",
            dom_b.value if dom_b else "",
        )

        # ── Build seed proposition from contradiction template ────────────────
        seed_text, seed_label = self._build_seed(csp, dom_a, dom_b, max_c)
        pip.seed_label = seed_label
        pip.seed_text  = seed_text

        # ── Run Paradox Engine ────────────────────────────────────────────────
        try:
            sim = self._engine.run_full(seed_text, label=seed_label)

            pip.simulation_id    = sim.simulation_id
            pip.simulation_state = sim.state.name
            pip.vault_key        = sim.vault_key or ""
            pip.containment_sig  = sim.containment_signature or ""

            if sim.result:
                pip.halt_reason     = sim.result.halt_reason
                pip.contained       = sim.result.contained
                pip.cycle_count     = sim.result.cycle_count
                pip.drift_score     = sim.result.drift_score
                pip.inflation_ratio = sim.result.inflation_ratio
                pip.elapsed_seconds = sim.result.elapsed_seconds

            logger.info(
                "ParadoxBridge: engine resolved %s → %s  cycles=%d  drift=%.3f  sig=%s",
                seed_label, sim.state.name,
                pip.cycle_count, pip.drift_score,
                pip.containment_sig[:16] if pip.containment_sig else "NONE",
            )

        except Exception as exc:
            logger.error("ParadoxBridge: engine error for CSP %s: %s", csp.synthesis_id, exc)
            pip.halt_reason = f"ENGINE_ERROR: {exc}"
            pip.contained   = True   # treat errors as contained

        return pip

    # ── Seed Construction ────────────────────────────────────────────────────

    def _build_seed(
        self,
        csp:   CSP,
        dom_a: Optional[DomainID],
        dom_b: Optional[DomainID],
        max_c: float,
    ) -> tuple[str, str]:
        """
        Build a paradox seed text from the dominant contradiction pair.
        Uses canon_constants.contradiction_template() when available;
        falls back to a generative template derived from synthesis_type.
        """
        if dom_a and dom_b:
            # Translate DomainID values to canonical lowercase keys
            _REV_MAP = {v: k for k, v in DOMAIN_ID_MAP.items()}
            key_a = _REV_MAP.get(dom_a, dom_a.value.lower())
            key_b = _REV_MAP.get(dom_b, dom_b.value.lower())

            # Determine expected vs. observed direction polarity
            exp_dir = expected_direction(key_a, key_b)  # +1 or -1 or None
            polarity = "negative" if exp_dir == 1 else "positive"

            tmpl = contradiction_template(key_a, key_b, polarity)
            if tmpl:
                label = f"cds-paradox-{key_a}-{key_b}-{csp.synthesis_id[:6]}"
                return tmpl, label

        # Fallback: derive from synthesis_type and insight
        insight_excerpt = csp.insight[:120] if csp.insight else "No insight available"
        seed = (
            f"The following cross-domain signal pattern is simultaneously "
            f"true and self-negating: {insight_excerpt}. "
            f"If this pattern holds, then the domains it describes cannot be "
            f"in the state that produced it."
        )
        label = f"cds-paradox-{csp.synthesis_type.value.lower()}-{csp.synthesis_id[:6]}"
        return seed, label

    # ── Recursive Re-synthesis Trigger ───────────────────────────────────────

    async def _trigger_recursive(self, csp: CSP, pip: ParadoxIntelPacket) -> None:
        """
        After paradox resolution, request constrained re-synthesis via
        Router.request_recursive_synthesis() (spec §6 — RECURSIVE mode).
        Focuses on the contradiction pair identified by the engine.
        """
        if not csp.domains_involved:
            return

        focus_cells: list[tuple[DomainID, DomainID]] = []
        if pip.contradiction_pair and len(pip.contradiction_pair) == 2:
            a_val, b_val = pip.contradiction_pair
            try:
                da = DomainID(a_val)
                db = DomainID(b_val)
                focus_cells = [(da, db)]
            except ValueError:
                pass

        request = RecursiveRequest(
            domain_set    = csp.domains_involved,
            time_window_s = 1800,           # 30-min re-synthesis window
            focus_cells   = focus_cells,
            synthesis_id  = csp.synthesis_id,
        )

        logger.info(
            "ParadoxBridge → recursive re-synthesis: domains=%s  focus=%s",
            [d.value for d in request.domain_set],
            [(a.value, b.value) for a, b in focus_cells],
        )

        try:
            await self.router.request_recursive_synthesis(request)
        except Exception as exc:
            logger.warning("ParadoxBridge: recursive re-synthesis failed: %s", exc)

    # ── CDS extraction helper ────────────────────────────────────────────────

    @staticmethod
    def _extract_csp(raw: Any) -> CSP:
        """
        Extract a CSP from a CITL message payload.
        Accepts either a CSP object directly or a raw dict.
        """
        if isinstance(raw, CSP):
            return raw
        if isinstance(raw, dict):
            from router import Router
            return Router._deserialise_csp(raw)
        raise TypeError(f"Unexpected payload type for paradox intake: {type(raw)}")

    # ── Introspection ─────────────────────────────────────────────────────────

    def processed_packets(self, last_n: int = 20) -> list[ParadoxIntelPacket]:
        return self._processed[-last_n:]

    def audit_export(self) -> str:
        """Export engine audit log as newline-delimited JSON."""
        return self._engine.audit.export_json()

    def vault_summary(self) -> dict:
        return self._engine.vault.summary()

    def status(self) -> dict:
        return {
            "subsystem_id":    self.SUBSYSTEM_ID,
            "engine_status":   self._engine.status(),
            "processed_count": len(self._processed),
            "error_count":     self._error_count,
        }

    def shutdown(self) -> None:
        self._engine.shutdown()
        logger.info("ParadoxBridge shutdown complete.")
