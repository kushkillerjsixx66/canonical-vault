class ConstraintResolver:
    """
    Resolves constraint classes from validated signals.
    """

    def resolve_classes(self, signals):
        classes = sorted({s.name for s in signals})
        return classes
