class Normalizer:
    """
    Basic text normalization.
    """

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        return text.strip()
