"""
PARADOX_ENGINE_1.0
Canon Layer: SUBSTRATE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE
Non-Identity-Binding: True
Reversibility: True

Public API surface of the paradox_engine package.
"""

from paradox_engine.config import (
    EngineConfig,
    ExplorationBounds,
    DriftPolicy,
    NarrativeInflationPolicy,
    AltitudeDiscipline,
    DecayPolicy,
    GovernancePolicy,
    DEFAULT_CONFIG,
    ENGINE_VERSION,
    ENGINE_LINEAGE_ROOT,
)
from paradox_engine.core.paradox import (
    Paradox,
    ParadoxLibrary,
    ParadoxNode,
    Polarity,
    Proposition,
    SelfRefClass,
)
from paradox_engine.core.simulation import ParadoxSimulation, SimulationState
from paradox_engine.core.resolver import RecursiveResolver, ResolutionResult, HaltReason
from paradox_engine.core.engine import ParadoxEngine
from paradox_engine.governance.audit import AuditCluster, AuditEvent, AuditEventType
from paradox_engine.governance.enforcement import (
    EnforcementCluster,
    ConstraintViolation,
    ViolationCode,
)
from paradox_engine.governance.vault import VaultCluster, VaultRecord
from paradox_engine.substrate.copilot_substrate import (
    CopilotSubstrate,
    AlignmentFrame,
    AlignmentViolation,
)

__version__      = ENGINE_VERSION
__lineage_root__ = ENGINE_LINEAGE_ROOT
__all__ = [
    # Engine
    "ParadoxEngine",
    # Core
    "Paradox", "ParadoxLibrary", "ParadoxNode", "Proposition",
    "Polarity", "SelfRefClass",
    "ParadoxSimulation", "SimulationState",
    "RecursiveResolver", "ResolutionResult", "HaltReason",
    # Governance
    "AuditCluster", "AuditEvent", "AuditEventType",
    "EnforcementCluster", "ConstraintViolation", "ViolationCode",
    "VaultCluster", "VaultRecord",
    # Substrate
    "CopilotSubstrate", "AlignmentFrame", "AlignmentViolation",
    # Config
    "EngineConfig", "ExplorationBounds", "DriftPolicy",
    "NarrativeInflationPolicy", "AltitudeDiscipline",
    "DecayPolicy", "GovernancePolicy", "DEFAULT_CONFIG",
    "ENGINE_VERSION", "ENGINE_LINEAGE_ROOT",
]
