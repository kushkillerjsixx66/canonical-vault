import re
from typing import List


class ClauseSplitter:
    """
    Splits text into clauses using simple heuristics.
    """

    def split(self, text: str) -> List[str]:
        if not text:
            return []

        parts = re.split(r"[.;]| and | then ", text, flags=re.IGNORECASE)
        return [p.strip() for p in parts if p.strip()]
