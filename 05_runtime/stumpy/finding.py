"""Schema-aligned finding construction for Stumpy."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .audit import BehavioralAuditResult, SourceAuditResult
from .classifier import EpistemicState


@dataclass(frozen=True)
class StumpyFinding:
    finding_id: str
    domain: str
    status: str
    severity: str
    claim: str
    observed_state: dict[str, Any]
    expected_state: dict[str, Any]
    constitutional_basis: list[str]
    evidence_refs: list[str]
    source_refs: list[str]
    lineage_refs: list[str]
    evaluator_id: str
    evaluator_version: str
    method: str
    confidence: float | None
    timestamp: str
    remediation_refs: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.finding_id or not self.domain or not self.status:
            raise ValueError("finding identity is incomplete")
        if self.status in {EpistemicState.PASS.value, EpistemicState.FAIL.value} and not self.evidence_refs:
            raise ValueError("PASS/FAIL finding must be evidence-bound")
        if not self.evaluator_id or not self.evaluator_version or not self.method:
            raise ValueError("evaluator identity and method are required")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


def finding_from_source_audit(
    result: SourceAuditResult,
    *,
    finding_id: str,
    domain: str,
    severity: str,
    evaluator_id: str = "stumpy.source_audit",
    evaluator_version: str = "1.0.0",
) -> StumpyFinding:
    evidence = result.claim.evidence
    finding = StumpyFinding(
        finding_id=finding_id,
        domain=domain,
        status=result.state.value,
        severity=severity,
        claim=result.claim.requirement,
        observed_state={"reason": result.reason},
        expected_state={"behavior": result.claim.expected_behavior},
        constitutional_basis=[result.claim.constitutional_basis],
        evidence_refs=[evidence.evidence_id],
        source_refs=[result.claim.target],
        lineage_refs=[evidence.lineage_ref] if evidence.lineage_ref else [],
        evaluator_id=evaluator_id,
        evaluator_version=evaluator_version,
        method="repository-source-audit",
        confidence=1.0 if result.state in {EpistemicState.PASS, EpistemicState.FAIL} else None,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    finding.validate()
    return finding


def finding_from_behavioral_audit(
    result: BehavioralAuditResult,
    *,
    finding_id: str,
    domain: str,
    severity: str,
) -> StumpyFinding:
    evidence = result.evidence
    finding = StumpyFinding(
        finding_id=finding_id,
        domain=domain,
        status=result.state.value,
        severity=severity,
        claim=result.claim.requirement,
        observed_state={"reason": result.reason, **dict(evidence.payload)},
        expected_state={"behavioral_probe": result.claim.expected_behavior},
        constitutional_basis=[result.claim.constitutional_basis],
        evidence_refs=[evidence.evidence_id],
        source_refs=[result.claim.target],
        lineage_refs=[evidence.lineage_ref] if evidence.lineage_ref else [],
        evaluator_id=evidence.evaluator_id,
        evaluator_version=evidence.evaluator_version,
        method=evidence.method,
        confidence=1.0 if result.state in {EpistemicState.PASS, EpistemicState.FAIL} else None,
        timestamp=evidence.captured_at,
    )
    finding.validate()
    return finding
