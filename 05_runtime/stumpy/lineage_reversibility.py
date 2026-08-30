"""Bounded source predicates for lineage binding and reversibility.

These predicates establish only observable implementation facts. They do not
claim semantic compliance merely because a matching symbol exists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .classifier import EpistemicState


@dataclass(frozen=True)
class StructuralObservation:
    target: str
    matched_tokens: tuple[str, ...]
    state: EpistemicState
    reason: str


def _observe(source: str, target: str, tokens: tuple[str, ...], requirement: str) -> StructuralObservation:
    matched = tuple(token for token in tokens if re.search(re.escape(token), source))
    if matched:
        return StructuralObservation(
            target=target,
            matched_tokens=matched,
            state=EpistemicState.PASS,
            reason=f"Observed source-level markers for {requirement}: {', '.join(matched)}",
        )
    return StructuralObservation(
        target=target,
        matched_tokens=(),
        state=EpistemicState.UNKNOWN,
        reason=f"No declared source-level marker established {requirement}; semantic compliance remains unknown.",
    )


def observe_lineage_binding(source: str, target: str) -> StructuralObservation:
    return _observe(
        source,
        target,
        ("lineage", "lineage_ref", "lineage_refs", "evidence_id"),
        "lineage binding",
    )


def observe_reversibility(source: str, target: str) -> StructuralObservation:
    return _observe(
        source,
        target,
        ("reversible", "reversibility", "rollback", "snapshot"),
        "reversibility",
    )
