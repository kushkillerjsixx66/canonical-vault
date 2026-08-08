"""
CDS-Ω1 Pipeline Orchestrator

Wires DAL → CDCE → CMX → EPS → Router into a single runnable system.
Manages the flush loop with mode-aware cadence and graceful shutdown.
"""

from __future__ import annotations

import asyncio
import logging
import signal
from datetime import datetime
from typing import Any

from citl import CITLBus, Topic
from models import DomainID
from pipeline import DAL, CDCE, CMX, EPS, CONTRADICTION_HIGH_THRESHOLD
from router import OperationalMode, RecursiveRequest, Router

logger = logging.getLogger("cds.orchestrator")


class CDSOrchestrator:
    """
    Top-level orchestrator for CDS-Ω1.

    Lifecycle
    ---------
    1. __init__  : create bus + all pipeline stages + router; wire subscriptions.
    2. start()   : begin flush loop (runs until stop() is called).
    3. stop()    : signal shutdown; await clean exit.

    Flush loop
    ----------
    - Runs CDCE.flush() and EPS.flush() every `cadence_s` seconds.
    - cadence_s is re-read from Router.cadence_s each iteration
      so PASSIVE/ACTIVE mode transitions take effect immediately.
    - In RECURSIVE mode the flush loop is paused; flushes are
      only triggered by explicit request_recursive_synthesis() calls.
    """

    def __init__(self, history_depth: int = 500) -> None:
        self.bus  = CITLBus(history_depth=history_depth)
        self.dal  = DAL(self.bus)
        self.cdce = CDCE(self.bus)
        self.cmx  = CMX(self.bus)
        self.eps  = EPS(self.bus, self.cmx)
        self.router = Router(self.bus, self.dal, self.cdce, self.cmx, self.eps)

        self._running  = False
        self._stop_evt = asyncio.Event()
        self._task: asyncio.Task | None = None

        logger.info("CDSOrchestrator constructed — CDS-Ω1 ready")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the flush loop."""
        if self._running:
            raise RuntimeError("Orchestrator already running")
        self._running  = True
        self._stop_evt.clear()
        self._task = asyncio.create_task(self._flush_loop(), name="cds-flush-loop")
        logger.info("CDSOrchestrator started — initial mode=%s", self.router.mode.value)

    async def stop(self) -> None:
        """Signal the flush loop to stop and await clean exit."""
        logger.info("CDSOrchestrator stopping…")
        self._stop_evt.set()
        self._running = False
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=10.0)
            except asyncio.TimeoutError:
                self._task.cancel()
        logger.info("CDSOrchestrator stopped")

    async def __aenter__(self) -> "CDSOrchestrator":
        await self.start()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.stop()

    # ------------------------------------------------------------------
    # Flush loop
    # ------------------------------------------------------------------

    async def _flush_loop(self) -> None:
        logger.info("Flush loop running")
        while not self._stop_evt.is_set():
            mode = self.router.mode

            if mode == OperationalMode.RECURSIVE:
                # Recursive mode: no autonomous flush — yield and wait
                logger.debug("Flush loop: RECURSIVE mode — waiting for PE requests")
                try:
                    await asyncio.wait_for(
                        self._stop_evt.wait(), timeout=60.0
                    )
                except asyncio.TimeoutError:
                    # Transition back to ACTIVE if no further recursive requests
                    logger.info("RECURSIVE timeout — falling back to ACTIVE mode")
                continue

            cadence = self.router.cadence_s
            logger.info(
                "Flush cycle starting  mode=%-9s  cadence=%ds",
                mode.value, cadence,
            )

            try:
                await self._run_flush_cycle()
            except Exception as exc:
                logger.error("Flush cycle error: %s", exc, exc_info=True)

            # Sleep for cadence, but wake early if stop is signalled
            try:
                await asyncio.wait_for(self._stop_evt.wait(), timeout=float(cadence))
            except asyncio.TimeoutError:
                pass   # normal — cadence elapsed

        logger.info("Flush loop exited")

    async def _run_flush_cycle(self) -> None:
        t0 = datetime.utcnow()

        # Stage 1: CDCE — generate SCPs from buffered DIPs
        scp_count = await self.cdce.flush()

        # Stage 2: EPS — generate CSP from SCPs + DIPs + CMX
        csp = await self.eps.flush()

        elapsed = (datetime.utcnow() - t0).total_seconds()
        logger.info(
            "Flush cycle complete  SCPs=%d  CSP=%s  elapsed=%.3fs",
            scp_count,
            csp.synthesis_id if csp else "none",
            elapsed,
        )

    # ------------------------------------------------------------------
    # Public API: inject DIPs directly (for testing / integration)
    # ------------------------------------------------------------------

    async def ingest_dip(self, dip_dict: dict) -> None:
        """
        Publish a raw DIP dict to the bus as if it came from a Harvester.
        domain_id must be set in the dict.
        """
        domain = dip_dict.get("domain_id", "UNKNOWN")
        topic  = f"canon.dip.raw.{domain.upper()}"
        await self.bus.publish(topic, dip_dict)

    async def ingest_dips(self, dip_dicts: list[dict]) -> None:
        """Bulk ingest multiple DIPs concurrently."""
        await asyncio.gather(*[self.ingest_dip(d) for d in dip_dicts])

    async def request_recursive_synthesis(self, request: RecursiveRequest) -> None:
        """Forward a recursive synthesis request from the Paradox Engine."""
        await self.router.request_recursive_synthesis(request)

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        cmx_snap = self.cmx.snapshot()
        max_c, da, db = self.cmx.max_contradiction()
        return {
            "subsystem": "CDS-Ω1",
            "running": self._running,
            "mode": self.router.mode.value,
            "cadence_s": self.router.cadence_s,
            "dal_stats": self.dal.stats,
            "bus_stats": self.bus.stats(),
            "bus_dead_letters": len(self.bus.dead_letters()),
            "route_counts": self.router.route_counts(),
            "cmx": {
                "domains": cmx_snap["domains"],
                "max_contradiction": round(max_c, 4),
                "hot_pair": [da.value if da else None, db.value if db else None],
            },
            "csp_history_size": len(self.router.csp_history(100)),
            "snapshot_at": datetime.utcnow().isoformat(),
        }

    def topic_map(self) -> dict[str, list[str]]:
        return self.bus.topic_subscriber_map()
