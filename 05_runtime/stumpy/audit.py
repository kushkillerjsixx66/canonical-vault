"""End-to-end source audit orchestration for Stumpy."""

from __future__ import annotations

from dataclasses import dataclass

from .claims import RepositoryClaimResolver, ResolvedClaim
from .classifier import EpistemicState
from .source_inspector import RepositorySourceInspector


@dataclass(frozen=True)
class SourceAuditResult:
    claim: ResolvedClaim
    state: EpistemicState
    reason: str


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
    """Acquire source evidence and evaluate one explicit predicate.

    Unknown predicates produce UNKNOWN rather than an inferred judgment.
    """
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
        observed = f"class {expected_behavior}(" in source
    else:
        return SourceAuditResult(claim, EpistemicState.UNKNOWN, "unsupported predicate")

    if observed:
        return SourceAuditResult(claim, EpistemicState.PASS, "declared source predicate matched")
    return SourceAuditResult(claim, EpistemicState.FAIL, "declared source predicate contradicted")
