"""
Vara Scan Domain Modes  —  Vara.ECON / Vara.CRYPTO / Vara.GEOPOL / Vara.WORLDPOL / Vara.INDUSTRIAL

Each VaraScanDomain is a self-contained scan mode that:
  1. Owns its Harvester instance
  2. Runs the Vara scan pipeline (weak signals → trends → anomalies)
  3. Maintains a rolling artifact history for temporal analysis
  4. Emits domain-qualified VaraScanResults to the EpistemicBus
  5. Reports scan lineage for Vault Chain persistence

This mirrors the canonical architecture:
    VaraInterface → Vara → EpistemicBus → stumpy_event_queue

In the Canon multi-domain lattice:
    [Vara.ECON]
    [Vara.CRYPTO]    →  EpistemicBus  →  Canon Aggregator  →  CDS-Ω1 DAL
    [Vara.GEOPOL]
    [Vara.WORLDPOL]
    [Vara.INDUSTRIAL]
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from vara.vara_schema import VaraScanResult
from vara.domain_ontology import DomainOntology, get_ontology
from vara.harvesters.base_harvester import BaseHarvester

logger = logging.getLogger("cds.vara.scan")


# ---------------------------------------------------------------------------
# Scan mode result — extends VaraScanResult with domain context
# ---------------------------------------------------------------------------

@dataclass
class DomainScanResult:
    """
    Enriched scan result for a single domain mode run.
    Wraps VaraScanResult with domain identity, timestamp, and
    a cross-domain export packet (DIP-ready).
    """
    domain_id:       str
    scan_id:         str
    timestamp:       datetime
    result:          VaraScanResult
    dip_packet:      dict              # ready for canon.dip.raw.<domain>
    cadence_s:       int
    escalation_bias: float

    def to_dict(self) -> dict:
        return {
            "domain_id":       self.domain_id,
            "scan_id":         self.scan_id,
            "timestamp":       self.timestamp.isoformat(),
            "result":          self.result.to_dict(),
            "dip_packet":      self.dip_packet,
            "cadence_s":       self.cadence_s,
            "escalation_bias": self.escalation_bias,
        }


# ---------------------------------------------------------------------------
# Epistemic Bus stub
# Bridges canonical Vara EpistemicBus contract → CITL bus
# In a full Vault runtime: replace with EpistemicBus(stumpy_event_queue)
# ---------------------------------------------------------------------------

class EpistemicBusBridge:
    """
    Translates Vara scan results into the canonical epistemic_state message
    format and forwards them to the CITL bus as DIP packets.

    Canonical payload shape (from vara_epistemic_bus.py):
        {
            "type":    "epistemic_state",
            "source":  "vara",
            "payload": {
                "identity": <domain_id>,
                "runtime":  <scan metadata>,
                "lineage":  <lineage chain>
            }
        }
    """

    def __init__(self, citl_bus: Any) -> None:
        self._bus = citl_bus
        self._emitted: int = 0

    async def emit(self, domain_id: str, scan_result: DomainScanResult) -> None:
        """
        Emit epistemic context to the bus.
        Publishes TWO messages:
          1. Epistemic state event (canonical Vara format)
          2. Raw DIP (consumed by DAL → pipeline)
        """
        # 1. Canonical epistemic state
        epistemic_payload = {
            "type":    "epistemic_state",
            "source":  "vara",
            "payload": {
                "identity": domain_id,
                "runtime":  {
                    "scan_id":          scan_result.scan_id,
                    "timestamp":        scan_result.timestamp.isoformat(),
                    "weak_signal_count": len(scan_result.result.weak_signals),
                    "trend_count":      len(scan_result.result.trends),
                    "anomaly_count":    len(scan_result.result.anomalies),
                    "trends":           [t.name for t in scan_result.result.trends],
                    "escalation_bias":  scan_result.escalation_bias,
                },
                "lineage": scan_result.result.lineage,
            },
        }
        await self._bus.publish(
            f"vara.epistemic.{domain_id.lower()}",
            epistemic_payload,
        )

        # 2. Raw DIP → DAL intake
        await self._bus.publish(
            f"canon.dip.raw.{domain_id.upper()}",
            scan_result.dip_packet,
        )

        self._emitted += 1
        logger.debug(
            "EpistemicBusBridge emitted [%s] scan_id=%s  dip_conf=%.3f",
            domain_id,
            scan_result.scan_id,
            scan_result.dip_packet.get("confidence_score", 0),
        )

    @property
    def emitted_count(self) -> int:
        return self._emitted


# ---------------------------------------------------------------------------
# VaraScanDomain — single-domain scan mode
# ---------------------------------------------------------------------------

class VaraScanDomain:
    """
    Canonical domain-mode scan controller.

    Lifecycle
    ---------
    - scan_once() : execute one harvest-scan-emit cycle.
    - start()     : begin autonomous cadence loop (async).
    - stop()      : graceful shutdown.

    History
    -------
    Maintains a rolling window of DomainScanResult objects.
    Used for temporal delta analysis and trend confirmation.

    Canonical modes produced by this class:
        Vara.ECON      ← EconHarvester
        Vara.CRYPTO    ← CryptoHarvester
        Vara.GEOPOL    ← GeoPolHarvester
        Vara.WORLDPOL  ← WorldPolHarvester
        Vara.INDUSTRIAL← IndustrialHarvester
    """

    def __init__(
        self,
        harvester:    BaseHarvester,
        epistemic_bus: EpistemicBusBridge,
        history_depth: int = 50,
    ) -> None:
        self._harvester     = harvester
        self._bus           = epistemic_bus
        self._history:      list[DomainScanResult] = []
        self._history_depth = history_depth
        self._running       = False
        self._stop_evt      = asyncio.Event()
        self._task: asyncio.Task | None = None
        self._scan_count    = 0
        self._error_count   = 0

        logger.info(
            "VaraScanDomain [%s] initialised — cadence=%ds  bias=%.2f",
            self.domain_id,
            self.ontology.cadence_s,
            self.ontology.escalation_bias,
        )

    # ------------------------------------------------------------------ props

    @property
    def domain_id(self) -> str:
        return self._harvester.domain_id

    @property
    def ontology(self) -> DomainOntology:
        return self._harvester.ontology

    @property
    def mode_name(self) -> str:
        return f"Vara.{self.domain_id}"

    # ---------------------------------------------------------------- core API

    async def scan_once(self) -> DomainScanResult | None:
        """
        Execute one full scan cycle:
          fetch → normalise → vara scan → DIP assembly → epistemic emit.
        Returns DomainScanResult or None on failure.
        """
        vara_result = await self._harvester.run_once()
        if vara_result is None:
            self._error_count += 1
            return None

        # Build DIP from harvester's internal _build_dip (already published)
        # We need to reconstruct a DomainScanResult from what we have.
        # The DIP was already published by run_once(); fetch the last bus msg.
        # Here we reconstruct from the scan result directly.

        raw      = await self._harvester.fetch()
        artifact = self._harvester.normalise(raw)
        dip      = self._harvester._build_dip(artifact, vara_result)

        scan_id  = str(uuid.uuid4())
        result   = DomainScanResult(
            domain_id       = self.domain_id,
            scan_id         = scan_id,
            timestamp       = datetime.utcnow(),
            result          = vara_result,
            dip_packet      = dip,
            cadence_s       = self.ontology.cadence_s,
            escalation_bias = self.ontology.escalation_bias,
        )

        # Append to history
        self._history.append(result)
        if len(self._history) > self._history_depth:
            self._history.pop(0)

        # Emit to epistemic bus
        await self._bus.emit(self.domain_id, result)

        self._scan_count += 1
        logger.info(
            "[%s] scan #%d  weak=%d  trends=%d  anomalies=%d  conf=%.3f",
            self.mode_name,
            self._scan_count,
            len(vara_result.weak_signals),
            len(vara_result.trends),
            len(vara_result.anomalies),
            dip.get("confidence_score", 0),
        )
        return result

    # -------------------------------------------------- autonomous cadence loop

    async def start(self) -> None:
        if self._running:
            raise RuntimeError(f"{self.mode_name} already running")
        self._running = True
        self._stop_evt.clear()
        self._task = asyncio.create_task(
            self._cadence_loop(), name=f"vara-{self.domain_id.lower()}"
        )
        logger.info("%s cadence loop started", self.mode_name)

    async def stop(self) -> None:
        self._stop_evt.set()
        self._running = False
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                self._task.cancel()
        logger.info("%s cadence loop stopped", self.mode_name)

    async def _cadence_loop(self) -> None:
        while not self._stop_evt.is_set():
            await self.scan_once()
            try:
                await asyncio.wait_for(
                    self._stop_evt.wait(),
                    timeout=float(self.ontology.cadence_s),
                )
            except asyncio.TimeoutError:
                pass

    async def __aenter__(self) -> "VaraScanDomain":
        await self.start()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.stop()

    # --------------------------------------------------------- introspection

    def history(self, last_n: int = 10) -> list[DomainScanResult]:
        return self._history[-last_n:]

    def latest(self) -> DomainScanResult | None:
        return self._history[-1] if self._history else None

    def delta(self) -> dict[str, Any] | None:
        """
        Compare the two most recent scans to detect directional change.
        Returns a delta dict or None if fewer than 2 scans available.
        """
        if len(self._history) < 2:
            return None
        prev, curr = self._history[-2], self._history[-1]
        prev_conf = prev.dip_packet.get("confidence_score", 0.5)
        curr_conf = curr.dip_packet.get("confidence_score", 0.5)
        prev_drift = prev.dip_packet.get("drift_indicators", [{}])[0].get("magnitude", 0)
        curr_drift = curr.dip_packet.get("drift_indicators", [{}])[0].get("magnitude", 0)
        return {
            "domain_id":        self.domain_id,
            "confidence_delta": round(curr_conf - prev_conf, 4),
            "drift_delta":      round(curr_drift - prev_drift, 4),
            "new_trends":       [t.name for t in curr.result.trends
                                 if t.name not in {x.name for x in prev.result.trends}],
            "resolved_trends":  [t.name for t in prev.result.trends
                                 if t.name not in {x.name for x in curr.result.trends}],
            "new_anomalies":    [a.field for a in curr.result.anomalies],
            "scans_completed":  self._scan_count,
        }

    def stats(self) -> dict[str, Any]:
        latest = self.latest()
        return {
            "mode":          self.mode_name,
            "domain_id":     self.domain_id,
            "running":       self._running,
            "scans":         self._scan_count,
            "errors":        self._error_count,
            "history_depth": len(self._history),
            "cadence_s":     self.ontology.cadence_s,
            "escalation_bias": self.ontology.escalation_bias,
            "last_conf":     latest.dip_packet.get("confidence_score") if latest else None,
            "last_trends":   [t.name for t in latest.result.trends] if latest else [],
            "harvester_stats": self._harvester.stats,
        }
