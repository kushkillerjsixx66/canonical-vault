from typing import Dict, Any
from .types import IDEIntent
from .normalizer import Normalizer
from .clause_splitter import ClauseSplitter
from .altitude import AltitudeDetector


class IDERuntime:
    """
    Intent Decomposition Engine runtime.
    """

    def __init__(self):
        self.normalizer = Normalizer()
        self.splitter = ClauseSplitter()
        self.altitude_detector = AltitudeDetector()

    def run(self, text: str, metadata: Dict[str, Any] | None = None) -> IDEIntent:
        metadata = metadata or {}

        normalized = self.normalizer.normalize(text)
        clauses = self.splitter.split(normalized)
        altitude = self.altitude_detector.detect(normalized)

        return IDEIntent(
            text=normalized,
            clauses=clauses,
            altitude=altitude,
            metadata={**metadata, "altitude": altitude},
        )
