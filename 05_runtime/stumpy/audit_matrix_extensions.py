"""Additional matrix entries for foundational invariants."""

from __future__ import annotations

from .audit_matrix import MatrixEntry
from .registry import AuditRule


FOUNDATIONAL_AUDIT_MATRIX = (
    MatrixEntry(
        invariant="lineage_binding",
        rule=AuditRule(
            rule_id="M-LINEAGE-001",
            domain="lineage_binding",
            constitutional_basis="Lineage Binding",
            requirement="Audit evidence and findings expose an explicit lineage reference.",
            target="05_runtime/stumpy/finding.py",
            expected_behavior="lineage_refs",
            predicate="contains_exact_text",
            severity="HIGH",
        ),
        evidence_type="repository_source",
        unknown_condition="A source marker alone cannot establish that lineage is preserved correctly through every transformation.",
    ),
    MatrixEntry(
        invariant="reversibility",
        rule=AuditRule(
            rule_id="M-REVERSIBILITY-001",
            domain="reversibility",
            constitutional_basis="Reversibility",
            requirement="The audit substrate exposes an explicit reversible-state or snapshot concept.",
            target="05_runtime/stumpy/report.py",
            expected_behavior="run_id",
            predicate="contains_exact_text",
            severity="MEDIUM",
        ),
        evidence_type="repository_source",
        unknown_condition="Audit-run identity does not by itself prove that repository or system state can be restored.",
    ),
)
