"""
vara_scan.py — Vara Scan Pipeline Orchestrator
Operator: JRM-01 @liminaljermo
Spec ref: Lattice Unified Spec §3, §5, §7, §8

Pipeline stages:
    stage_intake  → harvest signals from active planes via vara_harvesters
    stage_drift   → score velocity changes; tag anomalies
    stage_cluster → group signals by semantic proximity
    run_vara_scan → orchestrate all stages + sentinel + veil/vault routing

Output: VaraScanReport (dict-serializable)
"""

from vara_sentinel import run_sentinel, sentinel_to_vault_handoff
from vara_veil_vault import route_signals
from vara_harvesters import harvest_plane

import hashlib
import json
import datetime
import uuid
import os
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger("vara.scan")

DRIFT_LOG_PATH = "vara_drift_log.json"
OUTPUT_DIR     = "vara_output"

VALID_PLANES = {
    "social", "scientific", "tech", "adjacent_possible",
    "economic", "dark", "geopolitical", "persons",
}

VALID_FORMATS = {"markdown", "alert", "brief", "json", "graph"}


# ─── CONFIG ──────────────────────────────────────────────────────────────────

@dataclass
class VaraConfig:
    keywords:                list
    sweep_depth_hours:       int
    active_planes:           list
    scan_label:              str
    velocity_spike_threshold: float       = 3.5
    fringe_to_main_ratio:    float        = 0.40
    output_formats:          list         = field(default_factory=lambda: ["markdown", "json"])
    extra_rss_feeds:         list         = field(default_factory=list)
    extra_substacks:         list         = field(default_factory=list)
    config_hash:             str          = ""

    def compute_hash(self) -> str:
        payload = json.dumps(
            {
                "keywords":           sorted(self.keywords),
                "sweep_depth_hours":  self.sweep_depth_hours,
                "active_planes":      sorted(self.active_planes),
                "scan_label":         self.scan_label,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


# ─── SIGNAL ───────────────────────────────────────────────────────────────────

@dataclass
class Signal:
    source_id:      str
    plane:          str
    content:        str
    url:            str
    raw_velocity:   float
    novelty_score:  float
    velocity_score: float        = 0.0
    cluster_id:     Optional[str] = None
    title:          str          = ""
    feed_tier:      str          = "main"


# ─── REPORT ──────────────────────────────────────────────────────────────────

@dataclass
class VaraScanReport:
    scan_id:       str
    scan_label:    str
    timestamp:     str
    config_hash:   str
    keywords:      list
    active_planes: list
    signals:       list
    clusters:      list
    drift_log:     list
    null_result:   bool
    error:         Optional[str] = None


# ─── STAGE: INTAKE ───────────────────────────────────────────────────────────

def stage_intake(config: VaraConfig) -> tuple:
    """
    Validate config; harvest signals from all active planes.

    Returns (signals: list[dict], errors: list[str]).
    """
    errors = []

    if not config.keywords:
        errors.append("keywords empty")
    if config.sweep_depth_hours <= 0:
        errors.append("sweep_depth_hours must be > 0")
    if not config.active_planes:
        errors.append("active_planes empty")

    invalid = [p for p in config.active_planes if p not in VALID_PLANES]
    if invalid:
        errors.append(f"unknown planes: {invalid}")

    if errors:
        return [], errors

    all_signals = []
    for plane in config.active_planes:
        if plane not in VALID_PLANES:
            continue
        try:
            plane_sigs = harvest_plane(
                plane=plane,
                keywords=config.keywords,
                sweep_hours=config.sweep_depth_hours,
                extra_rss_feeds=config.extra_rss_feeds,
                extra_substacks=config.extra_substacks,
            )
            all_signals.extend(plane_sigs)
            logger.info("Intake plane=%s  signals=%d", plane, len(plane_sigs))
        except Exception as e:
            # V·SIL — plane failure logged, not propagated
            logger.error("Intake plane=%s failed: %s", plane, e, exc_info=True)

    return all_signals, errors


# ─── STAGE: DRIFT ────────────────────────────────────────────────────────────

def _load_drift_log() -> list:
    if not os.path.exists(DRIFT_LOG_PATH):
        return []
    try:
        with open(DRIFT_LOG_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def _save_drift_log(log: list) -> None:
    # Keep last 500 entries
    trimmed = log[-500:]
    with open(DRIFT_LOG_PATH, "w") as f:
        json.dump(trimmed, f, indent=2)


def stage_drift(
    signals:    list,
    config:     VaraConfig,
    scan_id:    str,
) -> tuple:
    """
    Compare raw_velocity against prior scan history.
    Tags signals with velocity_score and detects spikes.

    Returns (enriched_signals: list[dict], drift_entries: list[dict]).
    """
    drift_log    = _load_drift_log()
    drift_entries = []
    enriched     = []

    # Build plane->velocity history from prior log
    plane_history = {}
    for entry in drift_log[-100:]:
        p  = entry.get("plane", "")
        rv = entry.get("raw_velocity", 0.0)
        plane_history.setdefault(p, []).append(rv)

    for sig in signals:
        plane = sig.get("plane", "")
        rv    = sig.get("raw_velocity", 0.0)
        hist  = plane_history.get(plane, [])

        if hist:
            import statistics as _stats
            mean_rv = _stats.mean(hist)
            std_rv  = _stats.pstdev(hist) or 0.01
            z_score = (rv - mean_rv) / std_rv
            spike   = z_score >= config.velocity_spike_threshold
        else:
            z_score = 0.0
            spike   = False

        sig["velocity_score"] = round(max(0.0, min(1.0, rv + (z_score * 0.05))), 4)
        sig["velocity_spike"] = spike
        enriched.append(sig)

        entry = {
            "scan_id":      scan_id,
            "plane":        plane,
            "source_id":    sig.get("source_id", ""),
            "raw_velocity": rv,
            "z_score":      round(z_score, 4),
            "spike":        spike,
            "timestamp":    datetime.datetime.utcnow().isoformat(),
        }
        drift_entries.append(entry)

    _save_drift_log(drift_log + drift_entries)
    return enriched, drift_entries


# ─── STAGE: CLUSTER ──────────────────────────────────────────────────────────

def stage_cluster(signals: list) -> tuple:
    """
    Group signals into clusters by plane + novelty band.
    Returns (enriched_signals, clusters).

    Simple bucketing strategy:
      - Bucket key: (plane, novelty_band) where novelty_band = round(novelty*4)/4
      - Cluster ID: sha256(key)[:8]
    """
    from collections import defaultdict
    import hashlib

    buckets: dict = defaultdict(list)

    for sig in signals:
        plane   = sig.get("plane", "unknown")
        novelty = sig.get("novelty_score", 0.0)
        band    = round(novelty * 4) / 4          # quantise to 0.25 bands
        key     = f"{plane}:{band:.2f}"
        cid     = "c:" + hashlib.sha256(key.encode()).hexdigest()[:8]
        sig["cluster_id"] = cid
        buckets[cid].append(sig)

    enriched = [s for bucket in buckets.values() for s in bucket]

    clusters = [
        {
            "cluster_id":    cid,
            "plane":         members[0].get("plane", ""),
            "member_count":  len(members),
            "avg_novelty":   round(sum(m.get("novelty_score", 0) for m in members) / len(members), 4),
            "avg_velocity":  round(sum(m.get("velocity_score", 0) for m in members) / len(members), 4),
        }
        for cid, members in buckets.items()
    ]

    return enriched, clusters


# ─── MAIN RUNNER ─────────────────────────────────────────────────────────────

def run_vara_scan(config: VaraConfig) -> VaraScanReport:
    """
    Full Vara scan pipeline.

    1. Validate + harvest signals (stage_intake)
    2. Score drift / velocity (stage_drift)
    3. Cluster signals (stage_cluster)
    4. Gate through Sentinel (G1/G2/G3)
    5. Route through Veil/Vault
    6. Persist outputs
    7. Return VaraScanReport
    """
    scan_id   = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat()
    config.config_hash = config.compute_hash()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── Stage 1: intake ───────────────────────────────────────────────────────
    raw_signals, intake_errors = stage_intake(config)
    if intake_errors:
        logger.error("Intake validation errors: %s", intake_errors)
        return VaraScanReport(
            scan_id=scan_id,
            scan_label=config.scan_label,
            timestamp=timestamp,
            config_hash=config.config_hash,
            keywords=config.keywords,
            active_planes=config.active_planes,
            signals=[],
            clusters=[],
            drift_log=[],
            null_result=True,
            error="; ".join(intake_errors),
        )

    if not raw_signals:
        logger.info("V·SIL: scan_id=%s null result — no signals harvested", scan_id)
        return VaraScanReport(
            scan_id=scan_id,
            scan_label=config.scan_label,
            timestamp=timestamp,
            config_hash=config.config_hash,
            keywords=config.keywords,
            active_planes=config.active_planes,
            signals=[],
            clusters=[],
            drift_log=[],
            null_result=True,
        )

    # ── Stage 2: drift ────────────────────────────────────────────────────────
    drifted, drift_entries = stage_drift(raw_signals, config, scan_id)

    # ── Stage 3: cluster ──────────────────────────────────────────────────────
    clustered, clusters = stage_cluster(drifted)

    # ── Stage 4: sentinel ────────────────────────────────────────────────────
    sentinel_report = run_sentinel(clustered, scan_id)
    handoff         = sentinel_to_vault_handoff(sentinel_report)

    # ── Stage 5: veil/vault ───────────────────────────────────────────────────
    vault_report, veil_report = route_signals(
        passed_signals=handoff["passed_signals"],
        deferred_signals=handoff["deferred_signals"],
        scan_id=scan_id,
    )

    # ── Stage 6: persist output ───────────────────────────────────────────────
    output_signals = handoff["passed_signals"] + veil_report.promoted_signals
    report = VaraScanReport(
        scan_id=scan_id,
        scan_label=config.scan_label,
        timestamp=timestamp,
        config_hash=config.config_hash,
        keywords=config.keywords,
        active_planes=config.active_planes,
        signals=output_signals,
        clusters=clusters,
        drift_log=drift_entries[:50],    # truncate for report readability
        null_result=len(output_signals) == 0,
    )

    # Write JSON output
    out_path = os.path.join(OUTPUT_DIR, f"scan_{scan_id[:8]}.json")
    with open(out_path, "w") as f:
        json.dump(asdict(report), f, indent=2)

    logger.info(
        "Scan complete: id=%s  harvested=%d  passed=%d  deferred=%d  pruned=%d  clusters=%d",
        scan_id[:8],
        len(raw_signals),
        sentinel_report.passed,
        sentinel_report.deferred,
        sentinel_report.pruned,
        len(clusters),
    )

    return report
