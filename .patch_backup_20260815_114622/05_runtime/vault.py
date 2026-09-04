"""
vault.py — Persistent Memory Layer (Rank 3)
PATCH v1.1:
  FIX: __init__(self) had NO lattice param → TypeError when lattice_core
       called Vault(self). Now __init__(self, lattice).
  ADD: retrieve(key) — was MISSING; <Vault:Retrieve> had no implementation.
"""
from __future__ import annotations
import hashlib, json, time
from typing import Any

class Vault:
    def __init__(self, lattice: Any) -> None:        # FIX: was __init__(self)
        self.lattice = lattice
        self._store: dict = {}
        self._export_log: list = []

    def store(self, key: str, value: Any) -> dict:
        if key in self._store:
            key = f"{key}__v{int(time.time())}"
        h = hashlib.sha256(json.dumps(value, default=str).encode()).hexdigest()[:12]
        self._store[key] = {"value": value, "ts": time.time(), "hash": h}
        return {"stored": key, "hash": h}

    def retrieve(self, key: str) -> dict:            # ADD: was missing entirely
        if key in self._store:
            e = self._store[key]
            return {"key": key, "value": e["value"], "ts": e["ts"], "hash": e["hash"], "found": True}
        return {"key": key, "found": False, "value": None}

    def export(self) -> dict:
        snap = {"export_ts": time.time(), "entry_count": len(self._store),
                "entries": {k: {"value": v["value"], "hash": v["hash"], "ts": v["ts"]}
                            for k, v in self._store.items()}}
        self._export_log.append({"export_ts": snap["export_ts"]})
        return snap

    def list_keys(self) -> list:
        return list(self._store.keys())

    def status(self) -> dict:
        return {"entry_count": len(self._store), "export_count": len(self._export_log)}
