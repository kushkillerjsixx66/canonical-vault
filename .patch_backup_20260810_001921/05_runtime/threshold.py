"""
threshold.py — Governance Gate Enforcement
PATCH v1.1: FIX allow() returned True unconditionally. Now enforces G1/G2/G3.
"""
from __future__ import annotations
from typing import Any

class Threshold:
    def __init__(self, lattice: Any) -> None:
        self.lattice = lattice
        self._g1_threshold = 0.75
        self._g2_budget = 10.0
        self._g2_used = 0.0
        self._denied_count = 0
        self._passed_count = 0

    def allow(self, pulse: Any) -> bool:
        """FIX: v1.0 always returned True — no gate was ever enforced."""
        if pulse is None:
            self._denied_count += 1
            return False
        if isinstance(pulse, str):
            pulse = {"content": pulse}
        if not isinstance(pulse, dict):
            self._denied_count += 1
            return False
        coh = pulse.get("coherence_score")
        if coh is not None and isinstance(coh, (int,float)) and coh < self._g1_threshold:
            self._denied_count += 1
            pulse["gate_denial"] = f"G1: coherence {coh} < {self._g1_threshold}"
            return False
        cost = pulse.get("attention_cost", 0.1)
        if isinstance(cost, (int,float)):
            if cost > (self._g2_budget - self._g2_used):
                self._denied_count += 1
                pulse["gate_denial"] = f"G2: cost {cost} exceeds remaining budget"
                return False
            self._g2_used += cost
        if pulse.get("requires_anchor") and not pulse.get("anchor_ok"):
            self._denied_count += 1
            pulse["gate_denial"] = "G3: anchor required but not confirmed"
            return False
        self._passed_count += 1
        return True

    def reset_attention_budget(self) -> None:
        self._g2_used = 0.0

    def status(self) -> dict:
        return {"g2_budget": self._g2_budget, "g2_used": round(self._g2_used,4),
                "passed": self._passed_count, "denied": self._denied_count}
