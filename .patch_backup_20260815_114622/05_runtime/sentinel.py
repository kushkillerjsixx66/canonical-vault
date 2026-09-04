"""
sentinel.py — Gate Enforcement Layer (Rank 4)
PATCH v1.1: FIX inspect() was returning bool (signal is not None).
Downstream pipeline received True/False instead of message content.
Now returns the validated signal dict or raises ValueError on failure.
"""
from __future__ import annotations
from typing import Any

class Sentinel:
    def __init__(self, lattice: Any) -> None:
        self.lattice = lattice
        self._blocked_count: int = 0
        self._passed_count: int = 0

    def inspect(self, signal: Any) -> dict:
        """FIX: was 'return signal is not None' — returned bool, lost message."""
        if signal is None:
            self._blocked_count += 1
            raise ValueError("[SENTINEL] Gate G0 — null signal rejected.")
        if isinstance(signal, str):
            signal = {"content": signal, "type": "raw"}
        if not isinstance(signal, dict):
            self._blocked_count += 1
            raise ValueError(f"[SENTINEL] Gate G0 — unexpected type: {type(signal).__name__}")
        content = signal.get("content", "")
        if not content or not str(content).strip():
            self._blocked_count += 1
            raise ValueError("[SENTINEL] Gate G1 — empty content rejected.")
        _FAB = ("i am certain that", "it is known that")
        if any(m in str(content).lower() for m in _FAB):
            signal["sentinel_flag"] = "G4_FABRICATION_RISK"
        signal.setdefault("sentinel_passed", True)
        signal.setdefault("gate_version", "1.1")
        self._passed_count += 1
        return signal

    def status(self) -> dict:
        return {"passed": self._passed_count, "blocked": self._blocked_count, "gate_version": "1.1"}
