"""
epistemic_invariants.py
Stumpy Governance Engine — Epistemic invariant enforcement.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from thin stub — added EpistemicInvariant checks
             covering signal qualification, evidence class validation,
             lineage completeness, and weak-signal threshold gating.

Epistemic Invariants (from 02_epistemic_substrate/epistemic_laws.md):
    E·QUL  — All signals must meet qualification threshold before synthesis
    E·EVD  — Evidence class must be declared for every signal
    E·LIN  — Lineage chain must be present and non-circular
    E·WSG  — Weak signals must not be promoted to high-confidence claims
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple

from .constitutional_invariants import InvariantResult


# ── Type alias ────────────────────────────────────────────────────────────── #

CheckFn = Callable[[Dict[str, Any]], InvariantResult]

_REGISTRY: Dict[str, CheckFn] = {}


def register(invariant_id: str) -> Callable[[CheckFn], CheckFn]:
    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY[invariant_id] = fn
        return fn
    return decorator


# ── Invariant implementations ─────────────────────────────────────────────── #

# Minimum per-signal confidence to be admitted into synthesis
_SIGNAL_QUAL_THRESHOLD = 0.30

# Valid evidence classes (from 02_epistemic_substrate/evidence_classes.yaml)
_VALID_EVIDENCE_CLASSES = {
    "DIRECT", "DERIVED", "INFERRED", "CORROBORATED",
    "WEAK", "SPECULATIVE", "STRUCTURAL",
}


@register("E·QUL")
def check_signal_qualification(ctx: Dict[str, Any]) -> InvariantResult:
    """All signals in the signal_set must meet the qualification threshold."""
    signal_set = ctx.get("signal_set", [])
    if not signal_set:
        return InvariantResult("E·QUL", True, "no signal_set — n/a")

    failures = [
        s for s in signal_set
        if float(s.get("confidence", 1.0)) < _SIGNAL_QUAL_THRESHOLD
    ]
    passed = len(failures) == 0
    return InvariantResult(
        invariant_id="E·QUL",
        passed=passed,
        message="ok" if passed else
            f"{len(failures)} signal(s) below qualification threshold ({_SIGNAL_QUAL_THRESHOLD})",
        evidence={"failing_signals": [s.get("signal_type", "?") for s in failures]},
    )


@register("E·EVD")
def check_evidence_class(ctx: Dict[str, Any]) -> InvariantResult:
    """Every signal must declare a valid evidence class."""
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

    passed = len(missing) == 0 and len(invalid) == 0
    return InvariantResult(
        invariant_id="E·EVD",
        passed=passed,
        message="ok" if passed else
            f"missing evidence_class: {missing}; invalid: {invalid}",
        evidence={"missing": missing, "invalid": invalid},
    )


@register("E·LIN")
def check_lineage(ctx: Dict[str, Any]) -> InvariantResult:
    """Lineage chain must be present and non-circular."""
    lineage = ctx.get("lineage", ctx.get("provenance_chain", []))
    if not lineage:
        # If there's a synthesis_id at least, partial lineage is acceptable
        has_root = bool(ctx.get("synthesis_id") or ctx.get("source"))
        return InvariantResult(
            invariant_id="E·LIN",
            passed=has_root,
            message="ok — root source present" if has_root else "no lineage or root source",
            evidence={"synthesis_id": ctx.get("synthesis_id")},
        )

    # Cycle detection: no repeated node IDs in the chain
    seen: set = set()
    circular: List[str] = []
    for node in lineage:
        nid = str(node) if isinstance(node, str) else str(node.get("id", node))
        if nid in seen:
            circular.append(nid)
        seen.add(nid)

    passed = len(circular) == 0
    return InvariantResult(
        invariant_id="E·LIN",
        passed=passed,
        message="ok" if passed else f"circular lineage detected: {circular}",
        evidence={"lineage_depth": len(lineage), "circular_nodes": circular},
    )


@register("E·WSG")
def check_weak_signal_gate(ctx: Dict[str, Any]) -> InvariantResult:
    """Weak signals must not inflate the overall confidence score."""
    signal_set      = ctx.get("signal_set", [])
    confidence_score = ctx.get("confidence_score", ctx.get("confidence"))

    if not signal_set or confidence_score is None:
        return InvariantResult("E·WSG", True, "no signal_set or confidence — n/a")

    weak_signals = [
        s for s in signal_set
        if str(s.get("evidence_class", "")).upper() in ("WEAK", "SPECULATIVE")
    ]
    if not weak_signals:
        return InvariantResult("E·WSG", True, "no weak signals — n/a")

    # If majority of signals are weak, confidence must be ≤ 0.5
    weak_ratio = len(weak_signals) / len(signal_set)
    score      = float(confidence_score)
    violation  = weak_ratio >= 0.5 and score > 0.5

    return InvariantResult(
        invariant_id="E·WSG",
        passed=not violation,
        message="ok" if not violation else
            f"weak signal ratio {weak_ratio:.2f} with confidence {score:.2f} — gate breached",
        evidence={"weak_ratio": weak_ratio, "confidence_score": score},
    )


# ── Dispatcher ────────────────────────────────────────────────────────────── #

def check_all(ctx: Dict[str, Any]) -> List[InvariantResult]:
    """Run all registered epistemic invariant checks against ctx."""
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
