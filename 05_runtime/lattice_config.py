"""
lattice_config.py — Canonical Lattice Runtime Configuration
============================================================
Authority: 04_system_spec / 05_runtime
Operator: LiminalJermo
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import Optional

OPERATOR: str = "LiminalJermo"
LATTICE_VERSION: str = "1.0"
GENESIS_DATE: str = "2026-06-17"
OPERATOR_CODE: str = "[OP]"
DEFAULT_OUTPUT_MODE: str = "HUD"


@dataclass(frozen=True)
class OperatorConfig:
    name: str = OPERATOR
    role: str = "root"
    sovereignty: str = "root"

    def __str__(self) -> str:
        return self.name


@dataclass
class VaultConfig:
    decay_window: int = 30
    prune_window: int = 30
    auto_cycle_snapshot_interval: int = 50
    list_page_size: int = 50
    default_classification: str = "STANDARD"
    hash_algorithm: str = "sha256"
    auto_cycle_snapshot_retention_days: int = 90
    vara_promotion_snapshot_retention_days: int = 180
    sentinel_incident_snapshot_retention_days: int = 365
    decay_purge_snapshot_retention_days: int = 365

    @property
    def decay_window_days(self) -> int:
        return self.decay_window

    @property
    def snapshot_interval_cycles(self) -> int:
        return self.auto_cycle_snapshot_interval


@dataclass
class AttentionWeights:
    context_retrieval: float = 0.1
    inference: float = 0.3
    vault_writes: float = 0.5
    vara_scan: float = 0.2


@dataclass
class SentinelConfig:
    g1_coherence_threshold: float = 0.75
    g2_session_attention_budget: float = 10.0
    g2_attention_weights: AttentionWeights = field(default_factory=AttentionWeights)
    g2_override_window_seconds: int = 60
    g3_anchor_snapshot_window_minutes: int = 5
    g3_auto_pass_on_no_write: bool = True
    fabrication_grounding_min_ratio: float = 0.70
    require_explicit_lock_clear: bool = True

    @property
    def g2_attention_budget(self) -> float:
        return self.g2_session_attention_budget

    @property
    def g3_anchor_review_window_seconds(self) -> int:
        return self.g3_anchor_snapshot_window_minutes * 60


@dataclass
class VeilConfig:
    max_queue_size: int = 100
    priority_order: dict = field(default_factory=lambda: {
        "SENTINEL_INCIDENT": 1,
        "G1_BLOCK": 2,
        "VARA_HYPOTHESIS": 3,
        "G2_SOFT_BLOCK": 4,
        "G3_BLOCK": 5,
    })
    review_escalation_days: int = 7
    overflow_alert_enabled: bool = True
    overflow_behaviour: str = "alert_and_hold"

    @property
    def max_queue(self) -> int:
        return self.max_queue_size


@dataclass
class VaraConfig:
    entropy_spike_threshold: float = 0.15
    hypothesis_confidence_max: float = 0.65
    entropy_baseline_window: int = 30
    hypothesis_salience_min: float = 0.30
    contradiction_risk_alert_threshold: float = 0.50
    parallel_scan_enabled: bool = True
    max_hypotheses_per_cycle: int = 5

    @property
    def confidence_max(self) -> float:
        return self.hypothesis_confidence_max


@dataclass
class StumpyConfig:
    coherence_drift_epsilon: float = 0.05
    audit_records_decay_exempt: bool = True
    findings_major_threshold: int = 1
    findings_minor_threshold: int = 3
    audit_log_retention_cycles: int = 100
    chain_integrity_every_cycle: bool = True
    chain_integrity_check_interval: int = 10

    @property
    def drift_epsilon(self) -> float:
        return self.coherence_drift_epsilon


@dataclass
class CrossroadConfig:
    coherence_tie_epsilon: float = 0.05
    max_candidate_paths: int = 10
    preserve_rejected_paths: bool = True
    log_tie_defaults: bool = True

    @property
    def tie_epsilon(self) -> float:
        return self.coherence_tie_epsilon


@dataclass
class SBMConfig:
    default_output_mode: str = "HUD"
    clarify_on_ambiguity: bool = True
    unknown_symbol_behaviour: str = "quarantine"
    include_cycle_id_in_hud: bool = True
    max_output_tokens: int = 2048
    show_neuralese_in_full_lattice: bool = True

    @property
    def default_mode(self) -> str:
        return self.default_output_mode


@dataclass
class NeuraleseConfig:
    lexicon_path: str = "02_epistemic_substrate/Neuralese_Lexicon.md"
    enforce_lexicon_membership: bool = True
    packet_segment_count: int = 4
    segment_delimiter: str = " | "
    packet_open: str = "["
    packet_close: str = "]"


@dataclass
class PulseConfig:
    cycle_timeout_seconds: int = 300
    activation_stage_timeout_seconds: int = 60
    evaluation_stage_timeout_seconds: int = 60
    silence_interval_seconds: int = 30
    activation_decay_rate: float = 0.10
    activation_floor: float = 0.05
    activation_decay_window_cycles: int = 5
    max_active_nodes: int = 25
    log_cycle_boundaries: bool = True
    cycle_id_format: str = "uuid"


@dataclass
class LatticeConfig:
    operator: OperatorConfig = field(default_factory=OperatorConfig)
    lattice_version: str = LATTICE_VERSION
    genesis_date: str = GENESIS_DATE
    vault: VaultConfig = field(default_factory=VaultConfig)
    sentinel: SentinelConfig = field(default_factory=SentinelConfig)
    veil: VeilConfig = field(default_factory=VeilConfig)
    vara: VaraConfig = field(default_factory=VaraConfig)
    stumpy: StumpyConfig = field(default_factory=StumpyConfig)
    crossroad: CrossroadConfig = field(default_factory=CrossroadConfig)
    sbm: SBMConfig = field(default_factory=SBMConfig)
    neuralese: NeuraleseConfig = field(default_factory=NeuraleseConfig)
    pulse: PulseConfig = field(default_factory=PulseConfig)

    def summary(self) -> str:
        return (
            "[LATTICE CONFIG SUMMARY]\n"
            f"  Operator       : {self.operator.name}\n"
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


_DEFAULT = LatticeConfig()
G1_COHERENCE_THRESHOLD = _DEFAULT.sentinel.g1_coherence_threshold
G2_SESSION_BUDGET = _DEFAULT.sentinel.g2_session_attention_budget
G2_OVERRIDE_WINDOW_SECONDS = _DEFAULT.sentinel.g2_override_window_seconds
G3_ANCHOR_WINDOW_MINUTES = _DEFAULT.sentinel.g3_anchor_snapshot_window_minutes
VAULT_DECAY_WINDOW = _DEFAULT.vault.decay_window
VAULT_PRUNE_WINDOW = _DEFAULT.vault.prune_window
VAULT_SNAPSHOT_INTERVAL = _DEFAULT.vault.auto_cycle_snapshot_interval
VEIL_MAX_QUEUE = _DEFAULT.veil.max_queue_size
VARA_ENTROPY_SPIKE_THRESHOLD = _DEFAULT.vara.entropy_spike_threshold
VARA_HYPOTHESIS_CONFIDENCE_MAX = _DEFAULT.vara.hypothesis_confidence_max
STUMPY_COHERENCE_DRIFT_EPSILON = _DEFAULT.stumpy.coherence_drift_epsilon
CROSSROAD_COHERENCE_TIE_EPSILON = _DEFAULT.crossroad.coherence_tie_epsilon
SBM_DEFAULT_OUTPUT_MODE = _DEFAULT.sbm.default_output_mode


def validate_config(cfg: Optional[LatticeConfig] = None) -> bool:
    """Return True iff the supplied/default configuration satisfies boot constraints."""
    if cfg is None:
        cfg = LatticeConfig()
    violations = []
    if not (0.0 <= cfg.sentinel.g1_coherence_threshold <= 1.0):
        violations.append("g1_coherence_threshold")
    if cfg.sentinel.g2_session_attention_budget <= 0:
        violations.append("g2_session_attention_budget")
    if cfg.sentinel.g2_override_window_seconds <= 0:
        violations.append("g2_override_window_seconds")
    if not (0.0 < cfg.vara.hypothesis_confidence_max < 1.0):
        violations.append("hypothesis_confidence_max")
    if cfg.vara.entropy_spike_threshold <= 0:
        violations.append("entropy_spike_threshold")
    if cfg.vault.decay_window <= 0:
        violations.append("decay_window")
    if cfg.vault.auto_cycle_snapshot_interval <= 0:
        violations.append("auto_cycle_snapshot_interval")
    if cfg.stumpy.coherence_drift_epsilon < 0:
        violations.append("coherence_drift_epsilon")
    if cfg.crossroad.coherence_tie_epsilon < 0:
        violations.append("coherence_tie_epsilon")
    if cfg.veil.max_queue_size <= 0:
        violations.append("max_queue_size")
    if cfg.pulse.cycle_timeout_seconds <= 0:
        violations.append("cycle_timeout_seconds")
    if cfg.pulse.silence_interval_seconds < 0:
        violations.append("silence_interval_seconds")
    if not (0.0 <= cfg.pulse.activation_decay_rate <= 1.0):
        violations.append("activation_decay_rate")
    if not (0.0 <= cfg.pulse.activation_floor <= 1.0):
        violations.append("activation_floor")
    if cfg.pulse.activation_decay_window_cycles <= 0:
        violations.append("activation_decay_window_cycles")
    if cfg.pulse.max_active_nodes <= 0:
        violations.append("max_active_nodes")
    return not violations


if __name__ == "__main__":
    cfg = LatticeConfig()
    print(cfg.summary())
    print("[CONFIG VALID]" if validate_config(cfg) else "[CONFIG VIOLATIONS DETECTED]")
