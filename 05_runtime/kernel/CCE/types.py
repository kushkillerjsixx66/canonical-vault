from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class ConstraintSignal:
    name: str
    value: Any
    source: str
    confidence: float


@dataclass
class ConstraintMap:
    classes: List[str]
    signals: List[ConstraintSignal]
    metadata: Dict[str, Any]
