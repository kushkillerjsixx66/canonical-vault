from .types import ConstraintMap


class ConstraintCartographer:
    """
    Builds the final constraint map.
    """

    def build(self, classes, signals, altitude):
        return ConstraintMap(
            classes=classes,
            signals=signals,
            metadata={"altitude": altitude, "source": "cce"},
        )
