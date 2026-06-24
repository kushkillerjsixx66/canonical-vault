from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CFCState:
    load: float
    posture: str
    metadata: Dict[str, Any]
