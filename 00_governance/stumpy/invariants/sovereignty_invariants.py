"""
sovereignty_invariants.py
Stumpy Governance Engine — Sovereignty invariant enforcement.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from thin stub — added sovereignty checks covering
             operator identity verification, posture declaration, and
             subsystem boundary non-interference.

Sovereignty Invariants (from 01_sovereignty/):
    S·OPR  — Operator identity must be declared and match registered identity
    S·PST  — Execution posture must be a declared canonical value
    S·NIF  — No subsystem may directly modify another subsystem's state
    S·AUT  — All operator actions must carry authority attestation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Set, Tuple

from .constitutional_invariants import InvariantResult


CheckFn = Callable[[Dict[str, Any]], InvariantResult]
_REGISTRY: Dict[str, CheckFn] = {}


def register(invariant_id: str) -> Callable[[CheckFn], CheckFn]:
    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY[invariant_id] = fn
        return fn
    return decorator


# ── Constants ─────────────────────────────────────────────────────────────── #

# Registered operator identities (from 00_governance/operator_manual/operator_identity.yaml)
_REGISTERED_OPERATORS: Set[str] = {"JRM-01", "jrm-01", "liminaljermo"}

# Valid execution postures (from 00_governance/execution_postures.yaml)
_VALID_POSTURES: Set[str] = {
    "OBSERVE", "SURFACE", "ALERT", "ESCALATE", "CONTAIN", "ARCHIVE"
}

# Canonical subsystem boundaries — a subsystem may not write into another's namespace
_SUBSYSTEM_NAMESPACES: Dict[str, str] = {
    "veil":         "05_runtime",
    "vara":         "02_epistemic_substrate",
    "stumpy":       "00_governance",
    "vault":        "03_vault_pipeline",
    "paradox":      "10_simulation",
    "cds":          "canon",
}


# ── Invariant implementations ─────────────────────────────────────────────── #

@register("S·OPR")
def check_operator_identity(ctx: Dict[str, Any]) -> InvariantResult:
    """Operator identity must be declared and match a registered identity."""
    op = ctx.get("operator", ctx.get("operator_id"))
    if op is None:
        # Not all packets carry an operator field — treat as n/a
        return InvariantResult("S·OPR", True, "no operator field — n/a")

    passed = str(op).lower() in {o.lower() for o in _REGISTERED_OPERATORS}
    return InvariantResult(
        invariant_id="S·OPR",
        passed=passed,
        message="ok" if passed else f"unregistered operator '{op}'",
        evidence={"operator": op, "registered": sorted(_REGISTERED_OPERATORS)},
    )


@register("S·PST")
def check_posture(ctx: Dict[str, Any]) -> InvariantResult:
    """Execution posture must be a declared canonical value."""
    posture = ctx.get("posture", ctx.get("execution_posture"))
    if posture is None:
        return InvariantResult("S·PST", True, "no posture field — n/a")

    passed = str(posture).upper() in _VALID_POSTURES
    return InvariantResult(
        invariant_id="S·PST",
        passed=passed,
        message="ok" if passed else f"undeclared posture '{posture}'",
        evidence={"posture": posture, "valid_postures": sorted(_VALID_POSTURES)},
    )


@register("S·NIF")
def check_non_interference(ctx: Dict[str, Any]) -> InvariantResult:
    """
    No subsystem may write into another subsystem's namespace.
    Checks that ctx['target_namespace'] (if present) matches ctx['subsystem'].
    """
    subsystem        = ctx.get("subsystem", "")
    target_namespace = ctx.get("target_namespace")

    if not target_namespace or not subsystem:
        return InvariantResult("S·NIF", True, "no cross-namespace write declared — n/a")

    own_ns = _SUBSYSTEM_NAMESPACES.get(str(subsystem).lower())
    if own_ns is None:
        return InvariantResult(
            "S·NIF", True,
            f"subsystem '{subsystem}' not in namespace map — n/a",
        )

    passed = str(target_namespace).startswith(own_ns)
    return InvariantResult(
        invariant_id="S·NIF",
        passed=passed,
        message="ok" if passed else
            f"subsystem '{subsystem}' attempting write into '{target_namespace}' (own: '{own_ns}')",
        evidence={
            "subsystem":        subsystem,
            "own_namespace":    own_ns,
            "target_namespace": target_namespace,
        },
    )


@register("S·AUT")
def check_authority_attestation(ctx: Dict[str, Any]) -> InvariantResult:
    """
    Operator actions must carry an authority attestation token.
    Attestation is any of: operator_sig, authority_token, csig.
    """
    action = ctx.get("action", ctx.get("operator_action"))
    if not action:
        return InvariantResult("S·AUT", True, "no operator action declared — n/a")

    has_att = bool(
        ctx.get("operator_sig")
        or ctx.get("authority_token")
        or ctx.get("csig")
        or ctx.get("containment_sig")
    )
    return InvariantResult(
        invariant_id="S·AUT",
        passed=has_att,
        message="ok" if has_att else
            f"operator action '{action}' carries no authority attestation",
        evidence={"action": action, "has_attestation": has_att},
    )


# ── Dispatcher ────────────────────────────────────────────────────────────── #

def check_all(ctx: Dict[str, Any]) -> List[InvariantResult]:
    return [fn(ctx) for fn in _REGISTRY.values()]


def check_one(invariant_id: str, ctx: Dict[str, Any]) -> InvariantResult:
    fn = _REGISTRY.get(invariant_id)
    if fn is None:
        return InvariantResult(
            invariant_id=invariant_id,
            passed=False,
            message=f"no checker registered for '{invariant_id}'",
        )
    return fn(ctx)


INVARIANT_IDS: Tuple[str, ...] = tuple(_REGISTRY.keys())
