from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class IDEIntent:
    text: str
    clauses: List[str]
    altitude: str
    metadata: Dict[str, Any]
