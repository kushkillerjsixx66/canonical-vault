from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class RawInput:
    """Raw input into the Lattice pipeline."""
    text: str
    metadata: Dict[str, Any]


@dataclass
class SemanticAtom:
    """Smallest unit of meaning extracted by SBM."""
    text: str
    span_start: int
    span_end: int
    metadata: Dict[str, Any]


@dataclass
class SemanticBreakdown:
    """Full breakdown result."""
    atoms: List[SemanticAtom]
    notes: Optional[str] = None
