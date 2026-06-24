from typing import List
from .types import Anchor, Principle
from .matcher import PrincipleMatcher


class AnchorBuilder:
    """
    Builds anchors between atoms and principles.
    """

    def __init__(self):
        self.matcher = PrincipleMatcher()

    def build(self, atoms: List[str], principles: List[Principle]) -> List[Anchor]:
        anchors: List[Anchor] = []

        for atom in atoms:
            principle, score = self.matcher.match(atom, principles)

            if principle:
                anchors.append(
                    Anchor(
                        atom=atom,
                        principle=principle.id,
                        confidence=score,
                    )
                )

        return anchors
