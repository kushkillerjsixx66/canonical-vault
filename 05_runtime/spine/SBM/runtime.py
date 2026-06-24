from .types import RawInput, SemanticBreakdown
from .segmenter import SemanticSegmenter


class SBMRuntime:
    """
    Semantic Breakdown Module runtime.
    """

    def __init__(self):
        self.segmenter = SemanticSegmenter()

    def run(self, raw: RawInput) -> SemanticBreakdown:
        atoms = self.segmenter.segment(raw)

        notes = None
        if not atoms:
            notes = "No semantic atoms extracted."

        return SemanticBreakdown(
            atoms=atoms,
            notes=notes,
        )
