from typing import List
from .types import Principle, PAIG
from .anchor import AnchorBuilder


class PAMRuntime:
    """
    Principle Anchoring Module runtime.
    """

    def __init__(self, principles: List[Principle]):
        self.principles = principles
        self.builder = AnchorBuilder()

    def run(self, atoms: List[str]) -> PAIG:
        anchors = self.builder.build(atoms, self.principles)

        # Verdict logic
        if not anchors:
            verdict = "DEGRADED"
        elif any(a.confidence == 0 for a in anchors):
            verdict = "MITIGATED"
        else:
            verdict = "CLEAR"

        lineage = {
            "principle_count": len(self.principles),
            "anchor_count": len(anchors),
        }

        return PAIG(
            anchors=anchors,
            verdict=verdict,
            lineage=lineage,
        )
