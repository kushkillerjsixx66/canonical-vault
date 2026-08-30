"""Evidence contracts for executable Stumpy relationship audits."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .classifier import EpistemicState
from .relationship_graph import RelationshipEdge


@dataclass(frozen=True)
class RelationshipEvidence:
    edge_id: str
    relation: str
    state: EpistemicState
    evidence: tuple[str, ...]
    reason: str

    def validate(self) -> None:
        if not self.edge_id or not self.relation:
            raise ValueError("relationship evidence identity is incomplete")


def _marker_contract(edge: RelationshipEdge, source: str) -> RelationshipEvidence:
    markers = (edge.relation, edge.invariant)
    matched = tuple(marker for marker in markers if marker in source)
    if matched:
        return RelationshipEvidence(
            edge_id=edge.edge_id,
            relation=edge.relation,
            state=EpistemicState.PASS,
            evidence=matched,
            reason="Declared relationship markers observed in source; semantic validity remains unproven.",
        )
    return RelationshipEvidence(
        edge_id=edge.edge_id,
        relation=edge.relation,
        state=EpistemicState.UNKNOWN,
        evidence=(),
        reason="No relationship marker established the declared edge from source evidence.",
    )


CONTRACTS: dict[str, Callable[[RelationshipEdge, str], RelationshipEvidence]] = {
    "declares": _marker_contract,
    "implements": _marker_contract,
    "constrains": _marker_contract,
    "derives_from": _marker_contract,
    "authorizes": _marker_contract,
    "audits": _marker_contract,
}


def evaluate_relationship(edge: RelationshipEdge, source: str) -> RelationshipEvidence:
    try:
        evaluator = CONTRACTS[edge.relation]
    except KeyError as exc:
        raise ValueError(f"no evidence contract for relationship: {edge.relation}") from exc
    evidence = evaluator(edge, source)
    evidence.validate()
    return evidence
