"""Declarative invariant-to-evidence audit matrix for Stumpy.

A matrix entry is an authorization to test one observable property. It is not
an assertion that the property is satisfied, nor does absence from the matrix
mean compliance.
"""

from __future__ import annotations

from dataclasses import dataclass

from .registry import AuditRule, StumpyAuditRegistry


INVARIANTS = (
    "coherence",
    "reversibility",
    "lineage_binding",
    "source_integrity",
    "score_honesty",
    "drift_accountability",
    "silence_as_state",
    "operator_boundary",
    "authority_hierarchy",
    "constraint_enforcement",
)


@dataclass(frozen=True)
class MatrixEntry:
    invariant: str
    rule: AuditRule
    evidence_type: str
    unknown_condition: str

    def validate(self) -> None:
        if self.invariant not in INVARIANTS:
            raise ValueError(f"unknown invariant: {self.invariant}")
        if not self.evidence_type:
            raise ValueError("evidence_type is required")
        if not self.unknown_condition:
            raise ValueError("unknown_condition is required")


CORE_AUDIT_MATRIX = (
    MatrixEntry(
        invariant="score_honesty",
        rule=AuditRule(
            rule_id="M-SCORE-001",
            domain="score_honesty",
            constitutional_basis="Score Honesty",
            requirement="Evaluator score must not be a fixed unsupported constant.",
            target="05_runtime/governance/engine.py",
            expected_behavior="score = 0.95",
            predicate="contains_exact_text",
            severity="HIGH",
        ),
        evidence_type="repository_source",
        unknown_condition="Source cannot be read or the predicate cannot establish whether the score is evidence-derived.",
    ),
    MatrixEntry(
        invariant="silence_as_state",
        rule=AuditRule(
            rule_id="M-SILENCE-001",
            domain="silence_as_state",
            constitutional_basis="Silence as State",
            requirement="The epistemic substrate explicitly represents UNKNOWN.",
            target="05_runtime/stumpy/classifier.py",
            expected_behavior="EpistemicState.UNKNOWN",
            predicate="contains_exact_text",
            severity="HIGH",
        ),
        evidence_type="repository_source",
        unknown_condition="Source does not expose an observable representation of UNKNOWN.",
    ),
    MatrixEntry(
        invariant="source_integrity",
        rule=AuditRule(
            rule_id="M-SOURCE-001",
            domain="source_integrity",
            constitutional_basis="Source Integrity",
            requirement="Source evidence carries a verifiable digest.",
            target="05_runtime/stumpy/source_inspector.py",
            expected_behavior="sha256",
            predicate="contains_exact_text",
            severity="HIGH",
        ),
        evidence_type="repository_source",
        unknown_condition="Digest acquisition or verification is not observable from the selected target.",
    ),
    MatrixEntry(
        invariant="operator_boundary",
        rule=AuditRule(
            rule_id="M-OPERATOR-001",
            domain="operator_boundary",
            constitutional_basis="Operator Boundary",
            requirement="Operator boundary must be represented by an explicit source-level control.",
            target="05_runtime/governance/engine.py",
            expected_behavior="operator",
            predicate="contains_exact_text",
            severity="MEDIUM",
        ),
        evidence_type="repository_source",
        unknown_condition="A source scan cannot establish semantic enforcement of operator authority.",
    ),
    MatrixEntry(
        invariant="reversibility",
        rule=AuditRule(
            rule_id="M-REVERSIBILITY-001",
            domain="reversibility",
            constitutional_basis="Reversibility",
            requirement="An existing lineage sequence cannot be overwritten by a later append.",
            target="03_vault_pipeline/vault_chain/vault_chain.py",
            expected_behavior="reversibility",
            predicate="behavioral_probe",
            severity="HIGH",
        ),
        evidence_type="runtime_behavior",
        unknown_condition="The isolated VaultChain behavioral probe cannot execute or cannot establish the required behavior.",
    ),
    MatrixEntry(
        invariant="constraint_enforcement",
        rule=AuditRule(
            rule_id="M-CONSTRAINT-001",
            domain="constraint_enforcement",
            constitutional_basis="Constraint Enforcement",
            requirement="An unsafe runtime state must produce an enforcement finding.",
            target="00_governance/stumpy/stumpy_enforcement_pipelines.py",
            expected_behavior="constraint_enforcement",
            predicate="behavioral_probe",
            severity="HIGH",
        ),
        evidence_type="runtime_behavior",
        unknown_condition="The isolated enforcement behavioral probe cannot execute or cannot establish the required behavior.",
    ),
)


def validate_matrix() -> None:
    for entry in CORE_AUDIT_MATRIX:
        entry.validate()


def registry_for_matrix(repository_root: str) -> StumpyAuditRegistry:
    validate_matrix()
    return StumpyAuditRegistry(repository_root, tuple(entry.rule for entry in CORE_AUDIT_MATRIX))
