"""
lattice_core.py — Lattice Orchestrator (Canonical Modular Architecture)
PATCH v1.1:
  FIX: Vault(self) caused TypeError because vault.py __init__(self) had no
       lattice param. vault.py is now patched to accept (self, lattice).
  REMOVE: Duplicate inline class definitions — use modular imports.
  ADD: Full 9-stage pipeline with proper signal routing + HUD.
"""
from __future__ import annotations
from agent import Agent
from sentinel import Sentinel
from pulse import Pulse
from echo import Echo
from threshold import Threshold
from veil import Veil
from rift import Rift
from stumpy import Stumpy
from vault import Vault          # FIX: vault.py now accepts __init__(self, lattice)

class Lattice:
    VERSION = "1.1.0-patch"

    def __init__(self) -> None:
        self.agent     = Agent(self)
        self.sentinel  = Sentinel(self)
        self.pulse     = Pulse(self)
        self.echo      = Echo(self)
        self.threshold = Threshold(self)
        self.veil      = Veil(self)
        self.rift      = Rift(self)
        self.stumpy    = Stumpy(self)
        self.vault     = Vault(self)        # FIX: was crashing; vault.py patched
        self._cycle_count = 0

    def run(self, raw_input: str) -> dict:
        self._cycle_count += 1
        cycle: dict = {"cycle": self._cycle_count, "raw_input": raw_input, "pipeline": []}
        # Stage 1 — Sentinel
        try:
            signal = self.sentinel.inspect(raw_input)
            cycle["pipeline"].append(("sentinel","pass"))
        except ValueError as exc:
            cycle.update({"pipeline": [("sentinel","block",str(exc))], "result": None, "blocked_at": "sentinel"})
            return cycle
        # Stage 2 — Veil
        vr = self.veil.filter(signal)
        cycle["pipeline"].append(("veil", vr.get("tier")))
        if vr.get("tier") == "QUARANTINE":
            cycle.update({"result": None, "blocked_at": "veil", "veil_reason": vr.get("reason")})
            return cycle
        signal = vr.get("pulse", signal)
        # Stage 3 — Threshold
        if not self.threshold.allow(signal):
            cycle.update({"result": None, "blocked_at": "threshold"})
            cycle["pipeline"].append(("threshold","deny"))
            return cycle
        cycle["pipeline"].append(("threshold","pass"))
        # Stage 4 — Pulse
        pe = self.pulse.activate(signal)
        cycle["pipeline"].append(("pulse", pe.get("waveform")))
        # Stage 5 — Agent
        ar = self.agent.act(pe)
        cycle["pipeline"].append(("agent", ar.get("posture")))
        # Stage 6 — Echo
        self.echo.record(ar, label=f"cycle_{self._cycle_count:05d}")
        cycle["pipeline"].append(("echo","recorded"))
        # Stage 7 — Vault
        self.vault.store(f"cycle_{self._cycle_count}", ar)
        cycle["pipeline"].append(("vault","stored"))
        # Stage 8 — Stumpy audit
        audit = self.stumpy.audit({"coherence_score": ar.get("coherence_score"),
                                   "attention_cost": ar.get("attention_cost")})
        cycle["pipeline"].append(("stumpy","pass" if audit["pass"] else "violations"))
        cycle["stumpy_audit"] = audit
        # Stage 9 — Rift
        rift_r = self.rift.explore(ar)
        cycle["rift_branches"] = rift_r.get("branch_count")
        cycle["result"] = ar.get("agent_output")
        cycle["coherence_score"] = ar.get("coherence_score")
        return cycle

    def hud(self) -> dict:
        return {"lattice_version": self.VERSION, "cycle_count": self._cycle_count,
                "components": {n: getattr(self,n).status() for n in
                               ["agent","sentinel","pulse","echo","threshold","veil","rift","stumpy","vault"]}}
