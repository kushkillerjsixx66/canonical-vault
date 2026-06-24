from typing import List
from .types import Principle


class PrincipleMatcher:
    """
    Matches semantic atoms to principles using tag overlap.
    """

    def match(self, atom_text: str, principles: List[Principle]):
        atom_lower = atom_text.lower()

        best = None
        best_score = 0

        for p in principles:
            score = sum(tag in atom_lower for tag in p.tags)
            if score > best_score:
                best = p
                best_score = score

        return best, float(best_score)
