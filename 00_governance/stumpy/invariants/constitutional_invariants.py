"""
constitutional_invariants.py
Stumpy Governance Engine — Constitutional invariant enforcement.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08

The module exposes both the functional registry API and the
ConstitutionalInvariants facade expected by StumpyEngine. The facade delegates
to the registry so legacy engine imports remain compatible with the expanded
checker implementation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple


@dataclass
class InvariantResult:
    invariant_id: str
    passed: bool
    message: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "passed": self.passed,
            "message": self.message,
            "evidence": self.evidence,
        }


CheckFn = Callable[[Dict[str, Any]], InvariantResult]
_REGISTRY: Dict[str, CheckFn] = {}


def register(invariant_id: str) -> Callable[[CheckFn], CheckFn]:
    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY[invariant_id] = fn
        return fn
    return decorator


@register("I·SRC")
def check_provenance(ctx: Dict[str, Any]) -> InvariantResult:
    has_source = bool(ctx.get("source") or ctx.get("provenance") or ctx.get("synthesis_id"))
    return InvariantResult("I·SRC", has_source, "ok" if has_source else "missing provenance/source field", {"keys_present": list(ctx.keys())})


@register("II·SCR")
def check_score_integrity(ctx: Dict[str, Any]) -> InvariantResult:
    score = ctx.get("confidence_score", ctx.get("confidence"))
    if score is None:
        return InvariantResult("II·SCR", True, "no score field — n/a")
    try:
        inflated = not (0.0 <= float(score) <= 1.0)
    except (TypeError, ValueError):
        return InvariantResult("II·SCR", False, f"invalid score '{score}'", {"score": score})
    return InvariantResult("II·SCR", not inflated, "ok" if not inflated else f"score {score} outside [0,1] — possible inflation", {"score": score})


@register("III·ISO")
def check_context_isolation(ctx: Dict[str, Any]) -> InvariantResult:
    has_window = bool(ctx.get("synthesis_id") or ctx.get("window_id"))
    return InvariantResult("III·ISO", has_window, "ok" if has_window else "no window/synthesis_id — context isolation unverifiable", {"synthesis_id": ctx.get("synthesis_id"), "window_id": ctx.get("window_id")})


@register("IV·DEC")
def check_escalation_declared(ctx: Dict[str, Any]) -> InvariantResult:
    valid_paths = {"NONE", "PARADOX_ENGINE", "FIELD_INTEL", "OPERATOR_ALERT"}
    path = ctx.get("escalation_path", ctx.get("escalationpath"))
    if path is None:
        return InvariantResult("IV·DEC", False, "escalation_path missing", ctx)
    passed = str(path).upper() in valid_paths
    return InvariantResult("IV·DEC", passed, "ok" if passed else f"unknown escalation path '{path}'", {"escalation_path": path, "valid": list(valid_paths)})


@register("V·SIL")
def check_null_result(ctx: Dict[str, Any]) -> InvariantResult:
    has_insight = bool(ctx.get("insight") or ctx.get("result"))
    has_log = bool(ctx.get("log_null") or ctx.get("null_logged"))
    passed = has_insight or has_log
    return InvariantResult("V·SIL", passed, "ok" if passed else "null result not logged — V·SIL breach", {"has_insight": has_insight, "has_log": has_log})


@register("VI·BND")
def check_boundary(ctx: Dict[str, Any]) -> InvariantResult:
    directive_keys = {"directive", "instruction", "command", "order", "mandate"}
    found = [k for k in ctx if k.lower() in directive_keys]
    passed = len(found) == 0
    return InvariantResult("VI·BND", passed, "ok" if passed else f"directive field(s) detected: {found}", {"directive_keys_found": found})


def check_all(ctx: Dict[str, Any]) -> List[InvariantResult]:
    return [fn(ctx) for fn in _REGISTRY.values()]


def check_one(invariant_id: str, ctx: Dict[str, Any]) -> InvariantResult:
    fn = _REGISTRY.get(invariant_id)
    if fn is None:
        return InvariantResult(invariant_id, False, f"no checker registered for '{invariant_id}'")
    return fn(ctx)


INVARIANT_IDS: Tuple[str, ...] = tuple(_REGISTRY.keys())


class ConstitutionalInvariants:
    """Compatibility facade used by StumpyEngine and integration callers."""

    def __init__(self, context: Dict[str, Any] | None = None) -> None:
        self.context = dict(context or {})

    def check_all(self, ctx: Dict[str, Any] | None = None) -> List[InvariantResult]:
        return check_all(self.context if ctx is None else ctx)

    def check_one(self, invariant_id: str, ctx: Dict[str, Any] | None = None) -> InvariantResult:
        return check_one(invariant_id, self.context if ctx is None else ctx)

    def assert_all(self, ctx: Dict[str, Any] | None = None) -> List[InvariantResult]:
        results = self.check_all(ctx)
        failures = [result for result in results if not result.passed]
        if failures:
            details = "; ".join(f"{r.invariant_id}: {r.message}" for r in failures)
            raise AssertionError(f"constitutional invariant failure: {details}")
        return results
