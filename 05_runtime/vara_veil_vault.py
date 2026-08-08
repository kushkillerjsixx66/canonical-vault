"""
VARA Veil + Vault — Mediation and Persistence Layer
Operator: JRM-01 @liminaljermo
Spec ref: Lattice Unified Spec §4, §8; Constitution Article VI

Signal routing:
  passed_signals   → Vault.commit() → Stumpy audit
  deferred_signals → Veil.hold()    → re-gate next cycle → Vault.commit()

Veil invariant (§4): prevents runaway recursion; softens divergence.
Vault invariant (Article VI): commit → review → canon lifecycle.
  No artifact may bypass the Vault.
  No canonized artifact may be deleted.

Reversibility First: deferred signals earn passage through recurrence,
not declaration. A signal recurring across 2+ consecutive scans passes Veil.
"""

import json
import os
import datetime
import hashlib
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional

# ─── PATHS ───────────────────────────────────────────────────────────────────

VEIL_HOLD_PATH   = "veil_hold.json"       # deferred signals held between cycles
VAULT_PATH       = "vault_signals.json"   # committed signal store
VAULT_CANON_PATH = "vault_canon.json"     # canonized (immutable) signal store

# ─── RECURRENCE THRESHOLD ────────────────────────────────────────────────────
# A deferred signal must appear in N consecutive scans to earn Vault passage.

VEIL_RECURRENCE_THRESHOLD = 2

# ─── DATA STRUCTURES ─────────────────────────────────────────────────────────

@dataclass
class VeilEntry:
    source_id:        str
    signal:           dict
    first_seen_scan:  str
    last_seen_scan:   str
    recurrence_count: int  = 1
    status:           str  = "HELD"   # HELD | PROMOTED | EXPIRED


@dataclass
class VaultEntry:
    vault_id:     str
    source_id:    str
    scan_id:      str
    committed_at: str
    signal:       dict
    origin:       str                    # "passed" | "veil_promoted"
    canonized:    bool           = False
    canonized_at: Optional[str]  = None


@dataclass
class VeilReport:
    veil_id:          str
    scan_id:          str
    timestamp:        str
    held_incoming:    int
    promoted:         int
    held_over:        int
    expired:          int
    promoted_signals: list
    held_entries:     list


@dataclass
class VaultReport:
    vault_id:        str
    scan_id:         str
    timestamp:       str
    committed:       int
    total_vault_size: int
    new_entries:     list


# ─── VEIL ────────────────────────────────────────────────────────────────────

def load_veil_hold() -> dict:
    """Load held signals from prior cycles."""
    if not os.path.exists(VEIL_HOLD_PATH):
        return {}
    try:
        with open(VEIL_HOLD_PATH, "r") as f:
            raw = json.load(f)
        return {k: VeilEntry(**v) for k, v in raw.items()}
    except (json.JSONDecodeError, TypeError, KeyError):
        return {}


def save_veil_hold(hold: dict) -> None:
    """Persist the current veil hold to disk."""
    serializable = {k: asdict(v) for k, v in hold.items()}
    with open(VEIL_HOLD_PATH, "w") as f:
        json.dump(serializable, f, indent=2)


def run_veil(deferred_signals: list, scan_id: str) -> VeilReport:
    """
    Process deferred signals through the Veil.

    - Signals seen before (recurrence_count >= VEIL_RECURRENCE_THRESHOLD)
      are PROMOTED to Vault.
    - New signals are HELD for next cycle.
    - Signals not seen in this scan are marked EXPIRED if last_seen older
      than 3 cycles (approximated by a TTL approach using recurrence_count).

    Returns VeilReport with promoted_signals ready for Vault commit.
    """
    hold     = load_veil_hold()
    timestamp = datetime.datetime.utcnow().isoformat()
    promoted  = []
    expired   = 0

    # Mark unseen entries for expiry (decrement would require cycle tracking;
    # we use a simpler approach: expire if not updated in this cycle and
    # recurrence_count < threshold).
    current_ids = {s.get("source_id", "") for s in deferred_signals}
    for sid, entry in list(hold.items()):
        if sid not in current_ids and entry.status == "HELD":
            if entry.recurrence_count < VEIL_RECURRENCE_THRESHOLD:
                entry.status = "EXPIRED"
                expired += 1

    # Process incoming deferred signals
    for sig in deferred_signals:
        sid = sig.get("source_id", sig.get("url", str(hash(str(sig)))))

        if sid in hold:
            entry = hold[sid]
            entry.recurrence_count += 1
            entry.last_seen_scan    = scan_id
            entry.signal            = sig   # refresh with latest version

            if entry.recurrence_count >= VEIL_RECURRENCE_THRESHOLD:
                entry.status = "PROMOTED"
                promoted.append(sig)
        else:
            hold[sid] = VeilEntry(
                source_id=sid,
                signal=sig,
                first_seen_scan=scan_id,
                last_seen_scan=scan_id,
                recurrence_count=1,
                status="HELD",
            )

    # Prune expired entries from hold
    hold = {k: v for k, v in hold.items() if v.status != "EXPIRED"}
    save_veil_hold(hold)

    held_over = sum(1 for v in hold.values() if v.status == "HELD")

    return VeilReport(
        veil_id=str(uuid.uuid4()),
        scan_id=scan_id,
        timestamp=timestamp,
        held_incoming=len(deferred_signals),
        promoted=len(promoted),
        held_over=held_over,
        expired=expired,
        promoted_signals=promoted,
        held_entries=[asdict(v) for v in hold.values() if v.status == "HELD"],
    )


# ─── VAULT ───────────────────────────────────────────────────────────────────

def load_vault() -> list:
    """Load existing vault entries."""
    if not os.path.exists(VAULT_PATH):
        return []
    try:
        with open(VAULT_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def save_vault(entries: list) -> None:
    with open(VAULT_PATH, "w") as f:
        json.dump(entries, f, indent=2)


def commit_to_vault(
    signals: list,
    scan_id: str,
    origin:  str = "passed",   # "passed" | "veil_promoted"
) -> VaultReport:
    """
    Commit signals to the Vault store.
    Each entry gets a vault_id (SHA-256 of source_id + scan_id).
    Returns VaultReport with committed count.
    """
    vault     = load_vault()
    timestamp = datetime.datetime.utcnow().isoformat()
    new_entries = []

    existing_ids = {e.get("source_id") for e in vault}

    for sig in signals:
        sid = sig.get("source_id", str(uuid.uuid4()))
        if sid in existing_ids:
            # Signal already committed (idempotent vault per Article VI)
            continue

        vault_id = hashlib.sha256(
            f"{sid}:{scan_id}:{timestamp}".encode()
        ).hexdigest()[:24]

        entry = VaultEntry(
            vault_id=vault_id,
            source_id=sid,
            scan_id=scan_id,
            committed_at=timestamp,
            signal=sig,
            origin=origin,
        )
        vault.append(asdict(entry))
        new_entries.append(asdict(entry))

    save_vault(vault)

    return VaultReport(
        vault_id=str(uuid.uuid4()),
        scan_id=scan_id,
        timestamp=timestamp,
        committed=len(new_entries),
        total_vault_size=len(vault),
        new_entries=new_entries,
    )


# ─── MAIN ROUTER ─────────────────────────────────────────────────────────────

def route_signals(
    passed_signals:   list,
    deferred_signals: list,
    scan_id:          str,
) -> tuple:
    """
    Primary routing function called by vara_scan.py after sentinel.

    passed_signals   → Vault.commit() immediately
    deferred_signals → Veil.hold() → promote if recurrence met → Vault.commit()

    Returns (VaultReport, VeilReport) tuple.
    """
    # Commit passed signals directly
    vault_report = commit_to_vault(passed_signals, scan_id, origin="passed")

    # Run veil on deferred; commit any promotions
    veil_report = run_veil(deferred_signals, scan_id)

    if veil_report.promoted_signals:
        promo_vault = commit_to_vault(
            veil_report.promoted_signals,
            scan_id,
            origin="veil_promoted",
        )
        # Merge promoted into vault report counts
        vault_report.committed        += promo_vault.committed
        vault_report.total_vault_size  = promo_vault.total_vault_size
        vault_report.new_entries.extend(promo_vault.new_entries)

    return vault_report, veil_report


# ─── CANONIZATION ────────────────────────────────────────────────────────────

def canonize_vault_entry(vault_id: str) -> bool:
    """
    Mark a vault entry as canonized (immutable per Article VI).
    Returns True if the entry was found and updated.
    """
    vault = load_vault()
    timestamp = datetime.datetime.utcnow().isoformat()
    updated = False

    for entry in vault:
        if entry.get("vault_id") == vault_id:
            if entry.get("canonized"):
                return True   # idempotent
            entry["canonized"]    = True
            entry["canonized_at"] = timestamp
            updated = True
            break

    if updated:
        save_vault(vault)
        # Append to immutable canon store
        canon = []
        if os.path.exists(VAULT_CANON_PATH):
            try:
                with open(VAULT_CANON_PATH, "r") as f:
                    canon = json.load(f)
            except (json.JSONDecodeError, ValueError):
                canon = []
        canon.append(next(e for e in vault if e["vault_id"] == vault_id))
        with open(VAULT_CANON_PATH, "w") as f:
            json.dump(canon, f, indent=2)

    return updated
