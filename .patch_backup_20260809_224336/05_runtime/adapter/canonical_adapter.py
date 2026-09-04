"""
canonical_adapter.py — Bridge between external I/O and the Lattice runtime
PATCH v1.1: CREATED — this file was MISSING from the repo entirely.
run_lattice.py imported it as 'runtime.adapter.canonical_adapter' which
failed with ModuleNotFoundError on every execution.
"""
from __future__ import annotations
import time
from typing import Any

class CanonicalAdapter:
    ADAPTER_VERSION = "1.1.0"
    def __init__(self, lattice: Any) -> None:
        self.lattice = lattice
        self._ingest_count = 0; self._emit_count = 0
        self._error_count  = 0; self._started_at = time.time()

    def ingest(self, raw: Any) -> dict:
        self._ingest_count += 1
        if raw is None:       return {"content": None, "source": "adapter", "type": "null", "ts": time.time()}
        if isinstance(raw, bytes):
            try:              raw = raw.decode("utf-8")
            except UnicodeDecodeError:
                self._error_count += 1
                return {"content": None, "source": "adapter", "type": "binary_error", "ts": time.time()}
        if isinstance(raw, str):  return {"content": raw.strip(), "source": "adapter", "type": "text", "ts": time.time()}
        if isinstance(raw, dict): raw.setdefault("source","adapter"); raw.setdefault("ts",time.time()); return raw
        return {"content": str(raw), "source": "adapter", "type": "coerced", "ts": time.time()}

    def emit(self, cycle_result: dict) -> dict:
        self._emit_count += 1
        if not isinstance(cycle_result, dict): return {"result": str(cycle_result), "ts": time.time()}
        return {"result": cycle_result.get("result"), "coherence_score": cycle_result.get("coherence_score"),
                "blocked_at": cycle_result.get("blocked_at"), "cycle": cycle_result.get("cycle"),
                "ts": time.time(), "adapter_version": self.ADAPTER_VERSION}

    def process(self, raw: Any) -> dict:
        return self.emit(self.lattice.run(self.ingest(raw).get("content","")))

    def health(self) -> dict:
        return {"status": "ok", "adapter_version": self.ADAPTER_VERSION,
                "uptime_seconds": round(time.time()-self._started_at,1),
                "ingest_count": self._ingest_count, "emit_count": self._emit_count}
