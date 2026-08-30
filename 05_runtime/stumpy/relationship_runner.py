"""Execute declared Stumpy relationship edges against repository evidence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .classifier import EpistemicState
from .relationship_graph import CORE_RELATIONSHIP_GRAPH, RelationshipEdge, validate_graph
from .relational import RelationalObservation, observe_declared_reference


@dataclass(frozen=True)
class RelationshipRun:
    edges_evaluated: int
    observations: tuple[RelationalObservation, ...]

    @property
    def counts(self) -> dict[str, int]:
        return {state.value: sum(o.state == state for o in self.observations) for state in EpistemicState}


def _tokens_for(edge: RelationshipEdge) -> tuple[str, ...]:
    source_name = Path(edge.target).stem
    return (source_name, edge.relation, edge.invariant)


def run_relationship_graph(repository_root: str, edges=CORE_RELATIONSHIP_GRAPH) -> RelationshipRun:
    validate_graph(edges)
    observations = tuple(
        observe_declared_reference(
            repository_root,
            relation_id=edge.edge_id,
            left_target=edge.source,
            right_target=edge.target,
            tokens=_tokens_for(edge),
        )
        for edge in edges
    )
    return RelationshipRun(edges_evaluated=len(tuple(edges)), observations=observations)
