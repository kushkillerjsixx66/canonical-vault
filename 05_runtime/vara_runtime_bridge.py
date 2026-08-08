"""
vara_runtime_bridge.py — Old Vara → Canon CDS-Ω1 Integration Bridge
Operator: JRM-01 @liminaljermo
Version: 1.0.0   Generated: 2026-08-08

Connects the legacy Vara scan pipeline (05_runtime/vara_*.py) to the
CDS-Ω1 analytical framework (canon/vara/) via CITL message bus.

Architecture:
    VaraScanReport (old)
        └── VaraRuntimeBridge.ingest_scan_report()
                └── _map_signal_to_domain()   ← plane → DomainID
                └── _build_dip()              ← Signal → DIP packet
                └── CITL.publish()            → canon.dip.raw.<DOMAIN>

    vault_signals.json (old)
        └── VaraRuntimeBridge.ingest_from_vault()
                └── same path as above

Plane → Canon Domain mapping:
    tech / scientific / adjacent_possible → ECON + INDUSTRIAL (innovation pressure)
    economic                              → ECON
    geopolitical                          → GEOPOL + WORLDPOL
    social / persons                      → WORLDPOL
    dark                                  → CRYPTO (adversarial signals)

Sentinel gate results are preserved as anomaly_flags on the DIP.
Veil-promoted signals receive a confidence penalty (-0.15) to signal
their deferred provenance.

Invariants:
    I·SRC  — source_id and plane provenance passed through to DIP
    II·SCR — confidence derived from novelty+velocity; no inflation
    V·SIL  — empty vault or null scan report is valid; logged only
    VI·BND — bridge routes signals only; no directives issued
"""

from __future__ import annotations

import asyncio
import datetime
import hashlib
import json
import logging
import os
import sys
from typing import Optional

logger = logging.getLogger("vara.runtime_bridge")

# ─── PLANE → DOMAIN MAP ──────────────────────────────────────────────────────
# Maps old vara planes to canon DomainID strings.
# A plane may map to multiple domains (signal duplicated to each).

PLANE_TO_DOMAINS = {
    "tech":               ["ECON", "INDUSTRIAL"],
    "scientific":         ["ECON", "INDUSTRIAL"],
    "adjacent_possible":  ["ECON", "INDUSTRIAL"],
    "economic":           ["ECON"],
    "geopolitical":       ["GEOPOL", "WORLDPOL"],
    "social":             ["WORLDPOL"],
    "persons":            ["WORLDPOL"],
    "dark":               ["CRYPTO"],
}

# Fallback domain when plane is unknown
_FALLBACK_DOMAIN = "ECON"

# Confidence discount for veil-promoted signals (deferred provenance)
_VEIL_CONFIDENCE_PENALTY = 0.15

# ─── TOPIC BUILDER ───────────────────────────────────────────────────────────

def _dip_topic(domain_id: str) -> str:
    return f"canon.dip.raw.{domain_id.lower()}"


# ─── DIP BUILDER ─────────────────────────────────────────────────────────────

def _build_dip(
    signal:    dict,
    domain_id: str,
    scan_id:   str,
    veil_promoted: bool = False,
) -> dict:
    """
    Convert one old-vara signal dict into a Canon DIP packet.

    DIP schema (from CDS-Ω1 spec §2.1):
        type, version, domain_id, timestamp, signal_set,
        weight_vector, confidence_score, drift_indicators,
        anomaly_flags, metadata
    """
    novelty    = signal.get("novelty_score",  0.0)
    velocity   = signal.get("velocity_score", 0.0)
    raw_vel    = signal.get("raw_velocity",   0.0)
    source_id  = signal.get("source_id", "unknown")
    plane      = signal.get("plane", "unknown")
    title      = signal.get("title", "")
    content    = signal.get("content", "")
    url        = signal.get("url", "")
    feed_tier  = signal.get("feed_tier", "main")

    # Confidence: blend novelty + velocity; penalise veil-promoted
    confidence = round(
        min(1.0, (novelty * 0.6 + velocity * 0.4))
        - (_VEIL_CONFIDENCE_PENALTY if veil_promoted else 0.0),
        4,
    )
    confidence = max(0.0, confidence)

    # Weight: fringe feeds carry less weight
    weight = 0.65 if feed_tier == "fringe" else 0.80

    # Spike flag from drift stage
    spike = signal.get("velocity_spike", False)

    anomaly_flags = []
    if spike:
        anomaly_flags.append({
            "code":        "VELOCITY_SPIKE",
            "severity":    "MEDIUM",
            "description": f"velocity z-score spike on plane={plane}",
        })
    if veil_promoted:
        anomaly_flags.append({
            "code":        "VEIL_PROMOTED",
            "severity":    "LOW",
            "description": "signal earned passage through Veil after recurrence",
        })
    if novelty < 0.20:
        anomaly_flags.append({
            "code":        "LOW_NOVELTY",
            "severity":    "LOW",
            "description": f"novelty {novelty:.3f} near gate floor",
        })

    # Provenance UID (I·SRC)
    uid = "dip:" + hashlib.sha256(
        f"{source_id}:{domain_id}:{scan_id}".encode()
    ).hexdigest()[:16]

    return {
        "type":       "DIP",
        "version":    "1.0",
        "uid":        uid,
        "domain_id":  domain_id,
        "timestamp":  datetime.datetime.utcnow().isoformat(),
        "signal_set": [
            {
                "signal_type": "CONTENT_SIGNAL",
                "value":       novelty,
                "weight":      weight,
                "confidence":  confidence,
                "source":      url or source_id,
            }
        ],
        "weight_vector":    [weight],
        "confidence_score": confidence,
        "drift_indicators": [
            {
                "vector":     [raw_vel, velocity],
                "magnitude":  round(abs(raw_vel - velocity), 4),
                "direction":  "UP" if velocity > raw_vel else ("FLAT" if velocity == raw_vel else "DOWN"),
                "volatility": round(abs(velocity - 0.5), 4),
            }
        ],
        "anomaly_flags": anomaly_flags,
        "metadata": {
            "source_id":     source_id,
            "plane":         plane,
            "title":         title[:200],
            "content":       content[:300],
            "url":           url,
            "feed_tier":     feed_tier,
            "scan_id":       scan_id,
            "veil_promoted": veil_promoted,
            "origin":        "vara_runtime_bridge/05_runtime",
        },
    }


# ─── BRIDGE CLASS ────────────────────────────────────────────────────────────

class VaraRuntimeBridge:
    """
    Ingests old-Vara scan output and publishes DIP packets to the CITL bus.

    Usage (standalone, no CITL):
        bridge = VaraRuntimeBridge()
        dips = bridge.ingest_scan_report(report_dict)

    Usage (with CITL):
        bridge = VaraRuntimeBridge(citl=citl_instance)
        await bridge.ingest_scan_report_async(report_dict)
    """

    def __init__(self, citl=None):
        """
        Parameters
        ----------
        citl : CITL | None
            Live Canon Intelligence Transport Layer instance.
            When None, DIPs are returned but not published.
        """
        self.citl        = citl
        self._dip_count  = 0
        self._scan_count = 0

    # ── Public: sync ────────────────────────────────────────────────────────

    def ingest_scan_report(self, report: dict) -> list[dict]:
        """
        Convert a VaraScanReport dict → list of DIP packets.

        Publishes to CITL synchronously if available (fire-and-forget via
        asyncio.ensure_future when inside a running loop).

        Returns the list of DIP dicts regardless.
        """
        dips = self._report_to_dips(report)
        if self.citl and dips:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    for dip in dips:
                        asyncio.ensure_future(
                            self.citl.publish(_dip_topic(dip["domain_id"]), dip)
                        )
                else:
                    loop.run_until_complete(self._publish_all(dips))
            except Exception as e:
                logger.error("CITL publish failed: %s", e, exc_info=True)
        self._dip_count  += len(dips)
        self._scan_count += 1
        return dips

    async def ingest_scan_report_async(self, report: dict) -> list[dict]:
        """Async version — use inside a running event loop."""
        dips = self._report_to_dips(report)
        if self.citl:
            await self._publish_all(dips)
        self._dip_count  += len(dips)
        self._scan_count += 1
        return dips

    def ingest_from_vault(self, vault_path: str = "vault_signals.json") -> list[dict]:
        """
        Load committed vault signals from disk and convert to DIPs.

        Use this to re-hydrate the canon pipeline from persisted Vara state.
        """
        if not os.path.exists(vault_path):
            logger.info("V·SIL: vault not found at %s", vault_path)
            return []
        try:
            with open(vault_path, "r") as f:
                vault_entries = json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Failed to load vault: %s", e)
            return []

        dips = []
        for entry in vault_entries:
            signal       = entry.get("signal", entry)
            veil_promo   = entry.get("origin", "") == "veil_promoted"
            scan_id      = entry.get("scan_id", "vault_replay")
            plane        = signal.get("plane", "")
            target_domains = PLANE_TO_DOMAINS.get(plane, [_FALLBACK_DOMAIN])

            for domain_id in target_domains:
                dip = _build_dip(signal, domain_id, scan_id, veil_promoted=veil_promo)
                dips.append(dip)

        logger.info("Vault replay: %d vault entries → %d DIPs", len(vault_entries), len(dips))
        self._dip_count += len(dips)
        return dips

    def status(self) -> dict:
        return {
            "bridge":      "VaraRuntimeBridge",
            "version":     "1.0.0",
            "scans_ingested": self._scan_count,
            "dips_emitted":   self._dip_count,
            "citl_linked":    self.citl is not None,
        }

    # ── Internal ────────────────────────────────────────────────────────────

    def _report_to_dips(self, report: dict) -> list[dict]:
        """Convert VaraScanReport dict → flat list of DIP packets."""
        if not isinstance(report, dict):
            logger.warning("ingest_scan_report: expected dict, got %s", type(report))
            return []

        scan_id  = report.get("scan_id", "unknown")
        signals  = report.get("signals", [])

        if not signals:
            logger.info("V·SIL: scan_id=%s has no signals — bridge no-op", scan_id[:8])
            return []

        dips = []
        for sig in signals:
            plane          = sig.get("plane", "")
            veil_promoted  = sig.get("veil_promoted", False)
            target_domains = PLANE_TO_DOMAINS.get(plane, [_FALLBACK_DOMAIN])

            if not target_domains:
                logger.debug("No domain mapping for plane='%s'", plane)
                continue

            for domain_id in target_domains:
                dip = _build_dip(sig, domain_id, scan_id, veil_promoted=veil_promoted)
                dips.append(dip)

        logger.info(
            "scan_id=%s  signals=%d  dips=%d",
            scan_id[:8], len(signals), len(dips)
        )
        return dips

    async def _publish_all(self, dips: list[dict]) -> None:
        """Publish all DIPs to CITL in parallel."""
        if not dips or not self.citl:
            return
        await asyncio.gather(
            *(self.citl.publish(_dip_topic(d["domain_id"]), d) for d in dips),
            return_exceptions=True,
        )


# ─── STANDALONE DEMO ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

    print("VaraRuntimeBridge — standalone test")
    print("=" * 50)

    bridge = VaraRuntimeBridge(citl=None)

    # Synthetic minimal VaraScanReport
    mock_report = {
        "scan_id":    "test-1234-abcd",
        "scan_label": "bridge_demo",
        "timestamp":  datetime.datetime.utcnow().isoformat(),
        "signals": [
            {
                "source_id":     "src:abc123",
                "plane":         "tech",
                "content":       "New LLM inference benchmark breaks throughput records",
                "title":         "New LLM inference benchmark",
                "url":           "https://example.com/llm-bench",
                "raw_velocity":  0.85,
                "novelty_score": 0.72,
                "velocity_score": 0.80,
                "feed_tier":     "main",
                "velocity_spike": True,
            },
            {
                "source_id":     "src:def456",
                "plane":         "geopolitical",
                "content":       "New sanctions package targeting semiconductor exports",
                "title":         "Semiconductor export sanctions",
                "url":           "https://example.com/sanctions",
                "raw_velocity":  0.60,
                "novelty_score": 0.55,
                "velocity_score": 0.58,
                "feed_tier":     "main",
                "velocity_spike": False,
            },
            {
                "source_id":     "src:ghi789",
                "plane":         "dark",
                "content":       "Zero-day exploit targeting AI infrastructure detected",
                "title":         "AI infrastructure zero-day",
                "url":           "https://example.com/zero-day",
                "raw_velocity":  0.95,
                "novelty_score": 0.88,
                "velocity_score": 0.91,
                "feed_tier":     "main",
                "velocity_spike": True,
                "veil_promoted": True,
            },
        ],
    }

    dips = bridge.ingest_scan_report(mock_report)

    print(f"\nInput signals : {len(mock_report['signals'])}")
    print(f"Output DIPs   : {len(dips)}")
    print()

    for i, dip in enumerate(dips, 1):
        anom = [a["code"] for a in dip.get("anomaly_flags", [])]
        print(
            f"  [{i}] domain={dip['domain_id']:<12} "
            f"confidence={dip['confidence_score']:.3f}  "
            f"anomalies={anom}  "
            f"title={dip['metadata']['title'][:40]}"
        )

    print()
    print("Bridge status:", bridge.status())

    # Test vault replay if vault_signals.json exists locally
    if os.path.exists("vault_signals.json"):
        print("\nVault replay test:")
        vault_dips = bridge.ingest_from_vault("vault_signals.json")
        print(f"  Replayed {len(vault_dips)} DIPs from vault")
    else:
        print("\nNo vault_signals.json found — skipping vault replay test")
