"""
agent.py — Cognitive Action Layer (Rank 2 / Ψ)
PATCH v1.1: IMPROVE act() now classifies epistemic posture and builds a
structured response envelope. v1.0 was a trivial wrapper {'agent_output': signal}.
"""
from __future__ import annotations
from typing import Any

POSTURE_ASSERT = "assert"; POSTURE_INFER = "infer"
POSTURE_QUESTION = "question"; POSTURE_SILENCE = "silence"

class Agent:
    def __init__(self, lattice: Any) -> None:
        self.lattice = lattice
        self._act_count = 0

    def act(self, signal: Any) -> dict:
        self._act_count += 1
        if isinstance(signal, dict):
            content = signal.get("content",""); waveform = signal.get("waveform","standard")
            att = signal.get("attention_cost", 0.0)
        else:
            content = str(signal) if signal is not None else ""; waveform = "standard"; att = 0.0
        if waveform == "silent" or not str(content).strip():
            return {"agent_output": None, "posture": POSTURE_SILENCE,
                    "coherence_score": 1.0, "cycle": self._act_count,
                    "attention_cost": 0.0, "iv_sil": True}
        cl = str(content).lower()
        if cl.endswith("?") or cl.startswith(("what","why","how","who","when","is ","are ","can ")):
            posture = POSTURE_QUESTION
        elif any(h in cl for h in ("i think","probably","likely","might","possibly")):
            posture = POSTURE_INFER
        else:
            posture = POSTURE_ASSERT
        coh = {POSTURE_ASSERT:0.95, POSTURE_INFER:0.80, POSTURE_QUESTION:0.90}.get(posture,0.85)
        act_cost = 0.5 if posture == POSTURE_ASSERT else 0.3
        return {"agent_output": {"response": f"[Lattice processed: {str(content)[:200]}]",
                                  "original": content, "posture": posture},
                "posture": posture, "coherence_score": coh,
                "cycle": self._act_count, "attention_cost": att + act_cost, "iv_sil": False}

    def status(self) -> dict:
        return {"act_count": self._act_count}
