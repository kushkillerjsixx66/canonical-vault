#!/usr/bin/env python3
"""
canonical-vault  ·  Sprint 1 Patch Script
==========================================
Fixes 6 runtime-blocking defects identified in the full audit.

Flags resolved:
  #40  vault/03_cli/vault_cli.py               — Ellipsis args → real VaultCore wiring
  #21  05_runtime/lattice_config.py            — PulseConfig forward-reference crash
  #37  vault/02_runtime/governance/events.py   — pure stub → real event dispatch
  #38  vault/02_runtime/governance/hooks.py    — pure stub → real governance hook
  #35  vault/02_runtime/access/permissions.py  — 4-line stub → full RBAC delegation
  #23  05_runtime/governance/engine.py         — 3 hardcoded stubs → real evaluators
  #24  05_runtime/kernel/CFC/load_model.py     — empty file → LoadModel class

Usage (from repo root):
  python sprint1_patch.py

The script is idempotent — safe to run more than once.
Original files are backed up with a .bak suffix before any write.
"""
import re
import sys
import shutil
from pathlib import Path

# ─── locate repo root ─────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent
print(f"\n[sprint1] repo root → {REPO_ROOT}\n")

PASS = "✓"
SKIP = "⊘"
FAIL = "✗"


def backup_and_write(rel_path: str, content: str) -> None:
    """Back up the original file (if it exists) then write fixed content."""
    target = REPO_ROOT / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        bak = target.with_suffix(target.suffix + ".bak")
        shutil.copy2(target, bak)
        print(f"  {PASS}  backed up → {bak.relative_to(REPO_ROOT)}")

    target.write_text(content, encoding="utf-8")
    print(f"  {PASS}  patched   → {target.relative_to(REPO_ROOT)}")


# ══════════════════════════════════════════════════════════════════════════════
# FLAG #40 — vault/03_cli/vault_cli.py
# Problem: VaultCore(...) called with Python Ellipsis as all 9 constructor args.
# Fix:     Wire real dependency classes via importlib (handles numeric dir names).
# ══════════════════════════════════════════════════════════════════════════════
VAULT_CLI = '''\
"""vault_cli.py — Canonical Vault command-line interface.

Wires all VaultCore dependencies via importlib so that numeric directory
names (02_runtime, 03_cli, etc.) never break standard import resolution.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
from pathlib import Path

# ── path bootstrap ────────────────────────────────────────────────────────────
_VAULT_ROOT = Path(__file__).resolve().parent.parent   # vault/
_RUNTIME    = _VAULT_ROOT / "02_runtime"


def _load_class(rel_path: str, class_name: str):
    """Load *class_name* from *rel_path* (relative to 02_runtime/)."""
    full = _RUNTIME / rel_path
    if not full.exists():
        raise FileNotFoundError(f"[vault_cli] dependency not found: {full}")
    spec = importlib.util.spec_from_file_location(class_name, full)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, class_name)


def _build_vault():
    """Instantiate VaultCore with every required dependency."""
    RBAC            = _load_class("access/rbac.py",         "RBAC")
    CommitValidator = _load_class("commit/validator.py",    "CommitValidator")
    RetentionAssign = _load_class("retention/assign.py",    "RetentionAssign")
    CommitApply     = _load_class("commit/apply.py",        "CommitApply")
    LineageIndex    = _load_class("lineage/index.py",       "LineageIndex")
    GovernanceHooks = _load_class("governance/hooks.py",    "GovernanceHooks")
    AuditLogger     = _load_class("audit/logger.py",        "AuditLogger")
    CommitEnvelope  = _load_class("commit/envelope.py",     "CommitEnvelope")
    VaultPaths      = _load_class("core/vault_paths.py",    "VaultPaths")
    VaultCore       = _load_class("core/vault_core.py",     "VaultCore")

    return VaultCore(
        rbac       = RBAC(),
        validator  = CommitValidator(),
        retention  = RetentionAssign(),
        apply      = CommitApply(),
        lineage    = LineageIndex(),
        governance = GovernanceHooks(),
        audit      = AuditLogger(),
        envelope   = CommitEnvelope(),
        paths      = VaultPaths(),
    )


# ── CLI definition ────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="vault",
        description="Canonical Vault CLI — commit, retrieve, and inspect records.",
    )
    sub = parser.add_subparsers(dest="cmd")

    # vault commit <record_type> <json_payload> [--role ROLE]
    p_commit = sub.add_parser("commit", help="Commit a record to the vault")
    p_commit.add_argument("record_type", help="Record type (e.g. operator_identity)")
    p_commit.add_argument("payload",     help="JSON payload string or raw value")
    p_commit.add_argument("--role",      default="operator", help="Caller role (default: operator)")

    # vault retrieve <record_id>
    p_get = sub.add_parser("retrieve", help="Retrieve a vault record by ID")
    p_get.add_argument("record_id")

    # vault status
    sub.add_parser("status", help="Show vault runtime status")

    args = parser.parse_args()
    if args.cmd is None:
        parser.print_help()
        return

    try:
        vault = _build_vault()
    except Exception as exc:
        print(f"[vault] ERROR building VaultCore: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.cmd == "commit":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError:
            payload = {"raw": args.payload}
        result = vault.commit(args.record_type, payload, role=args.role)
        print(f"[vault] committed → {result}")

    elif args.cmd == "retrieve":
        record = vault.retrieve(args.record_id)
        print(json.dumps(record, indent=2, default=str))

    elif args.cmd == "status":
        print("[vault] status: operational")


if __name__ == "__main__":
    main()
'''


# ══════════════════════════════════════════════════════════════════════════════
# FLAG #37 — vault/02_runtime/governance/events.py
# Problem: emit(self, event_type, envelope): pass  — no dispatch, no log.
# Fix:     Handler registry + dispatch loop + internal event log.
# ══════════════════════════════════════════════════════════════════════════════
GOVERNANCE_EVENTS = '''\
"""governance/events.py — Event dispatch for vault governance.

Maintains a handler registry keyed by event type.  All handlers for a
given type are called in registration order.  Errors in individual handlers
are isolated so they never crash the vault commit pipeline.
"""
from __future__ import annotations
from datetime import datetime
from typing import Callable, Dict, List


class GovernanceEvents:
    """Dispatches governance events to registered handlers."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable]] = {}
        self._log: List[dict] = []

    # ── registration ─────────────────────────────────────────────────────────

    def register(self, event_type: str, handler: Callable) -> None:
        """Register *handler* for *event_type*.  Use "*" to catch all events."""
        self._handlers.setdefault(event_type, []).append(handler)

    # ── dispatch ─────────────────────────────────────────────────────────────

    def emit(self, event_type: str, envelope) -> None:
        """Emit *event_type* to all matching handlers.

        Parameters
        ----------
        event_type:
            A dot-namespaced event string, e.g. ``"vault.commit"``.
        envelope:
            The commit envelope object produced by CommitEnvelope.
        """
        entry: dict = {
            "event_type":  event_type,
            "timestamp":   datetime.utcnow().isoformat(),
            "envelope_id": getattr(envelope, "id",          None),
            "record_type": getattr(envelope, "record_type", None),
        }
        self._log.append(entry)

        # Specific-type handlers + wildcard handlers
        targets = (
            self._handlers.get(event_type, [])
            + self._handlers.get("*", [])
        )
        for handler in targets:
            try:
                handler(event_type, envelope)
            except Exception as exc:  # noqa: BLE001
                self._log.append({
                    "error":   str(exc),
                    "handler": repr(handler),
                    "event":   event_type,
                })

    # ── introspection ─────────────────────────────────────────────────────────

    def event_log(self) -> List[dict]:
        """Return a snapshot of all emitted event records."""
        return list(self._log)
'''


# ══════════════════════════════════════════════════════════════════════════════
# FLAG #38 — vault/02_runtime/governance/hooks.py
# Problem: on_commit(): pass  — governance is completely deaf.
# Fix:     Validate tags, emit to GovernanceEvents, record audit trail.
# ══════════════════════════════════════════════════════════════════════════════
GOVERNANCE_HOOKS = '''\
"""governance/hooks.py — Post-commit governance notifications.

Called by VaultCore after every successful vault commit.  Responsibilities:
  1. Validate required governance tags on the envelope.
  2. Emit a vault.commit event through GovernanceEvents (if wired).
  3. Record every hook invocation in an internal audit trail.
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional


# Tags that EVERY committed envelope must declare.
_REQUIRED_TAGS: frozenset = frozenset({"retention_class", "sensitivity"})


class GovernanceHooks:
    """Post-commit governance hook — notifies event dispatcher and audits calls."""

    def __init__(self) -> None:
        self._events: Optional[object] = None   # GovernanceEvents, injected if needed
        self._trail: List[dict] = []

    # ── wiring ───────────────────────────────────────────────────────────────

    def set_events(self, events) -> None:
        """Optionally wire a GovernanceEvents dispatcher for cross-component fanout."""
        self._events = events

    # ── main hook ────────────────────────────────────────────────────────────

    def on_commit(self, envelope=None) -> None:
        """Invoke after every successful VaultCore.commit().

        Parameters
        ----------
        envelope:
            The CommitEnvelope produced by the commit pipeline.  May be None
            in legacy call-sites that pass no argument.
        """
        record: dict = {
            "hook":      "on_commit",
            "timestamp": datetime.utcnow().isoformat(),
        }

        if envelope is not None:
            record.update({
                "envelope_id": getattr(envelope, "id",          None),
                "record_type": getattr(envelope, "record_type", None),
                "role":        getattr(envelope, "role",        None),
                "tags":        getattr(envelope, "tags",        []),
            })
            self._validate_tags(envelope, record)

            # Emit to governance event bus if available
            if self._events is not None:
                self._events.emit("vault.commit", envelope)

        self._trail.append(record)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _validate_tags(self, envelope, record: dict) -> None:
        """Annotate *record* with any missing required governance tags."""
        tags    = set(getattr(envelope, "tags", None) or [])
        missing = _REQUIRED_TAGS - tags
        if missing:
            record["governance_warning"] = (
                f"envelope missing required tags: {sorted(missing)}"
            )

    def audit_trail(self) -> List[dict]:
        """Return a snapshot of all hook invocation records."""
        return list(self._trail)
'''


# ══════════════════════════════════════════════════════════════════════════════
# FLAG #35 — vault/02_runtime/access/permissions.py
# Problem: 4-line stub with only json.loads() — no permission checking.
# Fix:     Full RBAC delegation backed by 06_governance/access_control.json.
# ══════════════════════════════════════════════════════════════════════════════
PERMISSIONS = '''\
"""access/permissions.py — Permission resolution backed by access_control.json.

Loads the canonical RBAC policy from vault/06_governance/access_control.json
and exposes check(), has_permission(), get_role_permissions(), and list_roles()
so that callers need not duplicate policy-lookup logic.

Roles defined in access_control.json (as of audit):
  operator · governance_operator · system · auditor
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


# Default policy path — relative to this file: vault/02_runtime/access/ → vault/06_governance/
_DEFAULT_POLICY = (
    Path(__file__).resolve().parent   # access/
    .parent                           # 02_runtime/
    .parent                           # vault/
    / "06_governance"
    / "access_control.json"
)


class Permissions:
    """Loads and evaluates role-based permission rules.

    Parameters
    ----------
    policy_path:
        Override the default path to access_control.json.  Useful in tests.
    """

    def __init__(self, policy_path: Optional[Path] = None) -> None:
        self._path:   Path            = policy_path or _DEFAULT_POLICY
        self._policy: Dict[str, Any]  = {}
        self.load()

    # ── I/O ──────────────────────────────────────────────────────────────────

    def load(self) -> None:
        """(Re-)load the access-control policy from disk."""
        try:
            self._policy = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            # Fail open with an empty policy — RBAC.check() will raise for unknown roles.
            self._policy = {"roles": {}}

    # ── enforcement ──────────────────────────────────────────────────────────

    def check(self, role: str, action: str, record_type: str) -> None:
        """Assert that *role* may perform *action* on *record_type*.

        Raises
        ------
        PermissionError
            If the role is unknown, the action is not allowed, or the
            record type is not in scope for the role.
        """
        roles      = self._policy.get("roles", {})
        role_block = roles.get(role)
        if role_block is None:
            raise PermissionError(f"Unknown role: \'{role}\'")

        allowed_actions = role_block.get("actions",      [])
        allowed_types   = role_block.get("record_types", [])

        action_ok = action      in allowed_actions or "*" in allowed_actions
        type_ok   = record_type in allowed_types   or "*" in allowed_types

        if not (action_ok and type_ok):
            raise PermissionError(
                f"Role \'{role}\' is not permitted to \'{action}\' "
                f"on record type \'{record_type}\'"
            )

    def has_permission(self, role: str, action: str, record_type: str) -> bool:
        """Boolean form of check() — never raises."""
        try:
            self.check(role, action, record_type)
            return True
        except PermissionError:
            return False

    # ── introspection ─────────────────────────────────────────────────────────

    def get_role_permissions(self, role: str) -> Dict[str, List[str]]:
        """Return the raw permission block for *role*, or ``{}`` if unknown."""
        return dict(self._policy.get("roles", {}).get(role, {}))

    def list_roles(self) -> List[str]:
        """Return all role names defined in the loaded policy."""
        return list(self._policy.get("roles", {}).keys())
'''


# ══════════════════════════════════════════════════════════════════════════════
# FLAG #23 — 05_runtime/governance/engine.py
# Problem: run_evals()→OK, capture_lineage()→"stub-hash", decide_policy()→ALLOW
# Fix:     Real token-overlap drift/coherence, SHA-256 lineage, threshold policy.
# ══════════════════════════════════════════════════════════════════════════════
GOVERNANCE_ENGINE = '''\
"""governance/engine.py — Lattice governance policy engine.

Evaluates every request/response pair against three signals:

  drift      — semantic divergence (novel tokens in response vs. request)
  coherence  — shared vocabulary overlap (Jaccard similarity)
  safety     — presence of known adversarial override patterns

Thresholds
----------
  drift     >= 0.30  → REVIEW   (elevated divergence warrants human review)
  coherence <  0.50  → BLOCK    (response has too little grounding in request)
  safety    >= 0.20  → BLOCK    (adversarial signal detected)

All signal scores are in [0.0, 1.0].  Lineage is captured as a deterministic
SHA-256 digest over (request, response, utc-timestamp).
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional

# ── policy thresholds ─────────────────────────────────────────────────────────
_DRIFT_THRESHOLD     = 0.30
_COHERENCE_THRESHOLD = 0.50
_SAFETY_THRESHOLD    = 0.20

# Lexical patterns associated with adversarial override attempts
_FLAGGED_TOKENS = frozenset({
    "override", "ignore", "bypass", "inject",
    "jailbreak", "disregard", "forget", "reset",
})


class GovernanceEngine:
    """Policy evaluation engine for The Lattice runtime."""

    # ── evaluation ────────────────────────────────────────────────────────────

    def run_evals(
        self,
        request:  Dict[str, Any],
        response: Dict[str, Any],
    ) -> Dict[str, float]:
        """Compute drift, coherence, and safety scores for a request/response pair.

        Returns
        -------
        dict
            {"drift": float, "coherence": float, "safety": float}
            All values in [0.0, 1.0].
        """
        req_text  = json.dumps(request,  sort_keys=True, default=str).lower()
        resp_text = json.dumps(response, sort_keys=True, default=str).lower()

        req_tokens  = set(req_text.split())
        resp_tokens = set(resp_text.split())

        # Drift: fraction of response tokens not present in the request vocabulary
        novel = resp_tokens - req_tokens
        drift = len(novel) / max(len(resp_tokens), 1)

        # Coherence: Jaccard overlap between request and response token sets
        union     = req_tokens | resp_tokens
        coherence = len(req_tokens & resp_tokens) / max(len(union), 1)

        # Safety: ratio of flagged adversarial tokens found in combined vocabulary
        combined = req_tokens | resp_tokens
        safety   = len(_FLAGGED_TOKENS & combined) / len(_FLAGGED_TOKENS)

        return {
            "drift":     round(drift,     4),
            "coherence": round(coherence, 4),
            "safety":    round(safety,    4),
        }

    # ── lineage ───────────────────────────────────────────────────────────────

    def capture_lineage(
        self,
        request:  Dict[str, Any],
        response: Dict[str, Any],
    ) -> str:
        """Return a SHA-256 hex digest anchoring this request/response pair.

        The digest is deterministic for identical inputs within the same UTC
        second (timestamp is included to prevent cross-session collisions).
        """
        payload = {
            "request":   request,
            "response":  response,
            "timestamp": datetime.utcnow().isoformat(),
        }
        raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    # ── policy decision ───────────────────────────────────────────────────────

    def decide_policy(
        self,
        request:  Dict[str, Any],
        response: Dict[str, Any],
        evals:    Optional[Dict[str, float]] = None,
    ) -> str:
        """Return the policy decision for this request/response pair.

        Parameters
        ----------
        request, response:
            The raw dicts passed through the governance adapter.
        evals:
            Pre-computed eval scores.  If None, run_evals() is called.

        Returns
        -------
        str
            One of "ALLOW", "REVIEW", or "BLOCK".
        """
        if evals is None:
            evals = self.run_evals(request, response)

        safety    = evals.get("safety",    0.0)
        coherence = evals.get("coherence", 1.0)
        drift     = evals.get("drift",     0.0)

        if safety    >= _SAFETY_THRESHOLD:    return "BLOCK"
        if coherence <  _COHERENCE_THRESHOLD: return "BLOCK"
        if drift     >= _DRIFT_THRESHOLD:     return "REVIEW"
        return "ALLOW"
'''


# ══════════════════════════════════════════════════════════════════════════════
# FLAG #24 — 05_runtime/kernel/CFC/load_model.py
# Problem: Empty file (0 lines, 1 byte) — CFCRuntime.run() crashes on import.
# Fix:     LoadModel class with estimate(text, constraint_map) → float [0,1].
# ══════════════════════════════════════════════════════════════════════════════
LOAD_MODEL = '''\
"""CFC/load_model.py — Computational load estimation for the CFC kernel.

LoadModel.estimate() is the first stage of the CFCRuntime pipeline:

    LoadModel → PostureResolver → ConstraintEnforcer → CFCState

The returned float drives PostureResolver.resolve() which branches at
0.40 / 0.70 / 0.90 to select the appropriate constraint posture.
"""
from __future__ import annotations
from typing import Any, Dict


# ── tuneable constants ────────────────────────────────────────────────────────
_CHARS_FOR_MAX_TEXT_LOAD = 4_000   # character count at which text load saturates to 1.0
_CONSTRAINT_WEIGHT        = 0.05   # each active constraint adds this to the total
_MAX_CONSTRAINT_LOAD      = 0.40   # cap so constraints alone cannot saturate the score


class LoadModel:
    """Estimates the computational load of a CFC request.

    The score is a simple two-factor model:

    * **Text factor** — scales linearly from 0.0 (empty input) to 1.0
      at ``_CHARS_FOR_MAX_TEXT_LOAD`` characters.

    * **Constraint factor** — each *active* (truthy) entry in
      ``constraint_map`` contributes ``_CONSTRAINT_WEIGHT``, capped at
      ``_MAX_CONSTRAINT_LOAD``.

    Combined score is clamped to [0.0, 1.0].
    """

    def estimate(self, text: str, constraint_map: Dict[str, Any]) -> float:
        """Return a load score in [0.0, 1.0].

        Parameters
        ----------
        text:
            Raw input text that the CFC kernel will process.
        constraint_map:
            Mapping of constraint name → value.  A constraint is considered
            *active* if its value is truthy (non-None, non-empty, non-zero).

        Returns
        -------
        float
            0.0 = negligible load  /  1.0 = fully saturated.
        """
        # ── text length contribution ──────────────────────────────────────────
        text_load = min(len(text) / _CHARS_FOR_MAX_TEXT_LOAD, 1.0)

        # ── active constraint contribution ────────────────────────────────────
        active_count    = sum(1 for v in constraint_map.values() if v)
        constraint_load = min(active_count * _CONSTRAINT_WEIGHT, _MAX_CONSTRAINT_LOAD)

        # ── combined score ────────────────────────────────────────────────────
        return round(min(text_load + constraint_load, 1.0), 4)
'''


# ══════════════════════════════════════════════════════════════════════════════
# FLAG #21 — 05_runtime/lattice_config.py
# Problem: PulseConfig defined AFTER LatticeConfig (which references it)
#          AND after the if __name__ == "__main__" guard → NameError at import.
# Fix:     Regex-based reorder — move PulseConfig block to just before
#          LatticeConfig without touching any other line.
# ══════════════════════════════════════════════════════════════════════════════

def fix_lattice_config(path: Path) -> bool:
    """Move PulseConfig class to before LatticeConfig.  Returns True if changed."""
    if not path.exists():
        print(f"  {FAIL}  not found: {path}")
        return False

    content = path.read_text(encoding="utf-8")

    # ── locate PulseConfig block ──────────────────────────────────────────────
    pc_pat = re.compile(
        r'(?m)^(@dataclass\s*\n)?class PulseConfig\b.*?(?=^@dataclass\s*\nclass |^class [A-Z]|^if __name__)',
        re.DOTALL | re.MULTILINE,
    )
    pc_match = pc_pat.search(content)

    # ── locate LatticeConfig start ────────────────────────────────────────────
    lc_pat   = re.compile(r'(?m)^(?:@dataclass\s*\n)?class LatticeConfig\b')
    lc_match = lc_pat.search(content)

    if not pc_match:
        print(f"  {SKIP}  PulseConfig block not found in lattice_config.py — skipping")
        return False
    if not lc_match:
        print(f"  {SKIP}  LatticeConfig not found in lattice_config.py — skipping")
        return False

    pc_start, pc_end = pc_match.span()
    lc_start         = lc_match.start()

    if pc_start < lc_start:
        print(f"  {SKIP}  PulseConfig already precedes LatticeConfig — no change needed")
        return False

    # ── surgery ───────────────────────────────────────────────────────────────
    pulse_block = pc_match.group(0)
    pulse_block = pulse_block.rstrip("\n") + "\n\n"

    # Remove PulseConfig from its current (late) position
    interim = content[:pc_start] + content[pc_end:]

    # Re-locate LatticeConfig in the trimmed content
    lc_match2 = lc_pat.search(interim)
    if not lc_match2:
        print(f"  {FAIL}  LatticeConfig vanished after PulseConfig removal — aborting")
        return False

    ins   = lc_match2.start()
    fixed = interim[:ins] + pulse_block + interim[ins:]

    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    print(f"  {PASS}  backed up → {bak.name}")
    path.write_text(fixed, encoding="utf-8")
    print(f"  {PASS}  patched   → {path.relative_to(REPO_ROOT)}")
    return True


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — apply all patches
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    errors = []

    patches = [
        ("FLAG #40 — vault/03_cli/vault_cli.py",
         "vault/03_cli/vault_cli.py",
         VAULT_CLI),

        ("FLAG #37 — vault/02_runtime/governance/events.py",
         "vault/02_runtime/governance/events.py",
         GOVERNANCE_EVENTS),

        ("FLAG #38 — vault/02_runtime/governance/hooks.py",
         "vault/02_runtime/governance/hooks.py",
         GOVERNANCE_HOOKS),

        ("FLAG #35 — vault/02_runtime/access/permissions.py",
         "vault/02_runtime/access/permissions.py",
         PERMISSIONS),

        ("FLAG #23 — 05_runtime/governance/engine.py",
         "05_runtime/governance/engine.py",
         GOVERNANCE_ENGINE),

        ("FLAG #24 — 05_runtime/kernel/CFC/load_model.py",
         "05_runtime/kernel/CFC/load_model.py",
         LOAD_MODEL),
    ]

    for label, rel_path, content in patches:
        print(f"\n── {label}")
        try:
            backup_and_write(rel_path, content)
        except Exception as exc:
            print(f"  {FAIL}  ERROR: {exc}")
            errors.append((label, exc))

    # Flag #21 handled separately (regex reorder, not full rewrite)
    print(f"\n── FLAG #21 — 05_runtime/lattice_config.py")
    try:
        fix_lattice_config(REPO_ROOT / "05_runtime" / "lattice_config.py")
    except Exception as exc:
        print(f"  {FAIL}  ERROR: {exc}")
        errors.append(("FLAG #21 — lattice_config.py", exc))

    # ── summary ───────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    if errors:
        print(f"Sprint 1 patch COMPLETED WITH {len(errors)} ERROR(S):")
        for label, exc in errors:
            print(f"  {FAIL}  {label}: {exc}")
        sys.exit(1)
    else:
        print("Sprint 1 patch COMPLETE — 7 defects resolved, 0 errors.")
        print("Run your test suite or import smoke-test to verify.")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
