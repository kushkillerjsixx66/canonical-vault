from .extractor import ConstraintExtractor
from .validator import ConstraintValidator
from .resolver import ConstraintResolver
from .cartographer import ConstraintCartographer


class CCERuntime:
    """
    Constraint Cartography Engine runtime.
    """

    def __init__(self):
        self.extractor = ConstraintExtractor()
        self.validator = ConstraintValidator()
        self.resolver = ConstraintResolver()
        self.cartographer = ConstraintCartographer()

    def run(self, ide_intent):
        raw_signals = self.extractor.extract(ide_intent.text)
        validated = self.validator.validate(raw_signals)
        classes = self.resolver.resolve_classes(validated)

        return self.cartographer.build(
            classes=classes,
            signals=validated,
            altitude=ide_intent.altitude,
        )
