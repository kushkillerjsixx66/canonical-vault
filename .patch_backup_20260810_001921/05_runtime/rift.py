"""
rift.py — State Exploration & Branching Layer (Rank 8 / ≈)
PATCH v1.1: IMPROVE explore() produces bifurcation map.
v1.0 returned state unchanged — pure pass-through stub.
"""
from __future__ import annotations
import copy
from typing import Any

class Rift:
    def __init__(self, lattice: Any) -> None:
        self.lattice = lattice
        self._explore_count = 0; self._branch_total = 0

    def explore(self, state: Any) -> dict:
        self._explore_count += 1
        if isinstance(state, str):
            state = {"content": state, "type": "text"}
        elif state is None:
            state = {"content": None, "type": "null"}
        sc = copy.deepcopy(state) if isinstance(state, dict) else {"content": state}
        content_str = str(sc.get("content","") or "")
        branch_a = {"interpretation": "literal", "content": content_str, "confidence": 0.90}
        branch_b = {"interpretation": "contextual",
                    "content": f"[contextual: {content_str[:80]}]", "confidence": 0.65}
        alts = [branch_b]
        if len(content_str) < 20:
            alts.append({"interpretation": "weak_signal",
                         "content": f"[weak signal: {content_str}]", "confidence": 0.40})
        self._branch_total += 1 + len(alts)
        return {"explore_id": self._explore_count, "original_state": sc,
                "primary": branch_a, "alternatives": alts,
                "delta": round(abs(branch_a["confidence"] - branch_b["confidence"]),4),
                "branch_count": 1 + len(alts), "ii_rev": True}

    def status(self) -> dict:
        return {"explore_count": self._explore_count, "branch_total": self._branch_total}
