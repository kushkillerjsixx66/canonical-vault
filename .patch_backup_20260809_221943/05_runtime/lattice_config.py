"""
lattice_config.py — Canonical Lattice Runtime Configuration
============================================================
Authority:   04_system_spec / 05_runtime
Operator:    LiminalJermo
Version:     1.0
Generated:   2026-06-17
Lineage:     lattice_initiation.md (Appendix C) · Lattice_Invariants_v1.md
             Governance_Gates.md · MODULE_REGISTRY.md

Description:
    Single source of truth for all runtime thresholds, budgets, operator
    identity, and module-level defaults for the Canonical Lattice Python
    runtime. Every configurable value that appears in the Canonical spec
    is wired here. No magic numbers should appear in module code — import
    from this file instead.

Usage:
    from lattice_config import LatticeConfig
    cfg = LatticeConfig()

    # Access operator identity
    print(cfg.OPERATOR)                  # "LiminalJermo"

    # Access Sentinel thresholds
    print(cfg.sentinel.g1_coherence_threshold)   # 0.75
    print(cfg.sentinel.g2_session_budget)        # 10.0

Amendment:
    Changes to any value in this file that affect runtime gate behaviour
    must be logged as an OPERATOR_DIRECTIVE Node in the Vault with a
    chain link to the previous configuration ANCHOR and a Stumpy audit
    record. See Operator_Playbook.md SOP-004 (Amending a Gate Threshold).
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# § 0  —  OPERATOR IDENTITY
# ---------------------------------------------------------------------------

OPERATOR: str = "LiminalJermo"
LATTICE_VERSION: str = "1.0"
GENESIS_DATE: str = "2026-06-17"

# Neuralese operator code used in signal packets
OPERATOR_CODE: str = "[OP]"

# Default output mode: "HUD" or "FULL_LATTICE"
DEFAULT_OUTPUT_MODE: str = "HUD"


# ---------------------------------------------------------------------------
# § 1  —  VAULT CONFIG  (Rank 3)
# ---------------------------------------------------------------------------

@dataclass
class VaultConfig:
    """
    Persistent memory configuration.
    Governs decay timing and auto-snapshot cadence.

    Invariant bindings: II·REV (append-only), V·DEC (decay mandate)
    """

    # Number of days before a LATENT node transitions to DECAYING
    decay_window: int = 30                     # days

    # Number of days before a DECAYING node is flagged as PRUNE_CANDIDATE
    prune_window: int = 30                     # days

    # Number of Pulse cycles between automatic snapshots
    auto_cycle_snapshot_interval: int = 50     # cycles

    # Maximum number of nodes to return in a VAULT LIST response
    list_page_size: int = 50

    # Default classification for new Vault writes
    default_classification: str = "STANDARD"

    # Hash algorithm used for content_hash integrity check
    hash_algorithm: str = "sha256"

    # Retention period for AUTO_CYCLE snapshots (days)
    auto_cycle_snapshot_retention_days: int = 90

    # Retention period for VARA_PROMOTION snapshots (days)
    vara_promotion_snapshot_retention_days: int = 180

    # Retention period for SENTINEL_INCIDENT snapshots (days)
    sentinel_incident_snapshot_retention_days: int = 365

    # Retention period for DECAY_PURGE snapshots (days)
    decay_purge_snapshot_retention_days: int = 365


# ---------------------------------------------------------------------------
# § 2  —  SENTINEL CONFIG  (Rank 4)
# ---------------------------------------------------------------------------

@dataclass
class AttentionWeights:
    """
    CCE (Cognitive Cost Estimator) attention cost weights.
    Invariant binding: III·ATT (attention is a scarce resource)
    """
    context_retrieval: float = 0.1    # cost per Vault read / Node activation
    inference:         float = 0.3    # cost per inference step
    vault_writes:      float = 0.5    # cost per Vault write
    vara_scan:         float = 0.2    # cost per Vara weak-signal scan pass


@dataclass
class SentinelConfig:
    """
    Gate enforcement thresholds for Sentinel (Rank 4).
    These values are the runtime implementation of Governance_Gates.md.
    """

    # --- G1: Coherence Gate ---
    # Minimum coherence score (0.0–1.0) for G1 PASS
    # Ref: Governance_Gates.md §G1 — default threshold 0.75
    g1_coherence_threshold: float = 0.75

    # --- G2: Attention Cost Gate ---
    # Total attention units available per session
    # Ref: Governance_Gates.md §G2 — default budget 10.0
    g2_session_attention_budget: float = 10.0

    # Attention cost weights
    g2_attention_weights: AttentionWeights = field(default_factory=AttentionWeights)

    # Duration of the G2 soft-block operator override window (seconds)
    # Ref: Governance_Gates.md §G2 — override window 60 seconds
    g2_override_window_seconds: int = 60

    # --- G3: Reversibility Gate ---
    # Duration before a pending ANCHOR write must be confirmed (minutes)
    # Ref: Governance_Gates.md §G3 — anchor snapshot confirmation window 5 minutes
    g3_anchor_snapshot_window_minutes: int = 5

    # Whether G3 auto-passes when no Vault write is planned
    g3_auto_pass_on_no_write: bool = True

    # --- Fabrication Detection (IV·SIL) ---
    # Minimum Vault grounding ratio required for SBM output
    fabrication_grounding_min_ratio: float = 0.70

    # --- Sentinel Lock ---
    # Whether to require explicit SENTINEL CLEAR before resuming
    require_explicit_lock_clear: bool = True


# ---------------------------------------------------------------------------
# § 3  —  VEIL CONFIG  (Rank 5)
# ---------------------------------------------------------------------------

@dataclass
class VeilConfig:
    """
    Quarantine and mediation layer configuration.
    Invariant binding: VI·SIG (weak signals must be preserved)
    """

    # Maximum number of entries the Veil queue may hold
    # Ref: lattice_initiation.md Appendix C — max_queue_size=100
    max_queue_size: int = 100

    # Priority ordering for the Veil review queue (1 = highest)
    priority_order: dict = field(default_factory=lambda: {
        "SENTINEL_INCIDENT": 1,
        "G1_BLOCK":          2,

# ---------------------------------------------------------------------------
# § 4  —  VARA CONFIG  (Rank 6)
# ---------------------------------------------------------------------------

@dataclass
class VaraConfig:
    """
    Weak-signal scanner and edge-detection configuration.
    Invariant binding: VI·SIG (weak signal parity)
    """

    # Fractional entropy increase above 30-cycle rolling average
    # Ref: lattice_initiation.md Appendix C — entropy_spike_threshold=0.15
    entropy_spike_threshold: float = 0.15

    # Maximum confidence score a Vara hypothesis may carry
    # Ref: lattice_initiation.md Appendix C — hypothesis_confidence_max=0.65
    hypothesis_confidence_max: float = 0.65

    # Rolling average window for entropy baseline (cycles)
    entropy_baseline_window: int = 30

    # Minimum salience score for a weak signal to generate a hypothesis
    hypothesis_salience_min: float = 0.30

    # Maximum contradiction risk before alert
    contradiction_risk_alert_threshold: float = 0.50

    # Whether Vara runs in parallel with Pulse Stage 2
    parallel_scan_enabled: bool = True

    # Maximum hypotheses Vara may generate per cycle
    max_hypotheses_per_cycle: int = 5


# ---------------------------------------------------------------------------
# § 5  —  STUMPY CONFIG  (Rank 7)
# ---------------------------------------------------------------------------

@dataclass
class StumpyConfig:
    """
    Integrity audit and decay lifecycle manager configuration.
    Symbol: Omega. Invariant binding: I·COH, II·REV, V·DEC
    """

    # Acceptable coherence drift between Sentinel G1 and Stumpy full-Vault audit
    # Ref: lattice_initiation.md Appendix C — coherence_drift_epsilon=0.05
    coherence_drift_epsilon: float = 0.05

    # AUDIT_RECORD Nodes always have decay_rate = 0.0
    audit_records_decay_exempt: bool = True

    # Compliance rating thresholds
    findings_major_threshold: int = 1
    findings_minor_threshold: int = 3

    # Maximum cycles Stumpy retains raw audit logs before archiving
    audit_log_retention_cycles: int = 100

    # Whether to run chain integrity check on every Pulse cycle
    chain_integrity_every_cycle: bool = True

    # If chain_integrity_every_cycle is False: run every N cycles
    chain_integrity_check_interval: int = 10


# ---------------------------------------------------------------------------
# § 6  —  CROSSROAD CONFIG  (Rank 8)
# ---------------------------------------------------------------------------

@dataclass
class CrossroadConfig:
    """
    Routing and path-resolution configuration.
    Invariant binding: I·COH (coherence-first path selection), III·ATT
    """

    # Coherence score difference below which two paths are considered tied
    # Ref: lattice_initiation.md Appendix C — coherence_tie_epsilon=0.05
    coherence_tie_epsilon: float = 0.05

    # Maximum candidate execution paths Crossroad will evaluate
    max_candidate_paths: int = 10

    # Whether rejected paths are preserved in Vault as AUDIT_RECORD entries
    preserve_rejected_paths: bool = True

    # Whether Crossroad logs TIE_DEFAULT events to Stumpy
    log_tie_defaults: bool = True


# ---------------------------------------------------------------------------
# § 7  —  SBM CONFIG  (Rank 9)
# ---------------------------------------------------------------------------

@dataclass
class SBMConfig:
    """
    Semantic Binding Module configuration.
    Invariant binding: IV·SIL (no fabrication), I·COH
    """

    # Default operator output mode
    # Ref: lattice_initiation.md Appendix C — default_output_mode="HUD"
    default_output_mode: str = "HUD"

    # Whether SBM requests clarification on ambiguous operator input
    clarify_on_ambiguity: bool = True

    # Unknown symbol behaviour: "quarantine" or "pass_through"
    unknown_symbol_behaviour: str = "quarantine"

    # Whether SBM includes cycle ID in every HUD output line
    include_cycle_id_in_hud: bool = True

    # Maximum natural language output length per cycle (tokens, approximate)
    max_output_tokens: int = 2048

    # Whether to include Neuralese packet alongside NL output in FULL_LATTICE mode
    show_neuralese_in_full_lattice: bool = True


# ---------------------------------------------------------------------------
# § 8  —  NEURALESE CONFIG
# ---------------------------------------------------------------------------

@dataclass
class NeuraleseConfig:
    """
    Neuralese protocol configuration.
    Reference: 02_epistemic_substrate/Neuralese_Lexicon.md
    """

    lexicon_path: str = "02_epistemic_substrate/Neuralese_Lexicon.md"
    enforce_lexicon_membership: bool = True
    packet_segment_count: int = 4
    segment_delimiter: str = " | "
    packet_open: str = "["
    packet_close: str = "]"


# ---------------------------------------------------------------------------
# § 9  —  PULSE CYCLE CONFIG

# ---------------------------------------------------------------------------
# § 10  —  MASTER CONFIG OBJECT
# ---------------------------------------------------------------------------

@dataclass
class LatticeConfig:
    """
    Master configuration object for the Canonical Lattice runtime.

    Instantiate once at boot in lattice_runtime.py:
        from lattice_config import LatticeConfig
        cfg = LatticeConfig()
    """

    operator:        str = OPERATOR
    lattice_version: str = LATTICE_VERSION
    genesis_date:    str = GENESIS_DATE

    vault:      VaultConfig     = field(default_factory=VaultConfig)
    sentinel:   SentinelConfig  = field(default_factory=SentinelConfig)
    veil:       VeilConfig      = field(default_factory=VeilConfig)
    vara:       VaraConfig      = field(default_factory=VaraConfig)
    stumpy:     StumpyConfig    = field(default_factory=StumpyConfig)
    crossroad:  CrossroadConfig = field(default_factory=CrossroadConfig)
    sbm:        SBMConfig       = field(default_factory=SBMConfig)
    neuralese:  NeuraleseConfig = field(default_factory=NeuraleseConfig)
    pulse:      PulseConfig     = field(default_factory=PulseConfig)

    def summary(self) -> str:
        """Return a HUD-formatted config summary for boot verification."""
        return (
            f"[LATTICE CONFIG SUMMARY]\n"
            f"  Operator       : {self.operator}\n"
            f"  Version        : {self.lattice_version}\n"
            f"  Genesis Date   : {self.genesis_date}\n"
            f"  Output Mode    : {self.sbm.default_output_mode}\n"
            f"  G1 Threshold   : {self.sentinel.g1_coherence_threshold}\n"
            f"  G2 Budget      : {self.sentinel.g2_session_attention_budget}\n"
            f"  G2 Override Wn : {self.sentinel.g2_override_window_seconds}s\n"
            f"  G3 Anchor Wn   : {self.sentinel.g3_anchor_snapshot_window_minutes}m\n"
            f"  Decay Window   : {self.vault.decay_window}d\n"
            f"  Snapshot Cadnc : every {self.vault.auto_cycle_snapshot_interval} cycles\n"
            f"  Vara Entropy D : >{self.vara.entropy_spike_threshold*100:.0f}%\n"
            f"  Vara Conf Max  : <{self.vara.hypothesis_confidence_max}\n"
            f"  Stumpy Drift e : {self.stumpy.coherence_drift_epsilon}\n"
            f"  Crossroad e    : {self.crossroad.coherence_tie_epsilon}\n"
            f"  Veil Max Queue : {self.veil.max_queue_size}\n"
        )


# ---------------------------------------------------------------------------
# § 11  —  CONVENIENCE ACCESSORS
# ---------------------------------------------------------------------------

_DEFAULT = LatticeConfig()

G1_COHERENCE_THRESHOLD:         float = _DEFAULT.sentinel.g1_coherence_threshold
G2_SESSION_BUDGET:               float = _DEFAULT.sentinel.g2_session_attention_budget
G2_OVERRIDE_WINDOW_SECONDS:      int   = _DEFAULT.sentinel.g2_override_window_seconds
G3_ANCHOR_WINDOW_MINUTES:        int   = _DEFAULT.sentinel.g3_anchor_snapshot_window_minutes

VAULT_DECAY_WINDOW:              int   = _DEFAULT.vault.decay_window
VAULT_PRUNE_WINDOW:              int   = _DEFAULT.vault.prune_window
VAULT_SNAPSHOT_INTERVAL:         int   = _DEFAULT.vault.auto_cycle_snapshot_interval

VEIL_MAX_QUEUE:                  int   = _DEFAULT.veil.max_queue_size

VARA_ENTROPY_SPIKE_THRESHOLD:    float = _DEFAULT.vara.entropy_spike_threshold
VARA_HYPOTHESIS_CONFIDENCE_MAX:  float = _DEFAULT.vara.hypothesis_confidence_max

STUMPY_COHERENCE_DRIFT_EPSILON:  float = _DEFAULT.stumpy.coherence_drift_epsilon

CROSSROAD_COHERENCE_TIE_EPSILON: float = _DEFAULT.crossroad.coherence_tie_epsilon

SBM_DEFAULT_OUTPUT_MODE:         str   = _DEFAULT.sbm.default_output_mode


# ---------------------------------------------------------------------------
# § 12  —  BOOT SELF-CHECK
# ---------------------------------------------------------------------------

def validate_config(cfg: Optional[LatticeConfig] = None) -> list[str]:
    """
    Run basic sanity checks on a LatticeConfig instance.
    Returns a list of violation strings (empty list = config is valid).
    Called automatically during lattice_runtime boot sequence.
    """
    if cfg is None:
        cfg = LatticeConfig()

    violations: list[str] = []

    if not (0.0 <= cfg.sentinel.g1_coherence_threshold <= 1.0):
        violations.append(
            f"G1 threshold {cfg.sentinel.g1_coherence_threshold} out of range [0.0, 1.0]"
        )
    if cfg.sentinel.g2_session_attention_budget <= 0:
        violations.append(
            f"G2 budget must be > 0 (got {cfg.sentinel.g2_session_attention_budget})"
        )
    if cfg.sentinel.g2_override_window_seconds <= 0:
        violations.append(
            f"G2 override window must be > 0s (got {cfg.sentinel.g2_override_window_seconds})"
        )
    if not (0.0 < cfg.vara.hypothesis_confidence_max < 1.0):
        violations.append(
            f"Vara hypothesis_confidence_max must be in (0.0,1.0) (got {cfg.vara.hypothesis_confidence_max})"
        )
    if cfg.vara.entropy_spike_threshold <= 0:
        violations.append(
            f"Vara entropy_spike_threshold must be > 0 (got {cfg.vara.entropy_spike_threshold})"
        )
    if cfg.vault.decay_window <= 0:
        violations.append(
            f"Vault decay_window must be > 0d (got {cfg.vault.decay_window})"
        )
    if cfg.vault.auto_cycle_snapshot_interval <= 0:
        violations.append(
            f"auto_cycle_snapshot_interval must be > 0 (got {cfg.vault.auto_cycle_snapshot_interval})"
        )
    if cfg.stumpy.coherence_drift_epsilon < 0:
        violations.append(
            f"Stumpy coherence_drift_epsilon must be >= 0 (got {cfg.stumpy.coherence_drift_epsilon})"
        )
    if cfg.crossroad.coherence_tie_epsilon < 0:
        violations.append(
            f"Crossroad coherence_tie_epsilon must be >= 0 (got {cfg.crossroad.coherence_tie_epsilon})"
        )
    if cfg.veil.max_queue_size <= 0:
        violations.append(
            f"Veil max_queue_size must be > 0 (got {cfg.veil.max_queue_size})"
        )

    return violations


# ---------------------------------------------------------------------------
# § 13  —  ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cfg = LatticeConfig()
    print(cfg.summary())

    violations = validate_config(cfg)
    if violations:
        print("\n[CONFIG VIOLATIONS DETECTED]")
        for v in violations:
            print(f"  X  {v}")
    else:
        print("\n[CONFIG VALID] All thresholds within bounds. Ready for boot.")
# ---------------------------------------------------------------------------

@dataclass
class PulseConfig:
    """Pulse Cycle orchestration configuration."""

    cycle_timeout_seconds: int = 300
    evaluation_stage_timeout_seconds: int = 60
    log_cycle_boundaries: bool = True
    cycle_id_format: str = "uuid"
        "VARA_HYPOTHESIS":   3,
        "G2_SOFT_BLOCK":     4,
        "G3_BLOCK":          5,
    })

    # Days before an un-reviewed entry is escalated to operator HUD
    review_escalation_days: int = 7

    # Whether Veil overflow triggers an operator alert
    overflow_alert_enabled: bool = True

    # Behaviour on overflow
    overflow_behaviour: str = "alert_and_hold"
