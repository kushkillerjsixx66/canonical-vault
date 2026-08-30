"""Relationship-specific evidence contracts for Stumpy.

Contracts acquire only observable evidence. A PASS means the contract's
structural condition was observed; it is not a semantic compliance verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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


def _unknown(edge: RelationshipEdge, reason: str) -> RelationshipEvidence:
    return RelationshipEvidence(edge.edge_id, edge.relation, EpistemicState.UNKNOWN, (), reason)


def _contains(source: str, markers: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(marker for marker in markers if marker in source)


def _derives_from(edge: RelationshipEdge, source: str, target: str) -> RelationshipEvidence:
    markers = _contains(source, ("evidence_refs", "source_refs", "lineage_refs"))
    if not markers:
        return _unknown(edge, "No source/evidence lineage reference observed in the declared source artifact.")
    return RelationshipEvidence(edge.edge_id, edge.relation, EpistemicState.PASS, markers,
                                "Observed explicit evidence/lineage reference fields; reference resolution remains a separate claim.")


def _audits(edge: RelationshipEdge, source: str, target: str) -> RelationshipEvidence:
    markers = _contains(source, ("run", "registry", "evidence"))
    if not markers:
        return _unknown(edge, "No observable audit/acquisition marker found in the source artifact.")
    return RelationshipEvidence(edge.edge_id, edge.relation, EpistemicState.PASS, markers,
                                "Observed audit/acquisition markers; invocation semantics remain unproven.")


def _implements(edge: RelationshipEdge, source: str, target: str) -> RelationshipEvidence:
    markers = _contains(source, ("requirement", "constraint", "invariant", "implements"))
    if not markers:
        return _unknown(edge, "No implementation-to-requirement marker observed in source evidence.")
    return RelationshipEvidence(edge.edge_id, edge.relation, EpistemicState.PASS, markers,
                                "Observed implementation/requirement markers; semantic enforcement remains unproven.")


def _constrains(edge: RelationshipEdge, source: str, target: str) -> RelationshipEvidence:
    markers = _contains(source, ("constraint", "enforce", "validate", "guard"))
    if not markers:
        return _unknown(edge, "No observable constraint/enforcement marker found.")
    return RelationshipEvidence(edge.edge_id, edge.relation, EpistemicState.PASS, markers,
                                "Observed constraint/enforcement markers; runtime enforcement remains unproven.")


def _authorizes(edge: RelationshipEdge, source: str, target: str) -> RelationshipEvidence:
    markers = _contains(source, ("authorize", "authority", "operator", "permission"))
    if not markers:
        return _unknown(edge, "No observable authority/authorization marker found.")
    return RelationshipEvidence(edge.edge_id, edge.relation, EpistemicState.PASS, markers,
                                "Observed authority markers; effective authorization semantics remain unproven.")


def _declares(edge: RelationshipEdge, source: str, target: str) -> RelationshipEvidence:
    target_name = Path(target).stem
    markers = _contains(source, (target_name, edge.invariant, "requirement"))
    if not markers:
        return _unknown(edge, "No declaration marker connecting source to target was observed.")
    return RelationshipEvidence(edge.edge_id, edge.relation, EpistemicState.PASS, markers,
                                "Observed declaration markers; declaration correctness remains unproven.")


CONTRACTS = {
    "declares": _declares,
    "implements": _implements,
    "constrains": _constrains,
    "derives_from": _derives_from,
    "authorizes": _authorizes,
    "audits": _audits,
}


def evaluate_relationship(edge: RelationshipEdge, source: str, target: str = "") -> RelationshipEvidence:
    try:
        evaluator = CONTRACTS[edge.relation]
    except KeyError as exc:
        raise ValueError(f"no evidence contract for relationship: {edge.relation}") from exc
    evidence = evaluator(edge, source, target)
    evidence.validate()
    return evidence
