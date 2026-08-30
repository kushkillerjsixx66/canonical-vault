"""
sovereignty_invariants.py
Stumpy Governance Engine — Sovereignty invariant enforcement.
"""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Set, Tuple
from .constitutional_invariants import InvariantResult

CheckFn = Callable[[Dict[str, Any]], InvariantResult]
_REGISTRY: Dict[str, CheckFn] = {}

_REGISTERED_OPERATORS: Set[str] = {"JRM-01", "jrm-01", "liminaljermo"}
_VALID_POSTURES: Set[str] = {"OBSERVE", "SURFACE", "ALERT", "ESCALATE", "CONTAIN", "ARCHIVE"}
_SUBSYSTEM_NAMESPACES: Dict[str, str] = {"veil": "05_runtime", "vara": "02_epistemic_substrate", "stumpy": "00_governance", "vault": "03_vault_pipeline", "paradox": "10_simulation", "cds": "canon"}


def register(invariant_id: str) -> Callable[[CheckFn], CheckFn]:
    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY[invariant_id] = fn
        return fn
    return decorator


@register("S·ROOT")
def check_sovereignty_root(ctx: Dict[str, Any]) -> InvariantResult:
    """The explicit sovereignty marker, when supplied, must be canonical root."""
    sovereignty = ctx.get("sovereignty")
    if sovereignty is None:
        return InvariantResult("S·ROOT", True, "no sovereignty field — n/a")
    passed = str(sovereignty).lower() == "root"
    return InvariantResult("S·ROOT", passed, "ok" if passed else f"invalid sovereignty '{sovereignty}'", {"sovereignty": sovereignty, "required": "root"})


@register("S·OPR")
def check_operator_identity(ctx: Dict[str, Any]) -> InvariantResult:
    op = ctx.get("operator", ctx.get("operator_id"))
    if op is None:
        return InvariantResult("S·OPR", True, "no operator field — n/a")
    passed = str(op).lower() in {o.lower() for o in _REGISTERED_OPERATORS}
    return InvariantResult("S·OPR", passed, "ok" if passed else f"unregistered operator '{op}'", {"operator": op, "registered": sorted(_REGISTERED_OPERATORS)})


@register("S·PST")
def check_posture(ctx: Dict[str, Any]) -> InvariantResult:
    posture = ctx.get("posture", ctx.get("execution_posture"))
    if posture is None:
        return InvariantResult("S·PST", True, "no posture field — n/a")
    passed = str(posture).upper() in _VALID_POSTURES
    return InvariantResult("S·PST", passed, "ok" if passed else f"undeclared posture '{posture}'", {"posture": posture, "valid_postures": sorted(_VALID_POSTURES)})


@register("S·NIF")
def check_non_interference(ctx: Dict[str, Any]) -> InvariantResult:
    subsystem, target_namespace = ctx.get("subsystem", ""), ctx.get("target_namespace")
    if not target_namespace or not subsystem:
        return InvariantResult("S·NIF", True, "no cross-namespace write declared — n/a")
    own_ns = _SUBSYSTEM_NAMESPACES.get(str(subsystem).lower())
    if own_ns is None:
        return InvariantResult("S·NIF", True, f"subsystem '{subsystem}' not in namespace map — n/a")
    passed = str(target_namespace).startswith(own_ns)
    return InvariantResult("S·NIF", passed, "ok" if passed else f"subsystem '{subsystem}' attempting write into '{target_namespace}' (own: '{own_ns}')", {"subsystem": subsystem, "own_namespace": own_ns, "target_namespace": target_namespace})


@register("S·AUT")
def check_authority_attestation(ctx: Dict[str, Any]) -> InvariantResult:
    action = ctx.get("action", ctx.get("operator_action"))
    if not action:
        return InvariantResult("S·AUT", True, "no operator action declared — n/a")
    has_att = bool(ctx.get("operator_sig") or ctx.get("authority_token") or ctx.get("csig") or ctx.get("containment_sig"))
    return InvariantResult("S·AUT", has_att, "ok" if has_att else f"operator action '{action}' carries no authority attestation", {"action": action, "has_attestation": has_att})


def check_all(ctx: Dict[str, Any]) -> List[InvariantResult]:
    return [fn(ctx) for fn in _REGISTRY.values()]


def check_one(invariant_id: str, ctx: Dict[str, Any]) -> InvariantResult:
    fn = _REGISTRY.get(invariant_id)
    return fn(ctx) if fn else InvariantResult(invariant_id, False, f"no checker registered for '{invariant_id}'")


INVARIANT_IDS: Tuple[str, ...] = tuple(_REGISTRY.keys())


class SovereigntyInvariants:
    """Compatibility facade used by StumpyKernel and tests."""
    def check(self, ctx: Dict[str, Any]) -> bool:
        return all(result.passed for result in check_all(ctx))

    def check_all(self, ctx: Dict[str, Any]) -> List[InvariantResult]:
        return check_all(ctx)

    def check_one(self, invariant_id: str, ctx: Dict[str, Any]) -> InvariantResult:
        return check_one(invariant_id, ctx)
