# lineage_engine.py
# Activated: 2026-08-10 — Lineage Engine operational under contract.lineage_engine v1.0.0
# Operator: SIG: JRM-01 @liminaljermo
# Reversibility: R4 (rollback window until audit seal)

import os
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(os.path.dirname(os.path.abspath(__file__)))
LINEAGE_DIR = BASE / "lineage"
# Canonical Vault lineage index (mirror)
VAULT_LINEAGE_INDEX = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) / "vault" / "05_lineage" / "lineage_index.json"

# Operator signature (canonical)
OPERATOR_SIGNATURE = "SIG: JRM-01 @liminaljermo"
ENGINE_ID = "lineage_engine_v1"


def _ensure_dirs():
    """Ensure lineage storage directories exist."""
    LINEAGE_DIR.mkdir(parents=True, exist_ok=True)
    VAULT_LINEAGE_INDEX.parent.mkdir(parents=True, exist_ok=True)


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def record_lineage(name, action, context=None, source_ids=None, record_type="artifact"):
    """
    Writes a lineage entry for an artifact and updates the global index.
    Each entry includes:
    - timestamp (UTC ISO)
    - action performed
    - operator signature
    - optional context
    - optional source_ids for edge construction
    """
    _ensure_dirs()

    timestamp = _utc_now()
    entry = f"{timestamp} — {action} — {OPERATOR_SIGNATURE}"
    if context:
        entry += f" — {context}"

    path = LINEAGE_DIR / f"{name}.lineage"
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

    # Update global index with structured edge
    edge = {
        "record_type": record_type,
        "target_id": name,
        "source_ids": source_ids or [],
        "timestamp": timestamp,
        "action": action,
        "operator": OPERATOR_SIGNATURE,
        "engine_id": ENGINE_ID
    }
    _append_to_index(edge)

    return entry


def get_lineage(name):
    """
    Returns the lineage chain for an artifact as a list of entries.
    """
    path = LINEAGE_DIR / f"{name}.lineage"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def _append_to_index(edge):
    """Append an edge to the canonical lineage_index.json."""
    _ensure_dirs()
    if VAULT_LINEAGE_INDEX.exists():
        with open(VAULT_LINEAGE_INDEX, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "id": "vault_lineage_index",
            "version": "1.0.0",
            "description": "Canonical lineage index for the Vault subsystem.",
            "edges": [],
            "meta": {}
        }

    data["edges"].append(edge)
    data["meta"]["last_updated"] = _utc_now()
    data["meta"]["edge_count"] = len(data["edges"])
    data["meta"]["status"] = "ACTIVE"

    with open(VAULT_LINEAGE_INDEX, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def activate():
    """
    Explicit activation of the Lineage Engine.
    Creates directories, writes genesis edge, marks index ACTIVE.
    Returns activation record.
    """
    _ensure_dirs()

    genesis_edge = {
        "record_type": "system",
        "target_id": "lineage_engine_genesis",
        "source_ids": ["constitution_v1.1", "contract.lineage_engine"],
        "timestamp": _utc_now(),
        "action": "ACTIVATE",
        "operator": OPERATOR_SIGNATURE,
        "engine_id": ENGINE_ID,
        "context": "Lineage Engine activated per INDEX.md next-step option. R4 reversible until audit seal."
    }

    # Seed local lineage file
    record_lineage(
        name="lineage_engine_genesis",
        action="ACTIVATE",
        context="Lineage Engine activated. Contract: contract.lineage_engine v1.0.0. Anchors: engine_id, anchor_id.",
        source_ids=["constitution_v1.1", "contract.lineage_engine"],
        record_type="system"
    )

    # Ensure index meta is fully set
    if VAULT_LINEAGE_INDEX.exists():
        with open(VAULT_LINEAGE_INDEX, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"edges": [], "meta": {}}

    data["id"] = "vault_lineage_index"
    data["version"] = "1.1.0"
    data["description"] = "Canonical lineage index for the Vault subsystem. Stores all lineage edges created by Vault commits. Activated."
    data["meta"] = {
        "created": data.get("meta", {}).get("created", _utc_now()),
        "last_updated": _utc_now(),
        "edge_count": len(data.get("edges", [])),
        "status": "ACTIVE",
        "activated_by": OPERATOR_SIGNATURE,
        "activation_timestamp": _utc_now(),
        "engine_id": ENGINE_ID,
        "schema": {
            "record_type": "string",
            "target_id": "string",
            "source_ids": "array<string>",
            "timestamp": "string",
            "action": "string",
            "operator": "string",
            "engine_id": "string"
        }
    }

    with open(VAULT_LINEAGE_INDEX, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return {
        "status": "ACTIVE",
        "engine_id": ENGINE_ID,
        "operator": OPERATOR_SIGNATURE,
        "timestamp": _utc_now(),
        "message": "Lineage Engine activated. Genesis edge recorded. Index status=ACTIVE."
    }


def status():
    """Return current activation and index status."""
    _ensure_dirs()
    if not VAULT_LINEAGE_INDEX.exists():
        return {"status": "INACTIVE", "edge_count": 0}

    with open(VAULT_LINEAGE_INDEX, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "status": data.get("meta", {}).get("status", "UNKNOWN"),
        "edge_count": data.get("meta", {}).get("edge_count", len(data.get("edges", []))),
        "last_updated": data.get("meta", {}).get("last_updated"),
        "engine_id": data.get("meta", {}).get("engine_id", ENGINE_ID),
        "activated_by": data.get("meta", {}).get("activated_by")
    }


if __name__ == "__main__":
    result = activate()
    print(json.dumps(result, indent=2))
    print("Current status:", status())
