from .types import ConstraintSignal


class ConstraintValidator:
    """
    Validates extracted constraint signals.
    """

    def validate(self, raw_signals):
        validated = []

        for s in raw_signals:
            validated.append(
                ConstraintSignal(
                    name=s["class"],
                    value=s["keyword"],
                    source="cce",
                    confidence=s["confidence"],
                )
            )

        return validated
