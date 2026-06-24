from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class RawIntent:
    text: str
    metadata: Dict[str, Any]


@dataclass
class Constraint:
    name: str
    rule: str
    value: Any
    source: str


@dataclass
class Mechanism:
    name: str
    description: str


@dataclass
class MechanismPlan:
    mechanism: Mechanism
    steps: List[Dict[str, Any]]
    constraints: Dict[str, Any]
    lineage: Dict[str, Any]
