"""Claim and finding primitives for the Stumpy audit boundary."""

from dataclasses import dataclass, field
from typing import Optional, Tuple

from .classifier import EpistemicState
from .evidence import EvidenceRecord
from .source_inspector import RepositorySourceInspector


@dataclass(frozen=True)
class AuditClaim:
    claim_id: str
    constitutional_basis: str
    requirement: str
    target: str
    expected_behavior: str


@dataclass(frozen=True)
class AuditFinding:
    finding_id: str
    claim: AuditClaim
    state: EpistemicState
    severity: str
    method: str
    evidence: Tuple[EvidenceRecord, ...] = field(default_factory=tuple)
    evaluator_id: str = "stumpy"
    evaluator_version: str = "0.1.0"
    limitation: Optional[str] = None

    def validate(self) -> None:
        """Reject findings that violate the evidence-first contract."""
        if self.state in {EpistemicState.PASS, EpistemicState.FAIL} and not self.evidence:
            raise ValueError("PASS/FAIL findings require evidence")
        if self.state is EpistemicState.PASS and all(e.is_assertion_only() for e in self.evidence):
            raise ValueError("assertion-only evidence cannot establish PASS")


@dataclass(frozen=True)
class ResolvedClaim:
    claim_id: str
    constitutional_basis: str
    requirement: str
    target: str
    expected_behavior: str
    evidence: EvidenceRecord


class RepositoryClaimResolver:
    """Bind a declared requirement to exact repository source evidence.

    Resolution never implies compliance. It only establishes the source
    evidence required for a later comparison.
    """

    def __init__(self, inspector: RepositorySourceInspector):
        self.inspector = inspector

    def resolve_source_claim(
        self,
        *,
        claim_id: str,
        constitutional_basis: str,
        requirement: str,
        target: str,
        expected_behavior: str,
        evidence_id: str,
    ) -> ResolvedClaim:
        evidence = self.inspector.evidence(
            evidence_id=evidence_id,
            claim_id=claim_id,
            relative_path=target,
        )
        return ResolvedClaim(
            claim_id=claim_id,
            constitutional_basis=constitutional_basis,
            requirement=requirement,
            target=target,
            expected_behavior=expected_behavior,
            evidence=evidence,
        )
