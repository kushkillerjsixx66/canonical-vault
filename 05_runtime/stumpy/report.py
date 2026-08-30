"""Bounded, explicit audit report aggregation for Stumpy."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import uuid4

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

    @property
    def counts(self) -> dict[str, int]:
        counts = {state.value: 0 for state in EpistemicState}
        for finding in self.findings:
            counts[finding.status] = counts.get(finding.status, 0) + 1
        return counts

    @property
    def overall_state(self) -> str:
        counts = self.counts
        if counts.get(EpistemicState.FAIL.value, 0):
            return EpistemicState.FAIL.value
        if counts.get(EpistemicState.UNKNOWN.value, 0) or self.rules_not_evaluated:
            return EpistemicState.UNKNOWN.value
        if counts.get(EpistemicState.ABSTAIN.value, 0):
            return EpistemicState.ABSTAIN.value
        return EpistemicState.PASS.value

    def validate(self) -> None:
        if not self.run_id or not self.repository_revision:
            raise ValueError("report identity is incomplete")
        if self.rules_evaluated < len(self.findings):
            raise ValueError("evaluated rule count cannot be below finding count")
        for finding in self.findings:
            finding.validate()

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "run_id": self.run_id,
            "repository_revision": self.repository_revision,
            "evaluator": {
                "id": self.evaluator_id,
                "version": self.evaluator_version,
            },
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "rules_evaluated": self.rules_evaluated,
            "rules_not_evaluated": list(self.rules_not_evaluated),
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
) -> StumpyAuditReport:
    now = datetime.now(timezone.utc).isoformat()
    finding_tuple = tuple(findings)
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
    )
    report.validate()
    return report
