"""Cross-artifact relational evidence primitives for Stumpy.

A relationship audit can establish that declared artifacts reference or
contain expected structural markers. It must not promote structural presence
to semantic compliance without stronger evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .classifier import EpistemicState


@dataclass(frozen=True)
class RelationalObservation:
    relation_id: str
    left_target: str
    right_target: str
    relation: str
    evidence: tuple[str, ...]
    state: EpistemicState
    reason: str

    def validate(self) -> None:
        if not self.relation_id or not self.left_target or not self.right_target:
            raise ValueError("relational observation identity is incomplete")
        if not self.relation:
            raise ValueError("relation is required")


def observe_declared_reference(
    repository_root: str,
    *,
    relation_id: str,
    left_target: str,
    right_target: str,
    tokens: tuple[str, ...],
) -> RelationalObservation:
    left = Path(repository_root, left_target)
    right = Path(repository_root, right_target)
    if not left.is_file() or not right.is_file():
        return RelationalObservation(
            relation_id=relation_id,
            left_target=left_target,
            right_target=right_target,
            relation="declared-reference",
            evidence=(),
            state=EpistemicState.UNKNOWN,
            reason="One or both relationship endpoints are unavailable; relationship cannot be established.",
        )

    source = left.read_text(encoding="utf-8")
    matched = tuple(token for token in tokens if token in source)
    if matched:
        state = EpistemicState.PASS
        reason = f"Observed declared-reference markers: {', '.join(matched)}"
    else:
        state = EpistemicState.UNKNOWN
        reason = "No declared-reference marker observed; semantic relationship remains unknown."

    observation = RelationalObservation(
        relation_id=relation_id,
        left_target=left_target,
        right_target=right_target,
        relation="declared-reference",
        evidence=matched,
        state=state,
        reason=reason,
    )
    observation.validate()
    return observation
