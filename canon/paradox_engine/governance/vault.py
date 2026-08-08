"""
PARADOX_ENGINE_1.0 — Vault Cluster
Canon Layer: GOVERNANCE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE

VaultCluster is the archival authority for completed and decayed
simulations. It stores immutable VaultRecord objects keyed by a
deterministic vault key and supports:
  - archive()   : Write a simulation record to the vault
  - retrieve()  : Read a VaultRecord by key
  - replay()    : Return a read-only copy of the resolved tree summary
  - purge()     : Permanently delete a record (irreversible)
  - list_keys() : Enumerate all stored keys
  - ttl_sweep() : Expire records beyond retention_days threshold

The vault is in-memory by default. Pass a persist_path to enable
JSON-line persistence to a local file.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from paradox_engine.config import EngineConfig, DEFAULT_CONFIG

if TYPE_CHECKING:
    from paradox_engine.core.simulation import ParadoxSimulation
    from paradox_engine.governance.audit import AuditCluster


# ── Vault Record ──────────────────────────────────────────────────────────────

@dataclass
class VaultRecord:
    """
    An immutable snapshot of a simulation at the time of archival.

    Attributes
    ----------
    vault_key       : Unique storage key (deterministic from sim ID).
    simulation_id   : Source simulation UUID.
    paradox_label   : Human-readable paradox name.
    archived_at     : Unix timestamp of archival.
    retention_until : Unix timestamp after which this record may be expired.
    record          : Full simulation record dict (from sim.to_record()).
    replay_allowed  : Whether this record can be used for replay.
    """
    vault_key:       str
    simulation_id:   str
    paradox_label:   str
    archived_at:     float
    retention_until: float
    record:          dict
    replay_allowed:  bool = True
    _purged:         bool = field(default=False, init=False, repr=False)

    @property
    def is_expired(self) -> bool:
        return time.time() > self.retention_until

    @property
    def is_purged(self) -> bool:
        return self._purged

    def to_dict(self) -> dict:
        return {
            "vault_key":       self.vault_key,
            "simulation_id":   self.simulation_id,
            "paradox_label":   self.paradox_label,
            "archived_at":     self.archived_at,
            "retention_until": self.retention_until,
            "replay_allowed":  self.replay_allowed,
            "record":          self.record,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    def __repr__(self) -> str:
        expired = " EXPIRED" if self.is_expired else ""
        purged  = " PURGED"  if self._purged   else ""
        return (
            f"VaultRecord(key={self.vault_key[:16]}, "
            f"sim={self.simulation_id[:8]}, "
            f"label={self.paradox_label!r}{expired}{purged})"
        )


def _make_vault_key(simulation_id: str) -> str:
    """Deterministic vault key: 'VAULT:' + first 40 hex chars of sim UUID."""
    return f"VAULT:{simulation_id.replace('-', '')[:40].upper()}"


# ── Vault Cluster ─────────────────────────────────────────────────────────────

class VaultCluster:
    """
    Archival store for resolved ParadoxSimulations.

    Parameters
    ----------
    config       : EngineConfig
    audit        : AuditCluster — receives vault read/write events.
    persist_path : Optional filesystem path for JSONL persistence.
                   If provided, new records are appended on archive.
    """

    def __init__(
        self,
        config:       EngineConfig            = DEFAULT_CONFIG,
        audit:        Optional["AuditCluster"] = None,
        persist_path: Optional[str | Path]     = None,
    ) -> None:
        self._config       = config
        self._audit        = audit
        self._store:       Dict[str, VaultRecord] = {}
        self._persist_path = Path(persist_path) if persist_path else None

        if self._persist_path and self._persist_path.exists():
            self._load_from_disk()

    # ── Archive ────────────────────────────────────────────────────────────────

    def archive(self, sim: "ParadoxSimulation") -> str:
        """
        Write *sim* to the vault.

        Returns
        -------
        vault_key : str — the key under which the record is stored.
        """
        key = _make_vault_key(sim.simulation_id)
        retention_seconds = self._config.decay.vault_retention_days * 86_400
        now = time.time()

        record = VaultRecord(
            vault_key       = key,
            simulation_id   = sim.simulation_id,
            paradox_label   = sim.paradox.label,
            archived_at     = now,
            retention_until = now + retention_seconds,
            record          = sim.to_record(),
            replay_allowed  = self._config.decay.allow_replay,
        )
        self._store[key] = record

        if self._persist_path:
            self._append_to_disk(record)

        if self._audit:
            self._audit.log_vault_write(key, sim.simulation_id)

        return key

    # ── Retrieve ───────────────────────────────────────────────────────────────

    def retrieve(self, vault_key: str) -> Optional[VaultRecord]:
        """
        Retrieve a VaultRecord by *vault_key*.
        Returns None if the key is unknown or has been purged.
        """
        record = self._store.get(vault_key)
        if record is None or record.is_purged:
            return None

        if self._audit:
            self._audit.log_vault_read(vault_key)

        return record

    def retrieve_by_sim_id(self, simulation_id: str) -> Optional[VaultRecord]:
        """Retrieve a VaultRecord by source simulation ID."""
        key = _make_vault_key(simulation_id)
        return self.retrieve(key)

    # ── Replay ────────────────────────────────────────────────────────────────

    def replay(self, vault_key: str) -> Optional[dict]:
        """
        Return a read-only replay summary dict from a vaulted record.
        Returns None if the record is not replayable (purged, or
        replay_allowed=False).
        """
        rec = self.retrieve(vault_key)
        if rec is None:
            return None
        if not rec.replay_allowed:
            return None
        # Shallow copy prevents mutation of the stored record
        return dict(rec.record)

    # ── Purge ─────────────────────────────────────────────────────────────────

    def purge(self, vault_key: str) -> bool:
        """
        Permanently mark a record as purged. Data is zeroed in place.
        Returns True if the record existed and was purged; False otherwise.

        This is a soft-purge: the key remains in the store for audit
        traceability, but all payload data is cleared.
        """
        rec = self._store.get(vault_key)
        if rec is None:
            return False
        rec._purged = True
        rec.record  = {}  # Clear payload
        return True

    # ── TTL Sweep ─────────────────────────────────────────────────────────────

    def ttl_sweep(self) -> List[str]:
        """
        Expire records whose retention window has passed.
        Calls purge() on each expired key.
        Returns the list of keys purged.
        """
        expired = [
            key for key, rec in self._store.items()
            if rec.is_expired and not rec.is_purged
        ]
        for key in expired:
            self.purge(key)
        return expired

    # ── Query ─────────────────────────────────────────────────────────────────

    def count(self) -> int:
        return sum(1 for r in self._store.values() if not r.is_purged)

    def list_keys(self, include_purged: bool = False) -> List[str]:
        return [
            k for k, r in self._store.items()
            if include_purged or not r.is_purged
        ]

    def list_records(self, include_purged: bool = False) -> List[VaultRecord]:
        return [
            r for r in self._store.values()
            if include_purged or not r.is_purged
        ]

    def summary(self) -> dict:
        records  = list(self._store.values())
        live     = [r for r in records if not r.is_purged]
        expired  = [r for r in live if r.is_expired]
        return {
            "total_records":   len(records),
            "live_records":    len(live),
            "expired_records": len(expired),
            "purged_records":  len(records) - len(live),
            "persist_path":    str(self._persist_path) if self._persist_path else None,
        }

    # ── Persistence ───────────────────────────────────────────────────────────

    def _append_to_disk(self, record: VaultRecord) -> None:
        """Append a single record as a JSON line to the persist file."""
        assert self._persist_path is not None
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._persist_path, "a", encoding="utf-8") as fh:
            fh.write(record.to_json() + "\n")

    def _load_from_disk(self) -> None:
        """Load records from an existing JSONL persist file."""
        assert self._persist_path is not None
        with open(self._persist_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    rec  = VaultRecord(
                        vault_key       = data["vault_key"],
                        simulation_id   = data["simulation_id"],
                        paradox_label   = data["paradox_label"],
                        archived_at     = data["archived_at"],
                        retention_until = data["retention_until"],
                        record          = data.get("record", {}),
                        replay_allowed  = data.get("replay_allowed", True),
                    )
                    self._store[rec.vault_key] = rec
                except (KeyError, json.JSONDecodeError):
                    continue  # Skip malformed lines

    def export_jsonl(self) -> str:
        """Export all live records as newline-delimited JSON."""
        return "\n".join(
            r.to_json() for r in self._store.values() if not r.is_purged
        )

    def __repr__(self) -> str:
        return (
            f"VaultCluster(live={self.count()}, "
            f"total={len(self._store)}, "
            f"persist={self._persist_path is not None})"
        )
