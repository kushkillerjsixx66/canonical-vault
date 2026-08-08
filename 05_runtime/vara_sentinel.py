"""
VARA Sentinel — G1/G2/G3 Governance Gates
Operator: JRM-01 @liminaljermo
Spec ref: Lattice Unified Spec §7, §8, §10
Authority: RANK 4 in module hierarchy

Gate definitions:
  G1 — Coherence: signal must meet novelty threshold (0.15) and keyword relevance
  G2 — Attention: max 100 signals per cycle; excess pruned or deferred
  G3 — Reversibility: signals are read-only evidence; always passes at harvest stage.
       Locks activate only at Vault commit.

Error codes (§10):
  Tier 1: INVARIANT_VIOLATION, SENTINEL_LOCK_BYPASS
  Tier 2: G1_BLOCK, G2_BUDGET_EXCEEDED, G3_CHAIN_BROKEN

VI·BND enforced — Sentinel classifies and gates. It does not interpret or direct.
"""

import datetime
import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum

# ─── THRESHOLDS ──────────────────────────────────────────────────────────────

G1_NOVELTY_THRESHOLD = 0.15       # minimum novelty_score to pass coherence gate
G2_ATTENTION_BUDGET  = 100        # max signals per cycle
G3_REVERSIBILITY     = True       # signals are always reversible at harvest stage

# ─── GATE RESULTS ────────────────────────────────────────────────────────────

class GateVerdict(Enum):
    PASS  = "PASS"
    BLOCK = "BLOCK"
    DEFER = "DEFER"
    PRUNE = "PRUNE"


@dataclass
class GateResult:
    gate:      str
    verdict:   GateVerdict
    reason:    str
    signal_id: str
    score:     Optional[float] = None


@dataclass
class SentinelReport:
    sentinel_id:       str
    scan_id:           str
    timestamp:         str
    g1_threshold:      float
    g2_budget:         int
    total_input:       int
    passed:            int
    blocked:           int
    pruned:            int
    deferred:          int
    gate_log:          list
    passed_signals:    list
    blocked_signals:   list
    pruned_signals:    list
    deferred_signals:  list
    tier2_errors:      list
    locked:            bool = False   # True if Sentinel Lock activated (Tier 1)


# ─── GATE IMPLEMENTATIONS ────────────────────────────────────────────────────

def gate_g1(signal: dict) -> GateResult:
    """
    G1 — Coherence Primacy (I-COH)
    Signal must meet novelty_score threshold AND have non-empty content.
    Failure: node downgraded → BLOCK.
    """
    novelty = signal.get("novelty_score", 0.0)
    content = signal.get("content", "").strip()
    title   = signal.get("title", "").strip()

    if not content and not title:
        return GateResult(
            gate="G1",
            verdict=GateVerdict.BLOCK,
            reason="empty content and title — no coherence value",
            signal_id=signal.get("source_id", "unknown"),
            score=0.0,
        )

    if novelty < G1_NOVELTY_THRESHOLD:
        return GateResult(
            gate="G1",
            verdict=GateVerdict.BLOCK,
            reason=f"novelty_score {novelty:.3f} below threshold {G1_NOVELTY_THRESHOLD}",
            signal_id=signal.get("source_id", "unknown"),
            score=novelty,
        )

    return GateResult(
        gate="G1",
        verdict=GateVerdict.PASS,
        reason=f"novelty {novelty:.3f} >= {G1_NOVELTY_THRESHOLD}; content present",
        signal_id=signal.get("source_id", "unknown"),
        score=novelty,
    )


def gate_g2(
    signal:  dict,
    current_count: int,
) -> GateResult:
    """
    G2 — Attention Budget (II·ATT)
    If cycle already has G2_ATTENTION_BUDGET signals, excess are PRUNED.
    Signals 90-100 are DEFERRED (soft limit warning zone).
    """
    sid = signal.get("source_id", "unknown")

    if current_count >= G2_ATTENTION_BUDGET:
        return GateResult(
            gate="G2",
            verdict=GateVerdict.PRUNE,
            reason=f"attention budget exhausted ({current_count}/{G2_ATTENTION_BUDGET})",
            signal_id=sid,
        )

    if current_count >= int(G2_ATTENTION_BUDGET * 0.90):
        return GateResult(
            gate="G2",
            verdict=GateVerdict.DEFER,
            reason=f"soft limit zone ({current_count}/{G2_ATTENTION_BUDGET}) — deferring",
            signal_id=sid,
        )

    return GateResult(
        gate="G2",
        verdict=GateVerdict.PASS,
        reason=f"within budget ({current_count}/{G2_ATTENTION_BUDGET})",
        signal_id=sid,
    )


def gate_g3(signal: dict) -> GateResult:
    """
    G3 — Reversibility (III·REV)
    At harvest stage, all signals are read-only evidence → always PASS.
    Lock activates only during Vault commit (handled in vara_veil_vault.py).
    """
    sid = signal.get("source_id", "unknown")
    return GateResult(
        gate="G3",
        verdict=GateVerdict.PASS,
        reason="harvest stage — signals are read-only evidence; reversibility preserved",
        signal_id=sid,
    )


# ─── SENTINEL RUNNER ─────────────────────────────────────────────────────────

def run_sentinel(signals: list[dict], scan_id: str) -> SentinelReport:
    """
    Run G1 → G2 → G3 on every signal.
    Returns a full SentinelReport with per-gate verdicts and sorted signal lists.
    """
    sentinel_id = str(uuid.uuid4())
    timestamp   = datetime.datetime.utcnow().isoformat()

    passed_signals   = []
    blocked_signals  = []
    pruned_signals   = []
    deferred_signals = []
    gate_log         = []
    tier2_errors     = []

    passed_count = 0

    for sig in signals:
        sid = sig.get("source_id", "unknown")

        # G1 ── coherence
        r1 = gate_g1(sig)
        gate_log.append({
            "gate":      r1.gate,
            "verdict":   r1.verdict.value,
            "reason":    r1.reason,
            "signal_id": r1.signal_id,
            "score":     r1.score,
        })

        if r1.verdict == GateVerdict.BLOCK:
            blocked_signals.append(sig)
            tier2_errors.append(f"G1_BLOCK:{sid}")
            continue

        # G2 ── attention budget
        r2 = gate_g2(sig, passed_count)
        gate_log.append({
            "gate":      r2.gate,
            "verdict":   r2.verdict.value,
            "reason":    r2.reason,
            "signal_id": r2.signal_id,
            "score":     None,
        })

        if r2.verdict == GateVerdict.PRUNE:
            pruned_signals.append(sig)
            tier2_errors.append(f"G2_BUDGET_EXCEEDED:{sid}")
            continue

        if r2.verdict == GateVerdict.DEFER:
            deferred_signals.append(sig)
            continue

        # G3 ── reversibility (always passes at harvest)
        r3 = gate_g3(sig)
        gate_log.append({
            "gate":      r3.gate,
            "verdict":   r3.verdict.value,
            "reason":    r3.reason,
            "signal_id": r3.signal_id,
            "score":     None,
        })

        passed_signals.append(sig)
        passed_count += 1

    return SentinelReport(
        sentinel_id=sentinel_id,
        scan_id=scan_id,
        timestamp=timestamp,
        g1_threshold=G1_NOVELTY_THRESHOLD,
        g2_budget=G2_ATTENTION_BUDGET,
        total_input=len(signals),
        passed=len(passed_signals),
        blocked=len(blocked_signals),
        pruned=len(pruned_signals),
        deferred=len(deferred_signals),
        gate_log=gate_log,
        passed_signals=passed_signals,
        blocked_signals=blocked_signals,
        pruned_signals=pruned_signals,
        deferred_signals=deferred_signals,
        tier2_errors=tier2_errors,
        locked=False,
    )


def sentinel_to_vault_handoff(report: SentinelReport) -> dict:
    """
    Package the passed + deferred signals for handoff to vara_veil_vault.route_signals().
    Returns the dict expected by route_signals(passed_signals, deferred_signals, scan_id).
    """
    return {
        "passed_signals":   report.passed_signals,
        "deferred_signals": report.deferred_signals,
        "scan_id":          report.scan_id,
        "sentinel_id":      report.sentinel_id,
    }
