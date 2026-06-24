class ConstraintExtractor:
    """
    Extracts raw constraint signals from text.
    """

    KEYWORDS = {
        "safety": ["harm", "danger", "weapon", "attack"],
        "privacy": ["pii", "personal data", "email", "address", "ssn"],
        "compliance": ["gdpr", "hipaa", "regulation", "compliance"],
        "resource": ["latency", "throughput", "cost", "budget"],
        "content": ["nsfw", "explicit", "hate", "toxic"],
    }

    def extract(self, text: str):
        signals = []

        lower = text.lower()

        for cls, words in self.KEYWORDS.items():
            for w in words:
                if w in lower:
                    signals.append(
                        {
                            "class": cls,
                            "keyword": w,
                            "confidence": 1.0,
                        }
                    )

        return signals
