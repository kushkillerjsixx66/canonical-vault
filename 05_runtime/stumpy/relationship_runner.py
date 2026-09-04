"""Execute declared Stumpy relationship edges against repository evidence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .classifier import EpistemicState
from .evidence_contracts import RelationshipEvidence, evaluate_relationship
from .relationship_graph import CORE_RELATIONSHIP_GRAPH, RelationshipEdge, validate_graph


@dataclass(frozen=True)
class RelationshipRun:
    edges_evaluated: int
    observations: tuple[RelationshipEvidence, ...]

    @property
    def counts(self) -> dict[str, int]:
        return {state.value: sum(o.state == state for o in self.observations) for state in EpistemicState}


def run_relationship_graph(repository_root: str, edges=CORE_RELATIONSHIP_GRAPH) -> RelationshipRun:
    edges = tuple(edges)
    validate_graph(edges)
    observations = []
    for edge in edges:
        source_path = Path(repository_root, edge.source)
        target_path = Path(repository_root, edge.target)
        if not source_path.is_file() or not target_path.is_file():
            observations.append(RelationshipEvidence(
                edge_id=edge.edge_id,
                relation=edge.relation,
                state=EpistemicState.UNKNOWN,
                evidence=(),
                reason="One or both relationship endpoints are unavailable; relationship cannot be established.",
            ))
            continue
        source = source_path.read_text(encoding="utf-8")
        observations.append(evaluate_relationship(edge, source, target_path.read_text(encoding="utf-8")))
    return RelationshipRun(edges_evaluated=len(edges), observations=tuple(observations))
