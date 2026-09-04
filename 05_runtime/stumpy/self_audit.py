"""Known-issue self-audit for Stumpy.

This module deliberately audits a source-level governance claim using explicit
source predicates. It does not silently infer semantic equivalence.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .audit import SourceAuditResult, audit_source_for_predicate
from .classifier import EpistemicState


@dataclass(frozen=True)
class SelfAuditReport:
    audit_id: str
    results: tuple[SourceAuditResult, ...]

    @property
    def state(self) -> EpistemicState:
        states = {result.state for result in self.results}
        if EpistemicState.FAIL in states:
            return EpistemicState.FAIL
        if EpistemicState.UNKNOWN in states:
            return EpistemicState.UNKNOWN
        return EpistemicState.PASS


def audit_g1_score_honesty(repository_root: str | Path) -> SelfAuditReport:
    """Audit whether G1 source contains a literal fixed score assignment.

    This is a deliberately narrow source-level probe. It establishes that a
    fixed score exists, not that the score is semantically invalid by itself.
    The constitutional interpretation remains a separate claim.
    """
    root = str(repository_root)
    result = audit_source_for_predicate(
        repository_root=root,
        claim_id="CLAIM-G1-SCORE-001",
        constitutional_basis="STUMPY_AUDIT_SCHEMA.yaml",
        requirement="G1 score calculation must be evidence-grounded and not an unsupported fixed default",
        target="05_runtime/governance/engine.py",
        expected_behavior="score = 0.95",
        predicate="contains_exact_text",
        evidence_id="EVID-G1-SCORE-001",
    )
    return SelfAuditReport(audit_id="STUMPY-SELF-G1-001", results=(result,))
