class PostureInterpreter:
    """
    Canonical posture interpreter.

    Converts raw runtime posture signals into canonical forms:
    - neutral
    - focused
    - elevated
    - hostile
    """

    def interpret(self, raw_state: dict) -> str:
        raw = raw_state.get("posture")

        if raw in ("neutral", "focused", "elevated", "hostile"):
            return raw

        # Default posture if none provided
        return "neutral"
