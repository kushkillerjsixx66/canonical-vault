"""
Vara → Canon Bridge

Wires the VaraDispatcher (multi-channel Vara Scan) into the CDSOrchestrator
(CDS-Ω1 pipeline).  This is the seam between the epistemic substrate and the
synthesis engine.

Data flow:
    VaraDispatcher.scan_all()
        └── VaraScanDomain.scan_once()          per domain
                └── BaseHarvester.run_once()
                        └── fetch() → normalise() → _scan() → _build_dip()
                                └── bus.publish(canon.dip.raw.<DOMAIN>)
                                        └── DAL → CDCE → CMX → EPS → CSP

The bridge adds:
  1. Coordinated flush: after all domains have scanned, it triggers
     the CDCE + EPS flush so synthesis runs on a fresh, complete snapshot.
  2. Cross-domain signal injection: Dispatcher-detected CrossDomainSignals
     are injected as synthetic DIPs so the pipeline can reason about them.
  3. Cadence arbitration: uses the fastest domain cadence (CRYPTO=900s) as
     the bridge flush interval when in ACTIVE mode.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from vara.vara_dispatcher import VaraDispatcher
from orchestrator import CDSOrchestrator

logger = logging.getLogger("cds.vara.bridge")


class VaraCanonBridge:
    """
    Orchestrates Vara multi-channel scanning and CDS-Ω1 synthesis together.

    Usage
    -----
        bridge = VaraCanonBridge()
        await bridge.start()
        # runs autonomously; call bridge.flush() to force a cycle
        await bridge.stop()

    Or as an async context manager:
        async with VaraCanonBridge() as bridge:
            await asyncio.sleep(300)   # run for 5 minutes
    """

    def __init__(self) -> None:
        self.orchestrator = CDSOrchestrator(history_depth=500)
        self.dispatcher   = VaraDispatcher(self.orchestrator.bus, history_depth=50)
        self._running     = False
        self._stop_evt    = asyncio.Event()
        self._task: asyncio.Task | None = None
        self._flush_count = 0
        logger.info("VaraCanonBridge constructed")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        if self._running:
            raise RuntimeError("VaraCanonBridge already running")
        self._running = True
        self._stop_evt.clear()
        # Start CDS-Ω1 (its flush loop manages CDCE/EPS internally)
        await self.orchestrator.start()
        # Start Vara multi-channel dispatcher (all domain cadence loops)
        await self.dispatcher.start()
        # Start the bridge coordination loop
        self._task = asyncio.create_task(self._bridge_loop(), name="vara-canon-bridge")
        logger.info("VaraCanonBridge started — all systems active")

    async def stop(self) -> None:
        logger.info("VaraCanonBridge stopping…")
        self._stop_evt.set()
        self._running = False
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=10.0)
            except asyncio.TimeoutError:
                self._task.cancel()
        await self.dispatcher.stop()
        await self.orchestrator.stop()
        logger.info("VaraCanonBridge stopped")

    async def __aenter__(self) -> "VaraCanonBridge":
        await self.start()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.stop()

    # ------------------------------------------------------------------
    # Bridge coordination loop
    # ------------------------------------------------------------------

    async def _bridge_loop(self) -> None:
        """
        Coordinates Vara scan completion with CDS-Ω1 flush cycles.

        In PASSIVE mode: runs once every 30 minutes.
        In ACTIVE mode:  runs once every 10 minutes.
        In RECURSIVE:    yields to orchestrator.
        """
        logger.info("Bridge coordination loop running")
        while not self._stop_evt.is_set():
            mode = self.orchestrator.router.mode.value
            cadence = 1800 if mode == "PASSIVE" else 600   # 30 or 10 min

            try:
                await self.flush()
            except Exception as exc:
                logger.error("Bridge flush error: %s", exc, exc_info=True)

            try:
                await asyncio.wait_for(self._stop_evt.wait(), timeout=float(cadence))
            except asyncio.TimeoutError:
                pass

        logger.info("Bridge coordination loop exited")

    # ------------------------------------------------------------------
    # Manual flush
    # ------------------------------------------------------------------

    async def flush(self) -> dict[str, Any]:
        """
        Execute one full Vara → Canon synthesis cycle:
          1. Scan all domains simultaneously.
          2. Inject any cross-domain signals as synthetic DIPs.
          3. Run CDCE pairwise correlation.
          4. Run EPS synthesis.
          5. Return summary dict.
        """
        t0 = datetime.utcnow()

        # Step 1: scan all Vara domains
        scan_results = await self.dispatcher.scan_all()
        scanned = sum(1 for r in scan_results.values() if r is not None)

        # Step 2: inject cross-domain signals
        xds = self.dispatcher.cross_domain_signals(last_n=5)
        for signal in xds:
            await self._inject_cross_domain_signal(signal)

        # Step 3: CDCE correlation flush
        scp_count = await self.orchestrator.cdce.flush()

        # Step 4: EPS synthesis flush
        csp = await self.orchestrator.eps.flush()

        elapsed = (datetime.utcnow() - t0).total_seconds()
        self._flush_count += 1

        summary = {
            "flush_count":        self._flush_count,
            "domains_scanned":    scanned,
            "scp_count":          scp_count,
            "csp_produced":       csp is not None,
            "csp_id":             csp.synthesis_id if csp else None,
            "synthesis_type":     csp.synthesis_type.value if csp else None,
            "confidence":         csp.confidence_score if csp else None,
            "escalation_path":    csp.escalation_path.value if csp else None,
            "cross_domain_signals": len(xds),
            "elapsed_s":          round(elapsed, 3),
            "mode":               self.orchestrator.router.mode.value,
        }

        logger.info(
            "Bridge flush #%d  domains=%d  SCPs=%d  CSP=%s  elapsed=%.2fs",
            self._flush_count, scanned, scp_count,
            csp.synthesis_id[:8] if csp else "none",
            elapsed,
        )
        return summary

    async def _inject_cross_domain_signal(self, signal: dict) -> None:
        """
        Convert a Dispatcher-detected CrossDomainSignal into a synthetic DIP
        and publish it so the DAL and CDCE can incorporate it.

        Uses the first listed domain as the DIP's domain_id.
        """
        domains = signal.get("domains", [])
        if not domains:
            return

        # Use severity → confidence mapping
        severity_conf = {"HIGH": 0.85, "MEDIUM": 0.70, "LOW": 0.55}
        severity = signal.get("severity", "MEDIUM")
        conf = severity_conf.get(severity, 0.65)

        synthetic_dip = {
            "type": "DIP",
            "version": "1.0",
            "domain_id": domains[0],
            "timestamp": datetime.utcnow().isoformat(),
            "signal_set": [
                {
                    "signal_type": "INDICATOR",
                    "value": 1.0,
                    "weight": 0.75,
                    "confidence": conf,
                    "source": f"vara_cross_domain_{signal.get('signal_type', 'UNKNOWN').lower()}",
                }
            ],
            "weight_vector": [0.75],
            "confidence_score": conf,
            "drift_indicators": [
                {
                    "vector": [0.6, 0.4],
                    "magnitude": 0.65,
                    "direction": "CHAOTIC",
                    "volatility": 0.50,
                }
            ],
            "anomaly_flags": [
                {
                    "code": "REGIME_SHIFT",
                    "severity": severity,
                    "description": signal.get("description", "Cross-domain signal detected"),
                }
            ],
            "metadata": {
                "source": "vara_cross_domain_detector",
                "signal_type": signal.get("signal_type"),
                "domains_involved": domains,
            },
        }

        topic = f"canon.dip.raw.{domains[0].upper()}"
        await self.orchestrator.bus.publish(topic, synthetic_dip)
        logger.debug(
            "Injected cross-domain signal [%s] → %s",
            signal.get("signal_type"), topic,
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        orch_status = self.orchestrator.status()
        disp_status = self.dispatcher.status()
        return {
            "bridge": {
                "running":     self._running,
                "flush_count": self._flush_count,
                "snapshot_at": datetime.utcnow().isoformat(),
            },
            "orchestrator": orch_status,
            "dispatcher":   disp_status,
        }
