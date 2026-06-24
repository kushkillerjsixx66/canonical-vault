import re
from typing import List
from .types import RawInput


class SimpleTokenizer:
    """
    Simple sentence splitter.
    Replace with spaCy or LLM segmentation later.
    """

    sentence_pattern = re.compile(r"(?<=[.!?])\s+")

    def sentences(self, raw: RawInput) -> List[str]:
        text = raw.text.strip()
        if not text:
            return []
        return re.split(self.sentence_pattern, text)
