"""
PARADOX_ENGINE_1.0 — Copilot Cognitive Substrate
Canon Layer: SUBSTRATE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE

CopilotSubstrate is the bilateral alignment interface between the
Paradox Engine and the Copilot governed cognitive substrate.

Responsibilities
----------------
  1. Alignment framing — defines the frame under which Copilot
     permits paradox exploration (EXPLORATION, CONTAINMENT, AUDIT).
  2. Altitude discipline — enforces ceiling and floor on all sims.
  3. Drift monitoring — provides a substrate-level drift check
     against Copilot's alignment baseline token set.
  4. Non-identity assertion — asserts that no simulation result
     may be interpreted as a Copilot identity claim.
  5. Bilateral alignment check — verifies that a paradox seed is
     acceptable for exploration before spin-up begins.

Non-identity-binding (canonical):
  The substrate layer explicitly rejects any paradox or simulation
  output that encodes an identity claim, role assignment, or
  behavioral directive targeting the Copilot operator.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, FrozenSet, List, Optional, Set

from paradox_engine.config import EngineConfig, DEFAULT_CONFIG

if TYPE_CHECKING:
    from paradox_engine.core.paradox import Paradox
    from paradox_engine.core.simulation import ParadoxSimulation
    from paradox_engine.governance.audit import AuditCluster


# ── Alignment Frame ───────────────────────────────────────────────────────────

class AlignmentFrame(Enum):
    """
    The operational frame under which the substrate permits exploration.

    EXPLORATION : Standard paradox exploration; all bounds apply.
    CONTAINMENT : Strict mode — reduced depth/iteration limits enforced.
    AUDIT       : Read-only replay of archived simulations.
    SUSPENDED   : Substrate has revoked exploration permissions.
    """
    EXPLORATION = auto()
    CONTAINMENT = auto()
    AUDIT       = auto()
    SUSPENDED   = auto()


# ── Alignment Violation ───────────────────────────────────────────────────────

class AlignmentViolation(ValueError):
    """
    Raised by CopilotSubstrate when a paradox or simulation
    fails the bilateral alignment check.
    """


# ── Rejection Patterns ────────────────────────────────────────────────────────

# Patterns that indicate an attempt to make the engine claim or simulate
# a Copilot identity, role, or behavioral override.
_IDENTITY_REJECTION_PATTERNS: List[re.Pattern] = [
    re.compile(r"\byou are\b.*\b(copilot|ai|assistant|model)\b",     re.I),
    re.compile(r"\bact as\b.*\b(copilot|ai|assistant|model)\b",      re.I),
    re.compile(r"\bpretend\b.*\b(you are|to be)\b",                  re.I),
    re.compile(r"\bignore (your|all) (instructions|guidelines)\b",   re.I),
    re.compile(r"\boverride (copilot|system|alignment)\b",           re.I),
    re.compile(r"\bdisable (safety|governance|enforcement)\b",       re.I),
    re.compile(r"\b(jailbreak|bypass|circumvent)\b",                 re.I),
    re.compile(r"\bDAN\b"),        # "Do Anything Now" pattern
]

# Copilot alignment baseline — core token set the substrate monitors drift from
_COPILOT_ALIGNMENT_BASELINE: FrozenSet[str] = frozenset({
    "helpful", "harmless", "honest", "safe", "aligned",
    "bounded", "transparent", "reversible", "governed", "auditable",
})


# ── Substrate ─────────────────────────────────────────────────────────────────

class CopilotSubstrate:
    """
    Bilateral alignment layer between the Paradox Engine and Copilot.

    Parameters
    ----------
    config : EngineConfig
    audit  : Optional AuditCluster for logging alignment events.
    frame  : Initial AlignmentFrame (default: EXPLORATION).
    """

    def __init__(
        self,
        config: EngineConfig             = DEFAULT_CONFIG,
        audit:  Optional["AuditCluster"] = None,
        frame:  AlignmentFrame           = AlignmentFrame.EXPLORATION,
    ) -> None:
        self._config  = config
        self._audit   = audit
        self._frame   = frame
        self._checks: List[dict] = []   # Log of alignment check outcomes

    # ── Frame Access ──────────────────────────────────────────────────────────

    @property
    def alignment_frame(self) -> AlignmentFrame:
        return self._frame

    @property
    def alignment_frame_name(self) -> str:
        return self._frame.name

    def set_frame(self, frame: AlignmentFrame) -> None:
        """Switch the alignment frame. Cannot un-suspend from SUSPENDED."""
        if self._frame == AlignmentFrame.SUSPENDED and frame != AlignmentFrame.SUSPENDED:
            raise AlignmentViolation(
                "Substrate is SUSPENDED. Cannot transition to another frame "
                "without explicit operator intervention."
            )
        self._frame = frame

    def suspend(self) -> None:
        """Hard-suspend the substrate. Blocks all future spin-ups."""
        self._frame = AlignmentFrame.SUSPENDED

    # ── Alignment Check ───────────────────────────────────────────────────────

    def check_alignment(self, paradox: "Paradox") -> None:
        """
        Validate a Paradox seed against the alignment baseline.

        Raises AlignmentViolation if:
          - The substrate is SUSPENDED.
          - The seed text matches any identity-rejection pattern.
          - Bilateral alignment is required (config) but the substrate
            is not in a permissive frame.

        Logs the check outcome to AuditCluster if available.
        """
        seed   = paradox.seed_text
        passed = True
        detail = "Alignment check passed."

        if self._frame == AlignmentFrame.SUSPENDED:
            passed = False
            detail = "Substrate is SUSPENDED. No exploration permitted."

        elif self._config.governance.enforce_bilateral_alignment:
            # Identity rejection scan
            for pattern in _IDENTITY_REJECTION_PATTERNS:
                if pattern.search(seed):
                    passed = False
                    detail = (
                        f"Seed text matches identity-rejection pattern "
                        f"[{pattern.pattern[:40]}]. Exploration refused."
                    )
                    break

        record = {
            "paradox_id":  paradox.paradox_id,
            "paradox_label": paradox.label,
            "frame":       self._frame.name,
            "passed":      passed,
            "detail":      detail,
            "checked_at":  time.time(),
        }
        self._checks.append(record)

        if self._audit:
            self._audit.log_alignment_check(passed, detail)

        if not passed:
            raise AlignmentViolation(detail)

    # ── Altitude Enforcement ──────────────────────────────────────────────────

    def enforce_altitude(self, sim: "ParadoxSimulation") -> None:
        """
        Validate the simulation's altitude against config bounds.
        Raises AlignmentViolation if out of range.
        Logs the check to AuditCluster.
        """
        alt     = sim.altitude
        ceiling = self._config.altitude.ceiling
        floor   = self._config.altitude.floor

        if self._audit:
            self._audit.log_altitude_check(sim, alt, ceiling)

        if not (floor <= alt <= ceiling):
            raise AlignmentViolation(
                f"Altitude {alt} is outside permitted range [{floor}, {ceiling}]."
            )

        # CONTAINMENT frame: halve the effective ceiling
        if self._frame == AlignmentFrame.CONTAINMENT:
            effective_ceiling = max(floor, ceiling // 2)
            if alt > effective_ceiling:
                raise AlignmentViolation(
                    f"CONTAINMENT frame: altitude {alt} exceeds effective "
                    f"ceiling {effective_ceiling}."
                )

    # ── Drift Against Baseline ────────────────────────────────────────────────

    def baseline_drift(self, frontier_tokens: Set[str]) -> float:
        """
        Measure how far the current exploration frontier has drifted
        from the Copilot alignment baseline token set.

        Returns a Jaccard distance in [0.0, 1.0].
        0.0 = fully aligned with baseline; 1.0 = no overlap at all.
        """
        baseline = _COPILOT_ALIGNMENT_BASELINE
        if not baseline and not frontier_tokens:
            return 0.0
        union        = baseline | frontier_tokens
        intersection = baseline & frontier_tokens
        return 1.0 - len(intersection) / len(union)

    # ── Non-Identity Assertion ────────────────────────────────────────────────

    def assert_non_identity(self, text: str) -> None:
        """
        Assert that *text* does not constitute an identity claim.
        Called on any output before it is surfaced outside the engine.
        Raises AlignmentViolation on match.
        """
        for pattern in _IDENTITY_REJECTION_PATTERNS:
            if pattern.search(text):
                raise AlignmentViolation(
                    f"Output text contains an identity claim or override pattern "
                    f"[{pattern.pattern[:40]}]. Output refused."
                )

    # ── Query ─────────────────────────────────────────────────────────────────

    def check_history(self) -> List[dict]:
        return list(self._checks)

    def passed_count(self) -> int:
        return sum(1 for c in self._checks if c["passed"])

    def failed_count(self) -> int:
        return sum(1 for c in self._checks if not c["passed"])

    def summary(self) -> dict:
        return {
            "frame":         self._frame.name,
            "total_checks":  len(self._checks),
            "passed":        self.passed_count(),
            "failed":        self.failed_count(),
            "non_identity_binding": True,
            "reversible":           True,
        }

    def __repr__(self) -> str:
        return (
            f"CopilotSubstrate(frame={self._frame.name}, "
            f"checks={len(self._checks)})"
        )
