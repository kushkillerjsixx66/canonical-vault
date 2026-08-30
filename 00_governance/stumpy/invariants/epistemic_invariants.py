"""
Epistemic invariant registry plus compatibility facade for StumpyKernel.
"""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Tuple
from .constitutional_invariants import InvariantResult

CheckFn = Callable[[Dict[str, Any]], InvariantResult]
_REGISTRY: Dict[str, CheckFn] = {}


def register(invariant_id: str) -> Callable[[CheckFn], CheckFn]:
    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY[invariant_id] = fn
        return fn
    return decorator

_SIGNAL_QUAL_THRESHOLD = 0.30
_VALID_EVIDENCE_CLASSES = {"DIRECT", "DERIVED", "INFERRED", "CORROBORATED", "WEAK", "SPECULATIVE", "STRUCTURAL"}


@register("E·QUL")
def check_signal_qualification(ctx: Dict[str, Any]) -> InvariantResult:
    signal_set = ctx.get("signal_set", [])
    if not signal_set:
        return InvariantResult("E·QUL", True, "no signal_set — n/a")
    failures = [s for s in signal_set if float(s.get("confidence", 1.0)) < _SIGNAL_QUAL_THRESHOLD]
    return InvariantResult("E·QUL", not failures, "ok" if not failures else f"{len(failures)} signal(s) below qualification threshold ({_SIGNAL_QUAL_THRESHOLD})", {"failing_signals": [s.get("signal_type", "?") for s in failures]})


@register("E·EVD")
def check_evidence_class(ctx: Dict[str, Any]) -> InvariantResult:
    signal_set = ctx.get("signal_set", [])
    if not signal_set:
        return InvariantResult("E·EVD", True, "no signal_set — n/a")
    missing, invalid = [], []
    for s in signal_set:
        ec = s.get("evidence_class")
        if ec is None:
            missing.append(s.get("signal_type", "?"))
        elif str(ec).upper() not in _VALID_EVIDENCE_CLASSES:
            invalid.append(f"{s.get('signal_type', '?')}={ec}")
    return InvariantResult("E·EVD", not missing and not invalid, "ok" if not missing and not invalid else f"missing evidence_class: {missing}; invalid: {invalid}", {"missing": missing, "invalid": invalid})


@register("E·LIN")
def check_lineage(ctx: Dict[str, Any]) -> InvariantResult:
    lineage = ctx.get("lineage", ctx.get("provenance_chain", []))
    if not lineage:
        has_root = bool(ctx.get("synthesis_id") or ctx.get("source"))
        return InvariantResult("E·LIN", has_root, "ok — root source present" if has_root else "no lineage or root source", {"synthesis_id": ctx.get("synthesis_id")})
    if not isinstance(lineage, (list, tuple)):
        return InvariantResult("E·LIN", False, "lineage must be a sequence")
    seen, circular = set(), []
    for node in lineage:
        nid = str(node) if isinstance(node, str) else str(node.get("id", node))
        if nid in seen:
            circular.append(nid)
        seen.add(nid)
    return InvariantResult("E·LIN", not circular, "ok" if not circular else f"circular lineage detected: {circular}", {"lineage_depth": len(lineage), "circular_nodes": circular})


@register("E·WSG")
def check_weak_signal_gate(ctx: Dict[str, Any]) -> InvariantResult:
    signal_set, score = ctx.get("signal_set", []), ctx.get("confidence_score", ctx.get("confidence"))
    if not signal_set or score is None:
        return InvariantResult("E·WSG", True, "no signal_set or confidence — n/a")
    weak = [s for s in signal_set if str(s.get("evidence_class", "")).upper() in ("WEAK", "SPECULATIVE")]
    ratio = len(weak) / len(signal_set) if signal_set else 0
    violation = ratio >= 0.5 and float(score) > 0.5
    return InvariantResult("E·WSG", not violation, "ok" if not violation else f"weak signal ratio {ratio:.2f} with confidence {float(score):.2f} — gate breached", {"weak_ratio": ratio, "confidence_score": score})


def check_all(ctx: Dict[str, Any]) -> List[InvariantResult]:
    return [fn(ctx) for fn in _REGISTRY.values()]


def check_one(invariant_id: str, ctx: Dict[str, Any]) -> InvariantResult:
    fn = _REGISTRY.get(invariant_id)
    return fn(ctx) if fn else InvariantResult(invariant_id, False, f"no checker registered for '{invariant_id}'")


INVARIANT_IDS: Tuple[str, ...] = tuple(_REGISTRY.keys())


class EpistemicInvariants:
    """Compatibility facade used by StumpyKernel and legacy tests."""
    def check(self, ctx: Dict[str, Any]) -> bool:
        if "lineage" in ctx and not isinstance(ctx["lineage"], (list, tuple)):
            return False
        return all(result.passed for result in check_all(ctx))

    def check_all(self, ctx: Dict[str, Any]) -> List[InvariantResult]:
        return check_all(ctx)

    def check_one(self, invariant_id: str, ctx: Dict[str, Any]) -> InvariantResult:
        return check_one(invariant_id, ctx)
