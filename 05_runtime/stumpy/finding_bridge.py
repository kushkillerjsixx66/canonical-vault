"""Convert relational evidence into canonical Stumpy findings."""

from __future__ import annotations

from datetime import datetime, timezone

from .evidence_contracts import RelationshipEvidence
from .finding import StumpyFinding


def finding_from_relationship(
    evidence: RelationshipEvidence,
    *,
    invariant: str,
    source_target: str,
    target_target: str,
    evaluator_id: str = "stumpy.relationship_contract",
    evaluator_version: str = "1.0.0",
) -> StumpyFinding:
    evidence_id = f"REL-EVID-{evidence.edge_id}"
    finding = StumpyFinding(
        finding_id=f"REL-FIND-{evidence.edge_id}",
        domain=invariant,
        status=evidence.state.value,
        severity="MEDIUM" if evidence.state.value != "FAIL" else "HIGH",
        claim=f"Relationship '{evidence.relation}' between {source_target} and {target_target} was structurally evaluated.",
        observed_state={
            "relationship": evidence.relation,
            "evidence": list(evidence.evidence),
        },
        expected_state={"relationship": evidence.relation},
        constitutional_basis=[invariant],
        evidence_refs=[evidence_id],
        source_refs=[source_target, target_target],
        lineage_refs=[evidence.edge_id],
        evaluator_id=evaluator_id,
        evaluator_version=evaluator_version,
        method="relationship-specific evidence contract",
        confidence=None if evidence.state.value == "UNKNOWN" else 0.8,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    return finding
