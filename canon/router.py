"""
CDS-Ω1 Output Router + Operational Mode Controller

Responsibilities
----------------
- Subscribe to canon.csp.synthesis
- Apply spec §5 thresholds to set/verify escalation_path
- Route CSPs to downstream topics per escalation_path
- Publish CMX summaries to operator dashboard
- Manage pipeline cadence: PASSIVE / ACTIVE / RECURSIVE modes
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Awaitable

from citl import CITLBus, Message, Topic
from models import CSP, DomainID, EscalationPath, SynthesisType
from canon_constants import (
    ACTIVE_MODE_TRIGGER, RECURSIVE_MODE_TRIGGER,
    CONTRADICTION_HIGH_THRESHOLD as _CONTR_HIGH,
    DRIFT_SURGE_THRESHOLD,
)
from pipeline import (
    CDCE, CMX, DAL, EPS,
    CONTRADICTION_HIGH_THRESHOLD,
    DRIFT_HIGH_THRESHOLD,
    CONFIDENCE_GATE,
)

logger = logging.getLogger("cds.router")


# ---------------------------------------------------------------------------
# Operational modes  (spec §6)
# ---------------------------------------------------------------------------

class OperationalMode(str, Enum):
    PASSIVE   = "PASSIVE"    # fixed cadence, always-on
    ACTIVE    = "ACTIVE"     # threshold exceeded → faster cadence
    RECURSIVE = "RECURSIVE"  # Paradox Engine requests re-synthesis


# Cadence in seconds per mode
CADENCE: dict[OperationalMode, int] = {
    OperationalMode.PASSIVE:   3600,   # 60 min
    OperationalMode.ACTIVE:    600,    # 10 min
    OperationalMode.RECURSIVE: 0,      # on-demand (no fixed interval)
}


# ---------------------------------------------------------------------------
# Recursive re-synthesis request  (issued by Paradox Engine)
# ---------------------------------------------------------------------------

@dataclass
class RecursiveRequest:
    """
    Constrained re-synthesis request from the Paradox Engine (spec §6).

    Fields
    ------
    domain_set   : restrict synthesis to these domains only.
    time_window_s: narrower time window for DIP collection.
    focus_cells  : list of (domain_i, domain_j) pairs — high CMX cells to focus.
    synthesis_id : reference to the original CSP that triggered recursion.
    """
    domain_set: list[DomainID]
    time_window_s: int
    focus_cells: list[tuple[DomainID, DomainID]]
    synthesis_id: str
    requested_at: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Threshold evaluator  (spec §5)
# ---------------------------------------------------------------------------

class ThresholdEvaluator:
    """
    Deterministic re-evaluation of escalation_path based on spec §5 thresholds.
    Called by the router AFTER EPS has already set a path, as a safety gate.
    """

    @staticmethod
    def evaluate(csp: CSP, cmx: CMX) -> EscalationPath:
        # Confidence gate: below threshold → NONE, regardless of other factors
        if csp.confidence_score < CONFIDENCE_GATE:
            logger.debug(
                "CSP %s below confidence gate (%.2f < %.2f) → NONE",
                csp.synthesis_id, csp.confidence_score, CONFIDENCE_GATE,
            )
            return EscalationPath.NONE

        max_contradiction, _, _ = cmx.max_contradiction()

        # Contradiction HIGH → PARADOX ENGINE
        if max_contradiction >= CONTRADICTION_HIGH_THRESHOLD:
            logger.info(
                "CMX max contradiction %.2f >= %.2f → PARADOXENGINE",
                max_contradiction, CONTRADICTION_HIGH_THRESHOLD,
            )
            return EscalationPath.PARADOX_ENGINE

        # Drift HIGH → already tagged in synthesis_type; escalate to OPERATOR
        drift_magnitude = float(csp.metadata.get("drift_magnitude", 0.0))
        if drift_magnitude >= DRIFT_HIGH_THRESHOLD:
            logger.info(
                "Drift magnitude %.2f >= %.2f → OPERATORALERT",
                drift_magnitude, DRIFT_HIGH_THRESHOLD,
            )
            return EscalationPath.OPERATOR_ALERT

        # Systemic drift synthesis type always gets field intel
        if csp.synthesis_type == SynthesisType.SYSTEMIC_DRIFT:
            return EscalationPath.FIELD_INTEL

        # Default: field intel for all escalatable CSPs
        return EscalationPath.FIELD_INTEL


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

class Router:
    """
    Output router + mode controller.

    Wires up:
    - Subscription to canon.csp.synthesis
    - Subscription to canon.cmx.grid (for dashboard snapshots)
    - Downstream publishing per escalation_path
    - Mode state machine
    - Recursive re-synthesis execution
    """

    def __init__(
        self,
        bus: CITLBus,
        dal: DAL,
        cdce: CDCE,
        cmx: CMX,
        eps: EPS,
    ) -> None:
        self.bus  = bus
        self.dal  = dal
        self.cdce = cdce
        self.cmx  = cmx
        self.eps  = eps

        self._mode: OperationalMode = OperationalMode.PASSIVE
        self._mode_lock = asyncio.Lock()

        self._recursive_queue: asyncio.Queue[RecursiveRequest] = asyncio.Queue()
        self._routed_csps: list[dict[str, Any]] = []
        self._csp_history: list[CSP] = []

        # Stats
        self._route_counts: dict[str, int] = {
            "paradox_engine": 0,
            "field_intel": 0,
            "operator_alert": 0,
            "none": 0,
        }

        # Wire subscriptions
        bus.subscribe(Topic.CSP_SYNTHESIS, self._handle_csp, "Router-CSP")
        bus.subscribe(Topic.CMX_GRID,      self._handle_cmx, "Router-CMX")

        logger.info("Router initialised — mode=%s", self._mode.value)

    # ------------------------------------------------------------------
    # CSP handler
    # ------------------------------------------------------------------

    async def _handle_csp(self, msg: Message) -> None:
        raw = msg.packet
        try:
            csp = self._deserialise_csp(raw)
        except Exception as exc:
            logger.error("Router: failed to deserialise CSP: %s", exc)
            return

        # Re-evaluate escalation path via threshold gates
        corrected_path = ThresholdEvaluator.evaluate(csp, self.cmx)
        if corrected_path != csp.escalation_path:
            logger.info(
                "Router overriding CSP escalation_path %s → %s",
                csp.escalation_path.value, corrected_path.value,
            )
            csp.escalation_path = corrected_path

        self._csp_history.append(csp)
        await self._route(csp)
        await self._update_mode(csp)

    async def _route(self, csp: CSP) -> None:
        path = csp.escalation_path
        record = {
            "synthesis_id": csp.synthesis_id,
            "routed_to": path.value,
            "routed_at": datetime.utcnow().isoformat(),
            "synthesis_type": csp.synthesis_type.value,
            "confidence": csp.confidence_score,
        }
        self._routed_csps.append(record)

        # Always forward to FIELD INTEL (spec §4.5)
        await self.bus.publish(Topic.FIELD_INTEL_INTAKE, csp)
        self._route_counts["field_intel"] += 1

        if path == EscalationPath.PARADOX_ENGINE:
            await self.bus.publish(Topic.PARADOX_INTAKE, csp)
            self._route_counts["paradox_engine"] += 1
            logger.warning(
                "→ PARADOX ENGINE: CSP %s  type=%s  conf=%.2f",
                csp.synthesis_id, csp.synthesis_type.value, csp.confidence_score,
            )

        elif path == EscalationPath.OPERATOR_ALERT:
            self._route_counts["operator_alert"] += 1
            logger.warning(
                "→ OPERATOR ALERT: CSP %s  drift=%.2f",
                csp.synthesis_id,
                float(csp.metadata.get("drift_magnitude", 0)),
            )

        elif path == EscalationPath.NONE:
            self._route_counts["none"] += 1
            logger.debug("CSP %s below confidence gate — not escalated", csp.synthesis_id)

        # Always push summary to operator dashboard
        await self._publish_dashboard(csp)

    async def _publish_dashboard(self, csp: CSP) -> None:
        cmx_snap = self.cmx.snapshot()
        max_c, da, db = self.cmx.max_contradiction()

        summary = {
            "type": "DASHBOARD_SUMMARY",
            "synthesis_id": csp.synthesis_id,
            "timestamp": csp.timestamp.isoformat(),
            "synthesis_type": csp.synthesis_type.value,
            "escalation_path": csp.escalation_path.value,
            "confidence_score": csp.confidence_score,
            "insight": csp.insight,
            "mode": self._mode.value,
            "drift_magnitude": csp.metadata.get("drift_magnitude"),
            "cmx": {
                "domains": cmx_snap["domains"],
                "max_contradiction": round(max_c, 4),
                "hot_pair": [da.value if da else None, db.value if db else None],
                "matrix": cmx_snap["matrix"],
            },
            "predictive_indicators": [p.to_dict() for p in csp.predictive_indicators],
            "route_counts": dict(self._route_counts),
            "dal_stats": self.dal.stats,
        }
        await self.bus.publish(Topic.OPERATOR_DASHBOARD, summary)

    # ------------------------------------------------------------------
    # Mode state machine  (spec §6)
    # ------------------------------------------------------------------

    async def _update_mode(self, csp: CSP) -> None:
        """
        Mode state machine — now honours operator count-based triggers
        from cds_omega1.py in addition to spec §5 magnitude gates:

          ACTIVE_MODE_TRIGGER    = 3  → enter ACTIVE when ≥3 domains anomalous
          RECURSIVE_MODE_TRIGGER = 2  → enter RECURSIVE when ≥2 contradictions
          DRIFT_SURGE_THRESHOLD  = 0.45 → enter ACTIVE on early drift surge
        """
        async with self._mode_lock:
            max_c, _, _  = self.cmx.max_contradiction()
            drift_mag    = float(csp.metadata.get("drift_magnitude", 0.0))
            anomaly_tot  = int(csp.metadata.get("dip_count", 0))   # proxy for domain count
            contr_count  = len(self.csp_history(50))               # rolling contradiction count

            # Count-based triggers (cds_omega1.py §MODE)
            recursive_trigger  = max_c >= _CONTR_HIGH           # spec §5 paradox gate
            active_trigger_mag = drift_mag >= DRIFT_HIGH_THRESHOLD
            active_trigger_drift_surge = drift_mag >= DRIFT_SURGE_THRESHOLD
            active_trigger_anomaly     = anomaly_tot >= ACTIVE_MODE_TRIGGER

            threshold_exceeded = (
                active_trigger_mag or
                active_trigger_drift_surge or
                active_trigger_anomaly or
                max_c >= CONTRADICTION_HIGH_THRESHOLD
            )

            if csp.escalation_path == EscalationPath.PARADOX_ENGINE or recursive_trigger:
                new_mode = OperationalMode.RECURSIVE
            elif threshold_exceeded:
                new_mode = OperationalMode.ACTIVE
            else:
                new_mode = OperationalMode.PASSIVE

            if new_mode != self._mode:
                logger.info(
                    "Mode transition: %s → %s  (contradiction=%.2f, drift=%.2f)",
                    self._mode.value, new_mode.value, max_c, drift_mag,
                )
                self._mode = new_mode

    @property
    def mode(self) -> OperationalMode:
        return self._mode

    @property
    def cadence_s(self) -> int:
        return CADENCE[self._mode]

    # ------------------------------------------------------------------
    # CMX handler (dashboard updates on new matrix)
    # ------------------------------------------------------------------

    async def _handle_cmx(self, msg: Message) -> None:
        # Lightweight handler — CMX publishes its own grid; we use cmx.snapshot()
        # when building dashboard payloads, so no additional work needed here.
        pass

    # ------------------------------------------------------------------
    # Recursive mode  (spec §6 — Paradox Engine callback)
    # ------------------------------------------------------------------

    async def request_recursive_synthesis(self, request: RecursiveRequest) -> CSP | None:
        """
        Entry point for Paradox Engine to request constrained re-synthesis.
        Runs correlation + synthesis restricted to request.domain_set
        with request.time_window_s and focus_cells context.
        Returns the new CSP (with distinct synthesis_id).
        """
        logger.info(
            "RECURSIVE re-synthesis requested by Paradox Engine: "
            "domains=%s  window=%ds  focus=%s  parent_id=%s",
            [d.value for d in request.domain_set],
            request.time_window_s,
            [(a.value, b.value) for a, b in request.focus_cells],
            request.synthesis_id,
        )

        async with self._mode_lock:
            self._mode = OperationalMode.RECURSIVE

        # Re-run CDCE flush (CDCE's buffer already has recent DIPs)
        await self.cdce.flush()

        # Re-run EPS with recursion metadata embedded
        # EPS will emit a new CSP on the synthesis topic, which Router handles normally
        # Inject focus context into EPS metadata via a side-channel metadata dict
        original_flush = self.eps.flush

        async def recursive_flush() -> CSP | None:
            csp = await original_flush()
            if csp:
                csp.metadata["recursive"] = True
                csp.metadata["parent_synthesis_id"] = request.synthesis_id
                csp.metadata["focus_domains"] = [d.value for d in request.domain_set]
                csp.metadata["focus_cells"] = [
                    (a.value, b.value) for a, b in request.focus_cells
                ]
            return csp

        return await recursive_flush()

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def routing_log(self, last_n: int = 20) -> list[dict]:
        return self._routed_csps[-last_n:]

    def csp_history(self, last_n: int = 10) -> list[CSP]:
        return self._csp_history[-last_n:]

    def route_counts(self) -> dict[str, int]:
        return dict(self._route_counts)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _deserialise_csp(raw: dict) -> CSP:
        from models import (
            DomainID, EscalationPath, IndicatorType, PredictiveIndicator,
            ReinforcementCluster, Signal, SignalType, SynthesisType,
        )
        domains = [DomainID(d) for d in raw["domains_involved"]]
        clusters = []
        for c in raw.get("reinforcement_clusters", []):
            sigs = [
                Signal(
                    signal_type=SignalType(s["signal_type"]),
                    value=float(s["value"]),
                    weight=float(s["weight"]),
                    confidence=float(s["confidence"]),
                    source=s["source"],
                )
                for s in c.get("signals", [])
            ]
            clusters.append(ReinforcementCluster(
                signals=sigs,
                domain_origin=DomainID(c["domain_origin"]),
                weight=float(c["weight"]),
            ))
        preds = [
            PredictiveIndicator(
                indicator_type=IndicatorType(p["indicator_type"]),
                value=float(p["value"]),
                confidence=float(p["confidence"]),
            )
            for p in raw.get("predictive_indicators", [])
        ]
        return CSP(
            synthesis_id=raw["synthesis_id"],
            timestamp=datetime.fromisoformat(raw["timestamp"]),
            domains_involved=domains,
            synthesis_type=SynthesisType(raw["synthesis_type"]),
            insight=raw["insight"],
            reinforcement_clusters=clusters,
            contradiction_matrix=raw.get("contradiction_matrix", []),
            drift_vector=raw.get("drift_vector", [0.0]),
            predictive_indicators=preds,
            confidence_score=float(raw["confidence_score"]),
            escalation_path=EscalationPath(raw["escalation_path"]),
            metadata=raw.get("metadata", {}),
        )
