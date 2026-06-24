class PostureResolver:
    """
    Maps load → execution posture.
    """

    def resolve(self, load: float) -> str:
        if load < 0.4:
            return "normal"
        if load < 0.7:
            return "cautious"
        if load < 0.9:
            return "degraded"
        return "blocked"
