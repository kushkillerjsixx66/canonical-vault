class AltitudeDetector:
    """
    Determines the abstraction altitude of the intent.
    """

    def detect(self, text: str) -> str:
        lower = text.lower()

        if any(w in lower for w in ["strategy", "framework", "policy"]):
            return "high"

        if any(w in lower for w in ["run", "execute", "call api", "query"]):
            return "low"

        return "medium"
