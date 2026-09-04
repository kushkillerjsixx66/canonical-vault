"""Deterministic source audit for unsupported fixed evaluator scores."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .audit import SourceAuditResult
from .classifier import EpistemicState
from .finding import StumpyFinding
from .source_inspector import RepositorySourceInspector


@dataclass(frozen=True)
class ScoreHonestyObservation:
    assignments: tuple[str, ...]
    methods: tuple[str, ...]


def inspect_fixed_scores(source: str) -> ScoreHonestyObservation:
    assignments = tuple(re.findall(r"\bscore\s*=\s*([0-9]+(?:\.[0-9]+)?)", source))
    methods = tuple(re.findall(r"method\s*=\s*['\"]([^'\"]+)['\"]", source))
    return ScoreHonestyObservation(assignments=assignments, methods=methods)


def audit_score_honesty(*, repository_root: str, target: str, claim_id: str, evidence_id: str) -> SourceAuditResult:
    inspector = RepositorySourceInspector(repository_root)
    evidence = inspector.evidence(
        evidence_id=evidence_id,
        claim_id=claim_id,
        relative_path=target,
    )
    source = inspector.observe(target).content
    observation = inspect_fixed_scores(source)

    fixed = any(value in {"0.95", "0.9", "0.99", "1.0", "0.0"} for value in observation.assignments)
    if fixed:
        reason = "Fixed numeric score assignment observed in evaluator source; score is not demonstrably derived from runtime evidence."
        state = EpistemicState.FAIL
    else:
        reason = "No targeted fixed numeric score assignment observed by this source predicate."
        state = EpistemicState.PASS

    from .claims import ResolvedClaim
    claim = ResolvedClaim(
        claim_id=claim_id,
        constitutional_basis="STUMPY_AUDIT_SCHEMA.yaml: score honesty",
        requirement="Evaluator scores must be grounded in an explicit method and evidence basis.",
        target=target,
        expected_behavior="score derived from declared evaluation method and evidence",
        evidence=evidence,
    )
    return SourceAuditResult(claim=claim, state=state, reason=reason)


def finding_from_score_honesty_audit(result: SourceAuditResult, finding_id: str) -> StumpyFinding:
    severity = "HIGH" if result.state is EpistemicState.FAIL else "LOW"
    return StumpyFinding(
        finding_id=finding_id,
        domain="score_honesty",
        status=result.state.value,
        severity=severity,
        claim=result.claim.requirement,
        observed_state={"reason": result.reason},
        expected_state={"behavior": result.claim.expected_behavior},
        constitutional_basis=[result.claim.constitutional_basis],
        evidence_refs=[result.claim.evidence.evidence_id],
        source_refs=[result.claim.target],
        lineage_refs=[],
        evaluator_id="stumpy.score_honesty",
        evaluator_version="1.0.0",
        method="deterministic-fixed-score-source-audit",
        confidence=None if result.state is EpistemicState.UNKNOWN else 1.0,
        timestamp=result.claim.evidence.captured_at,
    )
