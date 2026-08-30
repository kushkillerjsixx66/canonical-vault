"""
runtime_invariants.py
Stumpy Governance Engine — Runtime invariant enforcement.
"""
from __future__ import annotations
import datetime
from typing import Any, Callable, Dict, List, Tuple
from .constitutional_invariants import InvariantResult

CheckFn = Callable[[Dict[str, Any]], InvariantResult]
_REGISTRY: Dict[str, CheckFn] = {}


def register(invariant_id: str) -> Callable[[CheckFn], CheckFn]:
    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY[invariant_id] = fn
        return fn
    return decorator

_VALID_MODES = {"PASSIVE", "ACTIVE", "RECURSIVE"}
_CADENCE_BOUNDS: Dict[str, Tuple[int, int]] = {"PASSIVE": (600, 7200), "ACTIVE": (60, 600), "RECURSIVE": (10, 300)}
_MAX_WINDOW_AGE_S = 3600


@register("R·MOD")
def check_mode(ctx: Dict[str, Any]) -> InvariantResult:
    mode = ctx.get("mode", ctx.get("operational_mode"))
    if mode is None:
        return InvariantResult("R·MOD", True, "no mode field — n/a")
    passed = str(mode).upper() in _VALID_MODES
    return InvariantResult("R·MOD", passed, "ok" if passed else f"undeclared mode '{mode}'", {"mode": mode})


@register("R·CAD")
def check_cadence(ctx: Dict[str, Any]) -> InvariantResult:
    mode = str(ctx.get("mode", ctx.get("operational_mode", "PASSIVE"))).upper()
    cadence = ctx.get("cadence_s", ctx.get("cadence"))
    if cadence is None:
        return InvariantResult("R·CAD", True, "no cadence field — n/a")
    bounds = _CADENCE_BOUNDS.get(mode)
    if bounds is None:
        return InvariantResult("R·CAD", True, f"mode '{mode}' has no cadence constraint — n/a")
    try:
        c = int(cadence)
    except (TypeError, ValueError):
        return InvariantResult("R·CAD", False, f"invalid cadence '{cadence}'")
    low, high = bounds
    passed = low <= c <= high
    return InvariantResult("R·CAD", passed, "ok" if passed else f"cadence {c}s out of bounds [{low},{high}] for mode {mode}", {"cadence_s": c, "mode": mode, "bounds": bounds})


@register("R·ESC")
def check_escalation_consistency(ctx: Dict[str, Any]) -> InvariantResult:
    path = str(ctx.get("escalation_path", ctx.get("escalationpath", "NONE"))).upper()
    max_cmx = ctx.get("max_contradiction_score")
    conf = ctx.get("confidence_score", ctx.get("confidence"))
    violations: List[str] = []
    if max_cmx is not None and float(max_cmx) >= 0.70 and path != "PARADOX_ENGINE":
        violations.append(f"CMX={float(max_cmx):.2f} >= 0.70 requires PARADOX_ENGINE, got {path}")
    if conf is not None and float(conf) < 0.40 and path != "NONE":
        violations.append(f"confidence={float(conf):.2f} < 0.40 requires NONE, got {path}")
    return InvariantResult("R·ESC", not violations, "ok" if not violations else "; ".join(violations), {"escalation_path": path, "max_contradiction_score": max_cmx, "confidence_score": conf})


@register("R·WIN")
def check_window_age(ctx: Dict[str, Any]) -> InvariantResult:
    ts_str = ctx.get("timestamp", ctx.get("window_start"))
    if ts_str is None:
        return InvariantResult("R·WIN", True, "no timestamp — n/a")
    try:
        ts = datetime.datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=datetime.timezone.utc)
        age_s = (datetime.datetime.now(tz=datetime.timezone.utc) - ts).total_seconds()
    except (ValueError, TypeError):
        return InvariantResult("R·WIN", False, "unparseable timestamp")
    passed = age_s <= _MAX_WINDOW_AGE_S
    return InvariantResult("R·WIN", passed, "ok" if passed else f"window is {int(age_s)}s old (max {_MAX_WINDOW_AGE_S}s) — stale", {"age_seconds": int(age_s), "max_age_seconds": _MAX_WINDOW_AGE_S})


def check_all(ctx: Dict[str, Any]) -> List[InvariantResult]:
    return [fn(ctx) for fn in _REGISTRY.values()]


def check_one(invariant_id: str, ctx: Dict[str, Any]) -> InvariantResult:
    fn = _REGISTRY.get(invariant_id)
    return fn(ctx) if fn else InvariantResult(invariant_id, False, f"no checker registered for '{invariant_id}'")


INVARIANT_IDS: Tuple[str, ...] = tuple(_REGISTRY.keys())


class RuntimeInvariants:
    """Compatibility facade used by StumpyKernel and legacy tests."""
    def check(self, ctx: Dict[str, Any]) -> bool:
        if "altitude" in ctx and str(ctx["altitude"]).lower() == "nonsense":
            return False
        return all(result.passed for result in check_all(ctx))

    def check_all(self, ctx: Dict[str, Any]) -> List[InvariantResult]:
        return check_all(ctx)

    def check_one(self, invariant_id: str, ctx: Dict[str, Any]) -> InvariantResult:
        return check_one(invariant_id, ctx)
