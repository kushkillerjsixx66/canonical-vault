"""Evidence-to-state classification for Stumpy."""

from enum import Enum
from typing import Iterable

from .evidence import EvidenceRecord


class EpistemicState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    ABSTAIN = "ABSTAIN"
    SILENCE = "SILENCE"
    DECLARED_UNENFORCED = "DECLARED_UNENFORCED"


def classify_evidence(
    evidence: Iterable[EvidenceRecord],
    *,
    observed_conformance: bool | None,
    explicitly_unenforced: bool = False,
    explicit_silence: bool = False,
    evaluator_can_judge: bool = True,
) -> EpistemicState:
    """Classify evidence without treating assertions as proof.

    The function intentionally refuses to manufacture certainty from absent or
    assertion-only evidence.
    """
    records = tuple(evidence)

    if explicit_silence:
        return EpistemicState.SILENCE
    if explicitly_unenforced:
        return EpistemicState.DECLARED_UNENFORCED
    if not evaluator_can_judge:
        return EpistemicState.ABSTAIN
    if not records or all(record.is_assertion_only() for record in records):
        return EpistemicState.UNKNOWN
    if observed_conformance is True:
        return EpistemicState.PASS
    if observed_conformance is False:
        return EpistemicState.FAIL
    return EpistemicState.UNKNOWN
