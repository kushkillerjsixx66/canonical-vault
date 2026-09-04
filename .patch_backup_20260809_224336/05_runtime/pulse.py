"""
pulse.py — Temporal Signal Activation Layer (Rank 5 / ~)
PATCH v1.1: IMPROVE activate() now wraps signal in full Pulse envelope
with timing, attention cost, and waveform metadata.
v1.0 was a trivial wrapper returning {'pulse': signal}.
"""
from __future__ import annotations
import time, uuid
from typing import Any

class Pulse:
    def __init__(self, lattice: Any) -> None:
        self.lattice = lattice
        self._cycle_count = 0
        self._total_attention = 0.0

    def activate(self, signal: Any) -> dict:
        self._cycle_count += 1
        pid = f"PLS-{self._cycle_count:05d}-{uuid.uuid4().hex[:6]}"
        if isinstance(signal, dict):
            content = signal.get("content", signal)
            is_weak = bool(signal.get("veil_flag"))
            is_silent = bool(signal.get("silence"))
        elif isinstance(signal, str):
            content = signal; is_weak = False; is_silent = not signal.strip()
        else:
            content = signal; is_weak = False; is_silent = signal is None
        waveform = "silent" if is_silent else ("weak" if is_weak else "standard")
        cost = 0.05 if is_silent else (0.2 if is_weak else 0.1)
        self._total_attention += cost
        return {"pulse_id": pid, "content": content, "original_signal": signal,
                "cycle": self._cycle_count, "ts_activated": time.time(),
                "attention_cost": cost, "waveform": waveform, "iv_sil_honoured": is_silent}

    def status(self) -> dict:
        return {"cycle_count": self._cycle_count, "total_attention": round(self._total_attention,4)}
