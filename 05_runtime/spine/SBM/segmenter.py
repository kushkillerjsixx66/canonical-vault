from typing import List
from .types import RawInput, SemanticAtom
from .tokenizer import SimpleTokenizer


class SemanticSegmenter:
    """
    Converts sentences into semantic atoms.
    """

    def __init__(self):
        self.tokenizer = SimpleTokenizer()

    def segment(self, raw: RawInput) -> List[SemanticAtom]:
        atoms: List[SemanticAtom] = []
        sentences = self.tokenizer.sentences(raw)

        cursor = 0
        text = raw.text

        for s in sentences:
            s = s.strip()
            if not s:
                continue

            idx = text.find(s, cursor)
            if idx == -1:
                idx = cursor

            atoms.append(
                SemanticAtom(
                    text=s,
                    span_start=idx,
                    span_end=idx + len(s),
                    metadata={"source": "sbm", **raw.metadata},
                )
            )

            cursor = idx + len(s)

        return atoms
