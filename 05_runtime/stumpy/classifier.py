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
    """Classify evidence without manufacturing certainty.

    PASS/FAIL require at least one non-assertion record with a valid digest and
    an independently observable acquisition method. Invalid or unsupported
    evidence cannot substantiate constitutional truth.
    """
    records = tuple(evidence)

    if explicit_silence:
        return EpistemicState.SILENCE
    if explicitly_unenforced:
        return EpistemicState.DECLARED_UNENFORCED
    if not evaluator_can_judge:
        return EpistemicState.ABSTAIN

    substantive = tuple(
        record for record in records
        if not record.is_assertion_only()
        and record.verify_digest()
        and record.is_independently_observable()
    )
    if not substantive:
        return EpistemicState.UNKNOWN
    if observed_conformance is True:
        return EpistemicState.PASS
    if observed_conformance is False:
        return EpistemicState.FAIL
    return EpistemicState.UNKNOWN
