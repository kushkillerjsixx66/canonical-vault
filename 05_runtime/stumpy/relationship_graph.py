"""Declarative relationship graph for cross-artifact Stumpy audits.

Graph edges authorize relational observations. An edge never implies that the
relationship is semantically valid; that conclusion must come from evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


RELATION_TYPES = (
    "declares",
    "implements",
    "constrains",
    "derives_from",
    "authorizes",
    "audits",
)


@dataclass(frozen=True)
class RelationshipEdge:
    edge_id: str
    relation: str
    source: str
    target: str
    invariant: str
    evidence_required: str

    def validate(self) -> None:
        if self.relation not in RELATION_TYPES:
            raise ValueError(f"unknown relationship type: {self.relation}")
        if not all((self.edge_id, self.source, self.target, self.invariant, self.evidence_required)):
            raise ValueError("relationship edge is incomplete")


CORE_RELATIONSHIP_GRAPH = (
    RelationshipEdge(
        edge_id="REL-LINEAGE-001",
        relation="derives_from",
        source="05_runtime/stumpy/finding.py",
        target="05_runtime/stumpy/source_inspector.py",
        invariant="lineage_binding",
        evidence_required="finding evidence reference resolves to source acquisition record",
    ),
    RelationshipEdge(
        edge_id="REL-SOURCE-001",
        relation="audits",
        source="05_runtime/stumpy/registry.py",
        target="05_runtime/stumpy/source_inspector.py",
        invariant="source_integrity",
        evidence_required="registered audit rule produces an evidence record from the declared target",
    ),
    RelationshipEdge(
        edge_id="REL-GOV-001",
        relation="implements",
        source="05_runtime/governance/engine.py",
        target="00_governance",
        invariant="constraint_enforcement",
        evidence_required="implementation can be mapped to a declared governance requirement",
    ),
    RelationshipEdge(
        edge_id="REL-EPI-001",
        relation="implements",
        source="05_runtime/stumpy/classifier.py",
        target="01_epistemic_substrate",
        invariant="coherence",
        evidence_required="epistemic states correspond to declared substrate semantics",
    ),
)


def validate_graph(edges: Iterable[RelationshipEdge] = CORE_RELATIONSHIP_GRAPH) -> None:
    for edge in edges:
        edge.validate()
