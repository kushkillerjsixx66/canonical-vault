"""Conservative comparison of declared behavior against source evidence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

from .claims import ResolvedClaim
from .classifier import EpistemicState, classify_evidence


class ComparisonState(str, Enum):
    MATCH = "MATCH"
    CONTRADICTION = "CONTRADICTION"
    NOT_OBSERVABLE = "NOT_OBSERVABLE"


@dataclass(frozen=True)
class Comparison:
    state: ComparisonState
    observed: str
    detail: str
    epistemic_state: EpistemicState


class SourceClaimComparator:
    """Compare simple, explicitly declared source predicates.

    The comparator is intentionally conservative. It only recognizes a small
    set of predicates whose observation can be justified directly from source.
    Unknown predicates produce NOT_OBSERVABLE rather than guessed compliance.
    """

    def compare(self, claim: ResolvedClaim) -> Comparison:
        source = claim.evidence.payload
        if not claim.evidence.verify_digest():
            return Comparison(
                ComparisonState.NOT_OBSERVABLE,
                "evidence digest invalid",
                "source evidence integrity could not be established",
                EpistemicState.UNKNOWN,
            )

        text = source.get("content") if isinstance(source, dict) else None
        if text is None:
            return Comparison(
                ComparisonState.NOT_OBSERVABLE,
                "source content not captured",
                "source metadata alone cannot establish implementation behavior",
                EpistemicState.UNKNOWN,
            )

        expected = claim.expected_behavior.strip().lower()
        patterns = {
            "contains:explicit_contradiction": r"explicit_contradiction",
            "contains:corrupt_state": r"corrupt_state",
            "contains:lineage": r"lineage",
            "contains:reversible": r"reversible",
        }
        if expected not in patterns:
            return Comparison(
                ComparisonState.NOT_OBSERVABLE,
                "unsupported predicate",
                f"comparator does not recognize predicate: {claim.expected_behavior}",
                EpistemicState.UNKNOWN,
            )

        matched = re.search(patterns[expected], text, re.IGNORECASE) is not None
        if matched:
            return Comparison(
                ComparisonState.MATCH,
                expected,
                "declared source predicate observed",
                classify_evidence([claim.evidence], observed_conformance=True),
            )
        return Comparison(
            ComparisonState.CONTRADICTION,
            expected,
            "declared source predicate not observed",
            classify_evidence([claim.evidence], observed_conformance=False),
        )
