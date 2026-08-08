"""
constitutional_invariants.py
Stumpy Governance Engine — Constitutional invariant enforcement.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from thin stub — added ConstitutionalInvariant registry,
             check() dispatcher, and enforcement for the six canonical
             system invariants (I·SRC through VI·BND).

Constitutional Invariants (from 00_governance/constitution/invariants.md):
    I·SRC  — Full provenance on every construct
    II·SCR — Scores derived from signal data; no inflation
    III·ISO — No cross-context bleed between synthesis windows
    IV·DEC — Every escalation path explicitly declared
    V·SIL  — Null result valid; logged, not suppressed
    VI·BND — CDS surfaces constructs only; no directives
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ── Invariant result ──────────────────────────────────────────────────────── #

@dataclass
class InvariantResult:
    invariant_id: str
    passed:       bool
    message:      str            = ""
    evidence:     Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "passed":       self.passed,
            "message":      self.message,
            "evidence":     self.evidence,
        }


# ── Type alias for a check function ──────────────────────────────────────── #

CheckFn = Callable[[Dict[str, Any]], InvariantResult]


# ── Registry ──────────────────────────────────────────────────────────────── #

_REGISTRY: Dict[str, CheckFn] = {}


def register(invariant_id: str) -> Callable[[CheckFn], CheckFn]:
    """Decorator: register a function as the checker for invariant_id."""
    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY[invariant_id] = fn
        return fn
    return decorator


# ── Invariant implementations ─────────────────────────────────────────────── #

@register("I·SRC")
def check_provenance(ctx: Dict[str, Any]) -> InvariantResult:
    """Every construct must carry a provenance / source field."""
    has_source = bool(ctx.get("source") or ctx.get("provenance") or ctx.get("synthesis_id"))
    return InvariantResult(
        invariant_id="I·SRC",
        passed=has_source,
        message="ok" if has_source else "missing provenance/source field",
        evidence={"keys_present": list(ctx.keys())},
    )


@register("II·SCR")
def check_score_integrity(ctx: Dict[str, Any]) -> InvariantResult:
    """Confidence scores must be derived, not clamped or inflated."""
    score = ctx.get("confidence_score", ctx.get("confidence"))
    if score is None:
        return InvariantResult("II·SCR", True, "no score field — n/a")
    inflated = not (0.0 <= float(score) <= 1.0)
    return InvariantResult(
        invariant_id="II·SCR",
        passed=not inflated,
        message="ok" if not inflated else f"score {score} outside [0,1] — possible inflation",
        evidence={"score": score},
    )


@register("III·ISO")
def check_context_isolation(ctx: Dict[str, Any]) -> InvariantResult:
    """Synthesis window must carry an isolated window_id / synthesis_id."""
    has_window = bool(ctx.get("synthesis_id") or ctx.get("window_id"))
    return InvariantResult(
        invariant_id="III·ISO",
        passed=has_window,
        message="ok" if has_window else "no window/synthesis_id — context isolation unverifiable",
        evidence={"synthesis_id": ctx.get("synthesis_id"), "window_id": ctx.get("window_id")},
    )


@register("IV·DEC")
def check_escalation_declared(ctx: Dict[str, Any]) -> InvariantResult:
    """Every escalation path must be explicitly declared (not implied)."""
    valid_paths = {"NONE", "PARADOX_ENGINE", "FIELD_INTEL", "OPERATOR_ALERT"}
    path = ctx.get("escalation_path", ctx.get("escalationpath"))
    if path is None:
        return InvariantResult("IV·DEC", False, "escalation_path missing", evidence=ctx)
    passed = str(path).upper() in valid_paths
    return InvariantResult(
        invariant_id="IV·DEC",
        passed=passed,
        message="ok" if passed else f"unknown escalation path '{path}'",
        evidence={"escalation_path": path, "valid": list(valid_paths)},
    )


@register("V·SIL")
def check_null_result(ctx: Dict[str, Any]) -> InvariantResult:
    """Null/empty results must be logged, not suppressed."""
    # This invariant is structural — we verify the caller supplied a log_null field
    # or that an insight is present (non-null synthesis).
    has_insight = bool(ctx.get("insight") or ctx.get("result"))
    has_log     = bool(ctx.get("log_null") or ctx.get("null_logged"))
    passed      = has_insight or has_log
    return InvariantResult(
        invariant_id="V·SIL",
        passed=passed,
        message="ok" if passed else "null result not logged — V·SIL breach",
        evidence={"has_insight": has_insight, "has_log": has_log},
    )


@register("VI·BND")
def check_boundary(ctx: Dict[str, Any]) -> InvariantResult:
    """CDS surfaces constructs only — no directive fields permitted."""
    directive_keys = {"directive", "instruction", "command", "order", "mandate"}
    found = [k for k in ctx if k.lower() in directive_keys]
    passed = len(found) == 0
    return InvariantResult(
        invariant_id="VI·BND",
        passed=passed,
        message="ok" if passed else f"directive field(s) detected: {found}",
        evidence={"directive_keys_found": found},
    )


# ── Dispatcher ────────────────────────────────────────────────────────────── #

def check_all(ctx: Dict[str, Any]) -> List[InvariantResult]:
    """Run all registered constitutional invariant checks against ctx."""
    return [fn(ctx) for fn in _REGISTRY.values()]


def check_one(invariant_id: str, ctx: Dict[str, Any]) -> InvariantResult:
    """Run a single invariant check by ID."""
    fn = _REGISTRY.get(invariant_id)
    if fn is None:
        return InvariantResult(
            invariant_id=invariant_id,
            passed=False,
            message=f"no checker registered for '{invariant_id}'",
        )
    return fn(ctx)


INVARIANT_IDS: Tuple[str, ...] = tuple(_REGISTRY.keys())
