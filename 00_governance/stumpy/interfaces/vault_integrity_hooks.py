"""
vault_integrity_hooks.py
Stumpy Governance Engine — Vault integrity verification hooks.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from single emit_vault_event() stub — added
             VaultIntegrityCheck dataclass, hash-based signature verification,
             and hook callbacks for pre/post-write vault checks.
"""

from __future__ import annotations
import datetime
import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .vara_bridge import emit_epistemic_event


# ── Vault check schema ───────────────────────────────────────────────────── #

@dataclass
class VaultIntegrityCheck:
    """
    Result of a vault integrity verification pass on a single vault record.
    """
    check_id:    str            = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:   str            = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat()
    )
    vault_key:   str            = ""
    expected_sig: str           = ""
    actual_sig:  str            = ""
    passed:      bool           = False
    reason:      str            = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id":     self.check_id,
            "timestamp":    self.timestamp,
            "vault_key":    self.vault_key,
            "expected_sig": self.expected_sig,
            "actual_sig":   self.actual_sig,
            "passed":       self.passed,
            "reason":       self.reason,
        }


# ── Hook registry ─────────────────────────────────────────────────────────── #

_PRE_WRITE_HOOKS:  List[Callable[[str, Dict[str, Any]], None]] = []
_POST_WRITE_HOOKS: List[Callable[[VaultIntegrityCheck], None]] = []


def register_pre_write_hook(fn: Callable[[str, Dict[str, Any]], None]) -> None:
    """Register a callback invoked *before* a vault write with (key, payload)."""
    _PRE_WRITE_HOOKS.append(fn)


def register_post_write_hook(fn: Callable[[VaultIntegrityCheck], None]) -> None:
    """Register a callback invoked *after* a vault write with the check result."""
    _POST_WRITE_HOOKS.append(fn)


# ── Core helpers ─────────────────────────────────────────────────────────── #

def _compute_sig(payload: Dict[str, Any]) -> str:
    """SHA-256 signature of a JSON-serializable payload dict."""
    import json
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_vault_entry(
    vault_key: str,
    payload: Dict[str, Any],
    expected_sig: Optional[str] = None,
) -> VaultIntegrityCheck:
    """
    Verify the integrity of a vault entry.

    If expected_sig is None, computes the sig from payload and marks passed=True
    (first-write trust). If expected_sig is provided, compares against computed.
    """
    actual = _compute_sig(payload)
    if expected_sig is None:
        result = VaultIntegrityCheck(
            vault_key=vault_key,
            expected_sig=actual,
            actual_sig=actual,
            passed=True,
            reason="first-write trust — sig recorded",
        )
    else:
        passed = actual == expected_sig
        result = VaultIntegrityCheck(
            vault_key=vault_key,
            expected_sig=expected_sig,
            actual_sig=actual,
            passed=passed,
            reason="ok" if passed else "signature mismatch — possible tampering",
        )
    return result


# ── Public API ────────────────────────────────────────────────────────────── #

def emit_vault_event(
    vault_key: str,
    payload: Optional[Dict[str, Any]] = None,
    expected_sig: Optional[str] = None,
) -> VaultIntegrityCheck:
    """
    Run vault integrity hooks and emit the result to the epistemic bus.

    Preserved original function signature; now wraps into VaultIntegrityCheck,
    runs pre/post hooks, and cross-notifies Vara.
    """
    payload = payload or {}

    for hook in _PRE_WRITE_HOOKS:
        try:
            hook(vault_key, payload)
        except Exception:
            pass

    check = verify_vault_entry(vault_key, payload, expected_sig)

    emit_epistemic_event(
        event_type="vault_integrity_check",
        payload=check.to_dict(),
    )

    for hook in _POST_WRITE_HOOKS:
        try:
            hook(check)
        except Exception:
            pass

    return check
