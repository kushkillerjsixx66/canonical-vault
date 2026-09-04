"""
stumpy.py — Integrity Audit & Decay Lifecycle (Rank 7 / Ω)
PATCH v1.1:
  FIX: invariants had 5 wrong entries incl 'entropy' (not canonical).
       Now all 6 correct: coherence, reversibility, attention, silence, decay, signal.
  FIX: audit() only checked dict key presence — meaningless.
       Now evaluates actual threshold values per invariant spec.
"""
from __future__ import annotations
import time
from typing import Any

CANONICAL_INVARIANTS = [
    "coherence",     # I·COH
    "reversibility", # II·REV
    "attention",     # III·ATT
    "silence",       # IV·SIL
    "decay",         # V·DEC
    "signal",        # VI·SIG
]

class Stumpy:
    def __init__(self, lattice: Any) -> None:
        self.lattice = lattice
        self.invariants: list = CANONICAL_INVARIANTS   # FIX: was wrong list
        self._audit_log: list = []
        self._decay_log: list = []

    def audit(self, result: dict | None = None) -> dict:
        """FIX: v1.0 only checked 'invariant in result' (key presence)."""
        if result is None:
            result = {}
        report: dict = {}
        violations: list = []
        coh = result.get("coherence_score")
        if coh is not None:
            if isinstance(coh, (int, float)) and coh >= 0.75:
                report["coherence"] = "pass"
            else:
                report["coherence"] = "fail"
                violations.append(f"I·COH score {coh} < 0.75")
        else:
            report["coherence"] = "skip"
        report["reversibility"] = "fail" if result.get("overwrite_detected") else "pass"
        if result.get("overwrite_detected"):
            violations.append("II·REV overwrite detected")
        att = result.get("attention_cost")
        if att is not None:
            report["attention"] = "pass" if (isinstance(att, (int,float)) and att <= 10.0) else "fail"
            if report["attention"] == "fail": violations.append(f"III·ATT cost {att} > 10.0")
        else:
            report["attention"] = "skip"
        sil = result.get("silence")
        report["silence"] = ("pass" if isinstance(sil, bool) else "fail") if sil is not None else "skip"
        dec = result.get("decay_ts")
        report["decay"] = ("pass" if (isinstance(dec,(int,float)) and dec > 0) else "fail") if dec is not None else "skip"
        if result.get("entropy_spike"):
            ws = result.get("weak_signals")
            report["signal"] = "pass" if (isinstance(ws, list) and ws) else "fail"
            if report["signal"] == "fail": violations.append("VI·SIG weak_signals missing on entropy_spike")
        else:
            report["signal"] = "skip"
        entry = {"invariant_results": report, "violations": violations, "pass": len(violations) == 0}
        self._audit_log.append(entry)
        return entry

    def decay_check(self, entries: list, decay_window_days: int = 30) -> list:
        cutoff = time.time() - (decay_window_days * 86400)
        stale = [e.get("key","?") for e in entries if e.get("ts", 0) < cutoff]
        self._decay_log.extend({"key": k, "action": "flagged"} for k in stale)
        return stale

    def status(self) -> dict:
        return {"invariants": self.invariants, "audit_count": len(self._audit_log)}
