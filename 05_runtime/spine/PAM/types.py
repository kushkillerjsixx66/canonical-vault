from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Principle:
    id: str
    description: str
    tags: List[str]


@dataclass
class Anchor:
    atom: str
    principle: str
    confidence: float


@dataclass
class PAIG:
    anchors: List[Anchor]
    verdict: str
    lineage: Dict[str, Any]
