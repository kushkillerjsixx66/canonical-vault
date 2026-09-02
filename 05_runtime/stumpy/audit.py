"""End-to-end audit orchestration for Stumpy."""

from __future__ import annotations

from dataclasses import dataclass

from .behavioral import run_behavioral_probe
from .claims import AuditClaim, RepositoryClaimResolver, ResolvedClaim
from .classifier import EpistemicState
from .evidence import EvidenceKind, EvidenceRecord
from .source_inspector import RepositorySourceInspector


@dataclass(frozen=True)
class SourceAuditResult:
    claim: ResolvedClaim
    state: EpistemicState
    reason: str


@dataclass(frozen=True)
class BehavioralAuditResult:
    claim: AuditClaim
    state: EpistemicState
    reason: str
    evidence: EvidenceRecord


def audit_source_for_predicate(
    *,
    repository_root: str,
    claim_id: str,
    constitutional_basis: str,
    requirement: str,
    target: str,
    expected_behavior: str,
    predicate: str,
    evidence_id: str,
) -> SourceAuditResult:
    """Acquire source evidence and evaluate one explicit predicate."""
    inspector = RepositorySourceInspector(repository_root)
    resolver = RepositoryClaimResolver(inspector)
    claim = resolver.resolve_source_claim(
        claim_id=claim_id,
        constitutional_basis=constitutional_basis,
        requirement=requirement,
        target=target,
        expected_behavior=expected_behavior,
        evidence_id=evidence_id,
    )
    source = inspector.observe(target).content
    if predicate == "contains_exact_text":
        observed = expected_behavior in source
    elif predicate == "contains_function":
        observed = f"def {expected_behavior}(" in source
    elif predicate == "contains_class":
        observed = f"class {expected_behavior}" in source
    else:
        return SourceAuditResult(claim, EpistemicState.UNKNOWN, "unsupported predicate")
    if observed:
        return SourceAuditResult(claim, EpistemicState.PASS, "declared source predicate matched")
    return SourceAuditResult(claim, EpistemicState.FAIL, "declared source predicate contradicted")


def audit_behavioral_probe(
    *,
    repository_root: str,
    claim_id: str,
    constitutional_basis: str,
    requirement: str,
    target: str,
    probe: str,
    evidence_id: str,
    evaluator_id: str = "stumpy.behavioral_audit",
    evaluator_version: str = "1.0.0",
) -> BehavioralAuditResult:
    """Execute a registered runtime probe and bind its receipt to a claim."""
    try:
        observed, reason = run_behavioral_probe(repository_root, probe)
        state = EpistemicState.PASS if observed else EpistemicState.FAIL
    except Exception as exc:
        observed = None
        reason = f"probe execution failed: {type(exc).__name__}: {exc}"
        state = EpistemicState.UNKNOWN
    evidence = EvidenceRecord.create(
        evidence_id=evidence_id,
        claim_id=claim_id,
        kind=EvidenceKind.RUNTIME,
        target=target,
        method="isolated-behavioral-probe",
        evaluator_id=evaluator_id,
        evaluator_version=evaluator_version,
        payload={"probe": probe, "observed": observed, "reason": reason},
        source_ref=target,
    )
    claim = AuditClaim(
        claim_id=claim_id,
        constitutional_basis=constitutional_basis,
        requirement=requirement,
        target=target,
        expected_behavior=probe,
    )
    return BehavioralAuditResult(claim, state, reason, evidence)
