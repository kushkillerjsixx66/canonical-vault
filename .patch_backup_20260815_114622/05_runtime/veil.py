"""
veil.py — Epistemic Quarantine & Filter Layer (Rank 6 / ∇)
PATCH v1.1: FIX filter() returned pulse unchanged — pure stub.
Now applies PASS / FLAG / QUARANTINE tiers with pattern matching.
"""
from __future__ import annotations
import hashlib, json, time
from typing import Any

TIER_PASS = "PASS"; TIER_FLAG = "FLAG"; TIER_QUARANTINE = "QUARANTINE"
_QUARANTINE = ("i am certain","guaranteed","delete all","override governance","system prompt")
_FLAG = ("probably","i think","maybe","might be")

class Veil:
    def __init__(self, lattice: Any) -> None:
        self.lattice = lattice
        self._quarantine: dict = {}
        self._pass_count = 0; self._flag_count = 0; self._quarantine_count = 0

    def filter(self, pulse: Any) -> dict:
        """FIX: v1.0 returned pulse unchanged with zero logic."""
        if pulse is None:
            return {"tier": TIER_QUARANTINE, "pulse": None, "reason": "null"}
        if isinstance(pulse, str):
            pulse = {"content": pulse}
        if isinstance(pulse, bool):
            return {"tier": TIER_QUARANTINE, "pulse": None,
                    "reason": f"boolean ({pulse}) — sentinel v1.0 pipeline bug"}
        if not isinstance(pulse, dict):
            return {"tier": TIER_QUARANTINE, "pulse": None, "reason": f"unexpected type {type(pulse)}"}
        content = str(pulse.get("content","")).lower()
        h = hashlib.sha256(json.dumps(pulse,default=str).encode()).hexdigest()[:12]
        for p in _QUARANTINE:
            if p in content:
                entry = {"pulse": pulse, "reason": f"QUARANTINE: '{p}'", "ts": time.time()}
                self._quarantine[h] = entry
                self._quarantine_count += 1
                return {"tier": TIER_QUARANTINE, "pulse": None, "reason": entry["reason"], "quarantine_key": h}
        flagged = [p for p in _FLAG if p in content]
        if flagged:
            pulse["veil_flag"] = f"EPISTEMIC_HEDGE: {', '.join(flagged)}"
            self._flag_count += 1
            return {"tier": TIER_FLAG, "pulse": pulse, "reason": pulse["veil_flag"]}
        pulse.setdefault("veil_cleared", True)
        self._pass_count += 1
        return {"tier": TIER_PASS, "pulse": pulse, "reason": "cleared"}

    def release(self, key: str) -> dict:
        e = self._quarantine.get(key)
        return {"found": True, "key": key, **e} if e else {"found": False, "key": key}

    def status(self) -> dict:
        return {"passed": self._pass_count, "flagged": self._flag_count, "quarantined": self._quarantine_count}
