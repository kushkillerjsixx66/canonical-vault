"""Bounded, explicit audit report aggregation for Stumpy."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import uuid4

from .audit_matrix import INVARIANTS, CORE_AUDIT_MATRIX
from .classifier import EpistemicState
from .finding import StumpyFinding


@dataclass(frozen=True)
class StumpyAuditReport:
    run_id: str
    repository_revision: str
    evaluator_id: str
    evaluator_version: str
    started_at: str
    completed_at: str
    rules_evaluated: int
    findings: tuple[StumpyFinding, ...]
    rules_not_evaluated: tuple[str, ...] = field(default_factory=tuple)
    evaluated_invariants: tuple[str, ...] = field(default_factory=tuple)
    unevaluated_invariants: tuple[str, ...] = field(default_factory=tuple)

    @property
    def counts(self) -> dict[str, int]:
        counts = {state.value: 0 for state in EpistemicState}
        for finding in self.findings:
            counts[finding.status] = counts.get(finding.status, 0) + 1
        return counts

    @property
    def coverage_ratio(self) -> float:
        return len(self.evaluated_invariants) / len(INVARIANTS) if INVARIANTS else 0.0

    @property
    def overall_state(self) -> str:
        counts = self.counts
        if counts.get(EpistemicState.FAIL.value, 0):
            return EpistemicState.FAIL.value
        if counts.get(EpistemicState.UNKNOWN.value, 0) or self.rules_not_evaluated or self.unevaluated_invariants:
            return EpistemicState.UNKNOWN.value
        if counts.get(EpistemicState.ABSTAIN.value, 0):
            return EpistemicState.ABSTAIN.value
        return EpistemicState.PASS.value

    def validate(self) -> None:
        if not self.run_id or not self.repository_revision:
            raise ValueError("report identity is incomplete")
        if self.rules_evaluated < len(self.findings):
            raise ValueError("evaluated rule count cannot be below finding count")
        if set(self.evaluated_invariants) & set(self.unevaluated_invariants):
            raise ValueError("invariant cannot be both evaluated and unevaluated")
        if set(self.evaluated_invariants) | set(self.unevaluated_invariants) != set(INVARIANTS):
            raise ValueError("report must account for every canonical invariant")
        for finding in self.findings:
            finding.validate()

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "run_id": self.run_id,
            "repository_revision": self.repository_revision,
            "evaluator": {"id": self.evaluator_id, "version": self.evaluator_version},
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "rules_evaluated": self.rules_evaluated,
            "rules_not_evaluated": list(self.rules_not_evaluated),
            "coverage": {
                "total_invariants": len(INVARIANTS),
                "evaluated_invariants": list(self.evaluated_invariants),
                "unevaluated_invariants": list(self.unevaluated_invariants),
                "ratio": self.coverage_ratio,
            },
            "counts": self.counts,
            "overall_state": self.overall_state,
            "findings": [finding.to_dict() for finding in self.findings],
        }


def build_report(
    findings: Iterable[StumpyFinding],
    *,
    repository_revision: str,
    evaluator_id: str = "stumpy.audit_registry",
    evaluator_version: str = "1.0.0",
    rules_evaluated: int | None = None,
    rules_not_evaluated: Iterable[str] = (),
    evaluated_invariants: Iterable[str] | None = None,
    unevaluated_invariants: Iterable[str] | None = None,
) -> StumpyAuditReport:
    now = datetime.now(timezone.utc).isoformat()
    finding_tuple = tuple(findings)
    if evaluated_invariants is None:
        evaluated_invariants = tuple(dict.fromkeys(entry.invariant for entry in CORE_AUDIT_MATRIX))
    evaluated = tuple(dict.fromkeys(evaluated_invariants))
    if unevaluated_invariants is None:
        unevaluated_invariants = tuple(invariant for invariant in INVARIANTS if invariant not in evaluated)
    report = StumpyAuditReport(
        run_id=f"STUMPY-RUN-{uuid4().hex[:12]}",
        repository_revision=repository_revision,
        evaluator_id=evaluator_id,
        evaluator_version=evaluator_version,
        started_at=now,
        completed_at=now,
        rules_evaluated=rules_evaluated if rules_evaluated is not None else len(finding_tuple),
        findings=finding_tuple,
        rules_not_evaluated=tuple(rules_not_evaluated),
        evaluated_invariants=evaluated,
        unevaluated_invariants=tuple(unevaluated_invariants),
    )
    report.validate()
    return report
