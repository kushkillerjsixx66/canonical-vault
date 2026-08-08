"""
runtime_invariants.py
Stumpy Governance Engine — Runtime invariant enforcement.

Operator: JRM-01 @liminaljermo  Version: 1.1  Revised: 2026-08-08
REMEDIATION: expanded from thin stub — added runtime checks covering
             mode validity, cadence bounds, escalation path consistency,
             and synthesis window timeout enforcement.

Runtime Invariants:
    R·MOD  — Operational mode must be a declared value (PASSIVE/ACTIVE/RECURSIVE)
    R·CAD  — Cadence must be within declared min/max bounds per mode
    R·ESC  — Escalation path must match CMX threshold outcomes
    R·WIN  — Synthesis window must not exceed maximum age
"""

from __future__ import annotations
import datetime
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .constitutional_invariants import InvariantResult


CheckFn = Callable[[Dict[str, Any]], InvariantResult]
_REGISTRY: Dict[str, CheckFn] = {}


def register(invariant_id: str) -> Callable[[CheckFn], CheckFn]:
    def decorator(fn: CheckFn) -> CheckFn:
        _REGISTRY[invariant_id] = fn
        return fn
    return decorator


# ── Constants ─────────────────────────────────────────────────────────────── #

_VALID_MODES = {"PASSIVE", "ACTIVE", "RECURSIVE"}

# Cadence bounds in seconds per mode
_CADENCE_BOUNDS: Dict[str, Tuple[int, int]] = {
    "PASSIVE":   (600,  7200),   # 10 min – 2 hours
    "ACTIVE":    (60,   600),    # 1 min – 10 min
    "RECURSIVE": (10,   300),    # 10 sec – 5 min
}

# Maximum synthesis window age in seconds before it is considered stale
_MAX_WINDOW_AGE_S = 3600  # 1 hour


# ── Invariant implementations ─────────────────────────────────────────────── #

@register("R·MOD")
def check_mode(ctx: Dict[str, Any]) -> InvariantResult:
    """Operational mode must be a declared canonical value."""
    mode = ctx.get("mode", ctx.get("operational_mode"))
    if mode is None:
        return InvariantResult("R·MOD", True, "no mode field — n/a")
    passed = str(mode).upper() in _VALID_MODES
    return InvariantResult(
        invariant_id="R·MOD",
        passed=passed,
        message="ok" if passed else f"undeclared mode '{mode}'",
        evidence={"mode": mode, "valid_modes": list(_VALID_MODES)},
    )


@register("R·CAD")
def check_cadence(ctx: Dict[str, Any]) -> InvariantResult:
    """Cadence_s must fall within declared bounds for the active mode."""
    mode    = str(ctx.get("mode", ctx.get("operational_mode", "PASSIVE"))).upper()
    cadence = ctx.get("cadence_s", ctx.get("cadence"))
    if cadence is None:
        return InvariantResult("R·CAD", True, "no cadence field — n/a")

    bounds = _CADENCE_BOUNDS.get(mode)
    if bounds is None:
        return InvariantResult("R·CAD", True, f"mode '{mode}' has no cadence constraint — n/a")

    low, high = bounds
    c = int(cadence)
    passed = low <= c <= high
    return InvariantResult(
        invariant_id="R·CAD",
        passed=passed,
        message="ok" if passed else
            f"cadence {c}s out of bounds [{low},{high}] for mode {mode}",
        evidence={"cadence_s": c, "mode": mode, "bounds": bounds},
    )


@register("R·ESC")
def check_escalation_consistency(ctx: Dict[str, Any]) -> InvariantResult:
    """
    Escalation path must match what CMX thresholds mandate.
    If max_contradiction >= 0.7, path must be PARADOX_ENGINE.
    If confidence < 0.4, path must be NONE.
    """
    path        = str(ctx.get("escalation_path", ctx.get("escalationpath", "NONE"))).upper()
    max_cmx     = ctx.get("max_contradiction_score")
    conf        = ctx.get("confidence_score", ctx.get("confidence"))

    violations: List[str] = []

    if max_cmx is not None and float(max_cmx) >= 0.70:
        if path != "PARADOX_ENGINE":
            violations.append(
                f"CMX={max_cmx:.2f} >= 0.70 requires PARADOX_ENGINE, got {path}"
            )

    if conf is not None and float(conf) < 0.40:
        if path != "NONE":
            violations.append(
                f"confidence={float(conf):.2f} < 0.40 requires NONE, got {path}"
            )

    passed = len(violations) == 0
    return InvariantResult(
        invariant_id="R·ESC",
        passed=passed,
        message="ok" if passed else "; ".join(violations),
        evidence={
            "escalation_path": path,
            "max_contradiction_score": max_cmx,
            "confidence_score": conf,
        },
    )


@register("R·WIN")
def check_window_age(ctx: Dict[str, Any]) -> InvariantResult:
    """Synthesis window must not exceed maximum age (stale window detection)."""
    ts_str = ctx.get("timestamp", ctx.get("window_start"))
    if ts_str is None:
        return InvariantResult("R·WIN", True, "no timestamp — n/a")

    try:
        ts = datetime.datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=datetime.timezone.utc)
        age_s = (now - ts).total_seconds()
    except (ValueError, TypeError):
        return InvariantResult("R·WIN", True, "unparseable timestamp — n/a")

    passed = age_s <= _MAX_WINDOW_AGE_S
    return InvariantResult(
        invariant_id="R·WIN",
        passed=passed,
        message="ok" if passed else
            f"window is {int(age_s)}s old (max {_MAX_WINDOW_AGE_S}s) — stale",
        evidence={"age_seconds": int(age_s), "max_age_seconds": _MAX_WINDOW_AGE_S},
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
