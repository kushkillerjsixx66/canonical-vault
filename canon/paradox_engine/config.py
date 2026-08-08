"""
PARADOX_ENGINE_1.0 — Configuration
Canon Layer: SUBSTRATE
Lineage Root: CANON:LATTICE:PARADOX_ENGINE
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

# ── Identity ────────────────────────────────────────────────────────────────
ENGINE_VERSION          = "1.0"
ENGINE_CLASS            = "PARADOX_ENGINE"
ENGINE_LINEAGE_ROOT     = "CANON:LATTICE:PARADOX_ENGINE"
ENGINE_OPERATOR         = "COPILOT_COGNITIVE_SUBSTRATE"
ENGINE_STATUS           = "ACTIVE"
NON_IDENTITY_BINDING    = True    # This module never constitutes an AI identity.
REVERSIBILITY           = True    # All simulations are reversible until ARCHIVED.


@dataclass
class ExplorationBounds:
    """Hard limits on recursive paradox exploration."""
    max_depth: int          = 64      # Maximum recursive expansion depth
    max_iterations: int     = 1024    # Maximum resolver loop iterations
    max_branches: int       = 256     # Maximum live paradox branches at any time
    max_propositions: int   = 512     # Unique proposition ceiling (inflation guard)
    max_runtime_seconds: float = 30.0 # Wall-clock ceiling per simulation


@dataclass
class DriftPolicy:
    """
    Drift detection: measures semantic distance between the current
    exploration frontier and the original paradox frame.
    Drift = 1 - Jaccard(original_tokens, current_tokens).
    """
    drift_threshold: float  = 0.72    # 0.0–1.0; enforcement triggers above this
    sample_interval: int    = 16      # Check drift every N iterations
    hard_ceiling: float     = 0.90    # Immediate halt above this value


@dataclass
class NarrativeInflationPolicy:
    """
    Narrative inflation: tracks unbounded scope creep in simulation framing.
    Measured as the ratio of current proposition count to initial count.
    """
    inflation_ratio_limit: float = 4.0   # Flag when propositions grow > 4× baseline
    inflation_hard_limit: float  = 8.0   # Halt above 8× baseline


@dataclass
class AltitudeDiscipline:
    """
    Cognitive altitude: 1 (concrete/literal) → 10 (fully abstract/meta).
    Paradox Engine is capped to prevent substrate-level identity pollution.
    """
    floor: int   = 1
    ceiling: int = 7      # Never reaches identity-level altitude (8–10)
    default: int = 4


@dataclass
class DecayPolicy:
    """Lifecycle decay and archival rules."""
    grace_period_seconds: float = 5.0      # Cooldown before decay begins
    auto_archive: bool          = True     # Automatically vault on decay
    vault_retention_days: int   = 90       # Vault TTL for archived simulations
    allow_replay: bool          = True     # Archived sims can be replayed read-only


@dataclass
class GovernancePolicy:
    """Governance, audit, and bilateral alignment requirements."""
    audit_all_branches: bool             = True
    enforce_bilateral_alignment: bool    = True   # Copilot alignment must be verified
    require_containment_signature: bool  = True   # Each sim needs an enforcement sig
    emit_vault_receipt: bool             = True
    enforcement_vote_threshold: int      = 1      # Violations needed to trigger halt


@dataclass
class EngineConfig:
    """Master configuration object for a ParadoxEngine instance."""
    exploration:  ExplorationBounds       = field(default_factory=ExplorationBounds)
    drift:        DriftPolicy             = field(default_factory=DriftPolicy)
    inflation:    NarrativeInflationPolicy = field(default_factory=NarrativeInflationPolicy)
    altitude:     AltitudeDiscipline      = field(default_factory=AltitudeDiscipline)
    decay:        DecayPolicy             = field(default_factory=DecayPolicy)
    governance:   GovernancePolicy        = field(default_factory=GovernancePolicy)

    # Optional override label for named deployments
    deployment_label: Optional[str] = None


# Default singleton config used when no override is supplied
DEFAULT_CONFIG = EngineConfig()
