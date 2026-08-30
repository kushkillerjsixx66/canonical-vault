"""
echo.py — Signal Trace & Record Layer
PATCH v1.1: ADD trace(key) — was MISSING; <Echo:Trace> had no implementation.
"""
from __future__ import annotations
import time, hashlib, json
from typing import Any

class Echo:
    def __init__(self, lattice: Any) -> None:
        self.lattice = lattice
        self._records: list = []
        self._index: dict = {}

    def record(self, signal: Any, label: str | None = None) -> dict:
        if signal is None or (isinstance(signal, str) and not signal.strip()):
            return {"recorded": False, "reason": "empty signal — IV·SIL"}
        h = hashlib.sha256(json.dumps(signal, default=str).encode()).hexdigest()[:12]
        entry = {"index": len(self._records),
                 "label": label or f"echo_{len(self._records):04d}",
                 "signal": signal, "hash": h, "ts": time.time()}
        self._index[entry["label"]] = entry["index"]
        self._records.append(entry)
        return {"recorded": True, "label": entry["label"], "hash": h}

    def trace(self, key: str) -> dict:               # ADD: was missing entirely
        if key in self._index:
            return {"found": True, **self._records[self._index[key]]}
        try:
            idx = int(key)
            if 0 <= idx < len(self._records):
                return {"found": True, **self._records[idx]}
        except (ValueError, TypeError):
            pass
        return {"found": False, "key": key, "total_records": len(self._records)}

    def history(self) -> list:
        return list(self._records)

    def status(self) -> dict:
        return {"record_count": len(self._records)}
