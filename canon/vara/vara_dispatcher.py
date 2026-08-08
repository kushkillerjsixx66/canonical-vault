"""
Vara Multi-Channel Dispatcher

The Dispatcher is the top-level controller for all domain scan modes.
It owns every VaraScanDomain instance and coordinates:

  - Parallel startup of all domain cadence loops
  - On-demand forced flush across all channels simultaneously
  - Cross-domain delta comparison (the first layer of cross-domain paradox detection)
  - Aggregate status reporting
  - Graceful shutdown of all channels

Architecture position:
    [Dispatcher]
        ├── VaraScanDomain [Vara.ECON]
        ├── VaraScanDomain [Vara.CRYPTO]
        ├── VaraScanDomain [Vara.GEOPOL]
        ├── VaraScanDomain [Vara.WORLDPOL]
        └── VaraScanDomain [Vara.INDUSTRIAL]
              ↓  (via EpistemicBusBridge)
    canon.dip.raw.<DOMAIN>  →  DAL  →  CDCE  →  CMX  →  EPS  →  CSP
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from vara.vara_scan_domain import VaraScanDomain, EpistemicBusBridge, DomainScanResult
from vara.harvesters.econ_harvester       import EconHarvester
from vara.harvesters.crypto_harvester     import CryptoHarvester
from vara.harvesters.geopol_harvester     import GeoPolHarvester
from vara.harvesters.worldpol_harvester   import WorldPolHarvester
from vara.harvesters.industrial_harvester import IndustrialHarvester

logger = logging.getLogger("cds.vara.dispatcher")


# ---------------------------------------------------------------------------
# Cross-domain anomaly surface
# ---------------------------------------------------------------------------

class CrossDomainSignal:
    """
    A signal that spans multiple domains — the Dispatcher's contribution
    to the Canon Paradox Engine detection pipeline.

    Detected by comparing domain scan results:
      - Simultaneous anomaly spikes across ≥2 domains
      - Trend divergence (one domain UP, another DOWN in same window)
      - Confidence collapse across domains (systematic uncertainty)
    """

    def __init__(
        self,
        signal_type: str,
        domains: list[str],
        description: str,
        severity: str,
        evidence: dict[str, Any],
    ) -> None:
        self.signal_type = signal_type
        self.domains     = domains
        self.description = description
        self.severity    = severity
        self.evidence    = evidence
        self.detected_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "signal_type": self.signal_type,
            "domains":     self.domains,
            "description": self.description,
            "severity":    self.severity,
            "evidence":    self.evidence,
            "detected_at": self.detected_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

class VaraDispatcher:
    """
    Multi-channel Vara Scan Dispatcher.

    Instantiates all five domain scan modes, manages their lifecycles,
    and surfaces cross-domain signals to the Canon pipeline.

    Parameters
    ----------
    bus          : CITLBus — shared Canon Intelligence Transport Layer bus.
    history_depth: per-domain scan history depth (default 50).
    """

    DOMAIN_ORDER = ["ECON", "CRYPTO", "GEOPOL", "WORLDPOL", "INDUSTRIAL"]

    def __init__(self, bus: Any, history_depth: int = 50) -> None:
        self._bus      = bus
        self._ep_bus   = EpistemicBusBridge(bus)
        self._domains: dict[str, VaraScanDomain] = {}
        self._running  = False
        self._cross_domain_signals: list[CrossDomainSignal] = []

        self._build_domains(history_depth)
        logger.info(
            "VaraDispatcher initialised — channels: %s",
            list(self._domains.keys()),
        )

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_domains(self, history_depth: int) -> None:
        harvester_map = {
            "ECON":       EconHarvester,
            "CRYPTO":     CryptoHarvester,
            "GEOPOL":     GeoPolHarvester,
            "WORLDPOL":   WorldPolHarvester,
            "INDUSTRIAL": IndustrialHarvester,
        }
        for domain_id, HarvClass in harvester_map.items():
            harvester = HarvClass(self._bus)
            self._domains[domain_id] = VaraScanDomain(
                harvester=harvester,
                epistemic_bus=self._ep_bus,
                history_depth=history_depth,
            )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start all domain cadence loops concurrently."""
        if self._running:
            raise RuntimeError("VaraDispatcher already running")
        self._running = True
        await asyncio.gather(*[d.start() for d in self._domains.values()])
        logger.info("VaraDispatcher started — all %d channels active", len(self._domains))

    async def stop(self) -> None:
        """Gracefully stop all domain loops."""
        await asyncio.gather(*[d.stop() for d in self._domains.values()])
        self._running = False
        logger.info("VaraDispatcher stopped")

    async def __aenter__(self) -> "VaraDispatcher":
        await self.start()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.stop()

    # ------------------------------------------------------------------
    # On-demand scan
    # ------------------------------------------------------------------

    async def scan_all(self) -> dict[str, DomainScanResult | None]:
        """
        Trigger one scan cycle across all channels simultaneously.
        Returns {domain_id: DomainScanResult | None}.
        """
        results = await asyncio.gather(
            *[d.scan_once() for d in self._domains.values()],
            return_exceptions=True,
        )
        output: dict[str, DomainScanResult | None] = {}
        for domain_id, res in zip(self._domains.keys(), results):
            if isinstance(res, Exception):
                logger.error("[%s] scan_all error: %s", domain_id, res)
                output[domain_id] = None
            else:
                output[domain_id] = res

        # After scanning all, detect cross-domain signals
        self._detect_cross_domain(output)
        return output

    async def scan_domain(self, domain_id: str) -> DomainScanResult | None:
        """Trigger one scan for a specific domain."""
        domain = self._domains.get(domain_id.upper())
        if not domain:
            raise KeyError(f"Unknown domain: {domain_id}")
        return await domain.scan_once()

    # ------------------------------------------------------------------
    # Cross-domain signal detection
    # ------------------------------------------------------------------

    def _detect_cross_domain(
        self, results: dict[str, DomainScanResult | None]
    ) -> None:
        """
        Analyse latest scan batch for cross-domain signals.
        Three detection rules:

        Rule 1 — Anomaly Cascade:
            ≥3 domains with ≥1 anomaly each in the same window.

        Rule 2 — Confidence Collapse:
            ≥2 domains with confidence_score < 0.50.

        Rule 3 — Drift Divergence:
            One domain drift direction UP/CHAOTIC AND another DOWN/FLAT
            with magnitude difference > 0.3.
        """
        valid = {k: v for k, v in results.items() if v is not None}
        if not valid:
            return

        # Rule 1: Anomaly cascade
        anomalous_domains = [
            did for did, res in valid.items()
            if len(res.result.anomalies) >= 1
        ]
        if len(anomalous_domains) >= 3:
            sig = CrossDomainSignal(
                signal_type="ANOMALY_CASCADE",
                domains=anomalous_domains,
                description=f"Simultaneous anomalies across {len(anomalous_domains)} domains — "
                            f"systemic stress signal",
                severity="HIGH" if len(anomalous_domains) >= 4 else "MEDIUM",
                evidence={
                    did: [a.reason for a in res.result.anomalies]
                    for did, res in valid.items()
                    if res.result.anomalies
                },
            )
            self._cross_domain_signals.append(sig)
            logger.warning("CROSS-DOMAIN: %s — %s", sig.signal_type, sig.description)

        # Rule 2: Confidence collapse
        low_conf = [
            did for did, res in valid.items()
            if res.dip_packet.get("confidence_score", 1.0) < 0.50
        ]
        if len(low_conf) >= 2:
            confs = {
                did: res.dip_packet.get("confidence_score")
                for did, res in valid.items()
            }
            sig = CrossDomainSignal(
                signal_type="CONFIDENCE_COLLAPSE",
                domains=low_conf,
                description=f"Epistemic confidence collapse in {len(low_conf)} domains",
                severity="HIGH",
                evidence={"confidence_scores": confs},
            )
            self._cross_domain_signals.append(sig)
            logger.warning("CROSS-DOMAIN: %s — %s", sig.signal_type, sig.description)

        # Rule 3: Drift divergence
        drifts = {}
        for did, res in valid.items():
            di_list = res.dip_packet.get("drift_indicators", [])
            if di_list:
                di = di_list[0]
                drifts[did] = {
                    "direction": di.get("direction", "FLAT"),
                    "magnitude": float(di.get("magnitude", 0.0)),
                }

        up_domains   = [d for d, v in drifts.items() if v["direction"] in ("UP", "CHAOTIC")]
        down_domains = [d for d, v in drifts.items() if v["direction"] in ("DOWN", "FLAT")]

        if up_domains and down_domains:
            max_up   = max(drifts[d]["magnitude"] for d in up_domains)
            max_down = max(drifts[d]["magnitude"] for d in down_domains)
            if abs(max_up - max_down) > 0.3:
                sig = CrossDomainSignal(
                    signal_type="DRIFT_DIVERGENCE",
                    domains=up_domains + down_domains,
                    description=f"Opposing drift vectors: {up_domains} ↑ vs {down_domains} ↓",
                    severity="MEDIUM",
                    evidence={
                        "up":   {d: drifts[d] for d in up_domains},
                        "down": {d: drifts[d] for d in down_domains},
                    },
                )
                self._cross_domain_signals.append(sig)
                logger.info("CROSS-DOMAIN: %s — %s", sig.signal_type, sig.description)

        # Trim history
        if len(self._cross_domain_signals) > 200:
            self._cross_domain_signals = self._cross_domain_signals[-200:]

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "dispatcher": "VaraDispatcher",
            "running":    self._running,
            "channels":   {did: d.stats() for did, d in self._domains.items()},
            "epistemic_bus_emitted": self._ep_bus.emitted_count,
            "cross_domain_signals": len(self._cross_domain_signals),
            "last_cross_domain": (
                self._cross_domain_signals[-1].to_dict()
                if self._cross_domain_signals else None
            ),
            "snapshot_at": datetime.utcnow().isoformat(),
        }

    def cross_domain_signals(self, last_n: int = 20) -> list[dict]:
        return [s.to_dict() for s in self._cross_domain_signals[-last_n:]]

    def domain(self, domain_id: str) -> VaraScanDomain:
        d = self._domains.get(domain_id.upper())
        if not d:
            raise KeyError(f"Unknown domain: {domain_id}")
        return d

    @property
    def domains(self) -> dict[str, VaraScanDomain]:
        return dict(self._domains)
