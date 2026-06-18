"""
test_lattice_config.py — Canonical Lattice Smoke Tests: Runtime Configuration
==============================================================================
Authority: 05_runtime/tests/
Operator: LiminalJermo
Generated: 2026-06-17
Lineage: lattice_config.py · MODULE_REGISTRY.md · Lattice_Invariants_v1.md

Tests that the LatticeConfig dataclass loads with canonical defaults,
that validate_config() passes, and that all spec-defined thresholds are present
and correctly valued.
"""

import sys
import importlib
import dataclasses
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_config():
    """Import lattice_config from the runtime directory."""
    try:
        import importlib.util, os
        spec_path = os.path.join(os.path.dirname(__file__), "..", "lattice_config.py")
        spec = importlib.util.spec_from_file_location("lattice_config", spec_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        pytest.skip(f"lattice_config.py not importable from test context: {e}")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def cfg_module():
    return _import_config()


@pytest.fixture(scope="module")
def lattice(cfg_module):
    return cfg_module.LatticeConfig()


# ---------------------------------------------------------------------------
# 1. Operator Identity
# ---------------------------------------------------------------------------

class TestOperatorIdentity:
    def test_operator_name(self, lattice):
        """Operator identity must be 'LiminalJermo' per spec."""
        assert lattice.operator.name == "LiminalJermo", (
            f"Expected operator 'LiminalJermo', got '{lattice.operator.name}'"
        )

    def test_operator_field_exists(self, lattice):
        assert hasattr(lattice, "operator"), "LatticeConfig missing 'operator' field"


# ---------------------------------------------------------------------------
# 2. Sentinel / Governance Gate Thresholds (spec-mandated values)
# ---------------------------------------------------------------------------

class TestSentinelConfig:
    def test_g1_coherence_threshold(self, lattice):
        """G1 coherence minimum must be 0.75 (Governance_Gates.md §G1 Scoring)."""
        assert lattice.sentinel.g1_coherence_threshold == 0.75, (
            f"G1 threshold mismatch: {lattice.sentinel.g1_coherence_threshold}"
        )

    def test_g2_attention_budget(self, lattice):
        """G2 attention budget default must be 10.0 (spec §G2)."""
        assert lattice.sentinel.g2_attention_budget == 10.0, (
            f"G2 budget mismatch: {lattice.sentinel.g2_attention_budget}"
        )

    def test_g2_override_window(self, lattice):
        """G2 operator override window must be 60 seconds."""
        assert lattice.sentinel.g2_override_window_seconds == 60, (
            f"G2 override window: {lattice.sentinel.g2_override_window_seconds}"
        )

    def test_g3_anchor_window(self, lattice):
        """G3 anchor write review window must be 5 minutes (300s)."""
        assert lattice.sentinel.g3_anchor_review_window_seconds == 300, (
            f"G3 anchor window: {lattice.sentinel.g3_anchor_review_window_seconds}"
        )


# ---------------------------------------------------------------------------
# 3. Vault Config
# ---------------------------------------------------------------------------

class TestVaultConfig:
    def test_decay_window(self, lattice):
        """Vault decay window must be 30 days (Lattice_Node_Model.md §Decay)."""
        assert lattice.vault.decay_window_days == 30, (
            f"Decay window: {lattice.vault.decay_window_days}"
        )

    def test_snapshot_interval(self, lattice):
        """Auto snapshot every 50 Pulse cycles (SNAPSHOT_REGISTRY.md §AUTO_CYCLE)."""
        assert lattice.vault.snapshot_interval_cycles == 50, (
            f"Snapshot interval: {lattice.vault.snapshot_interval_cycles}"
        )


# ---------------------------------------------------------------------------
# 4. Vara Config
# ---------------------------------------------------------------------------

class TestVaraConfig:
    def test_entropy_spike_threshold(self, lattice):
        """Vara entropy spike threshold must be 0.15 (Vara_Spec.md §Entropy Monitoring)."""
        assert lattice.vara.entropy_spike_threshold == 0.15, (
            f"Entropy spike: {lattice.vara.entropy_spike_threshold}"
        )

    def test_confidence_max(self, lattice):
        """Vara hypothesis confidence ceiling must be 0.65 (Vara_Spec.md §Hypothesis)."""
        assert lattice.vara.confidence_max == 0.65, (
            f"Confidence max: {lattice.vara.confidence_max}"
        )


# ---------------------------------------------------------------------------
# 5. Stumpy / Drift Config
# ---------------------------------------------------------------------------

class TestStumpyConfig:
    def test_drift_epsilon(self, lattice):
        """Coherence drift epsilon must be 0.05 (Stumpy_Spec.md §Coherence Audit)."""
        assert lattice.stumpy.drift_epsilon == 0.05, (
            f"Drift epsilon: {lattice.stumpy.drift_epsilon}"
        )


# ---------------------------------------------------------------------------
# 6. Crossroad Config
# ---------------------------------------------------------------------------

class TestCrossroadConfig:
    def test_tie_epsilon(self, lattice):
        """Crossroad tie-break epsilon must be 0.05 (Crossroad_Spec.md §Path Scoring)."""
        assert lattice.crossroad.tie_epsilon == 0.05, (
            f"Tie epsilon: {lattice.crossroad.tie_epsilon}"
        )


# ---------------------------------------------------------------------------
# 7. Veil Config
# ---------------------------------------------------------------------------

class TestVeilConfig:
    def test_max_queue(self, lattice):
        """Veil max queue size must be 100 (Veil_Spec.md §Overflow Management)."""
        assert lattice.veil.max_queue == 100, (
            f"Veil max_queue: {lattice.veil.max_queue}"
        )


# ---------------------------------------------------------------------------
# 8. SBM Config
# ---------------------------------------------------------------------------

class TestSBMConfig:
    def test_default_mode(self, lattice):
        """SBM default output mode must be 'HUD' (SBM_Spec.md §Output Modes)."""
        assert lattice.sbm.default_mode == "HUD", (
            f"SBM default_mode: {lattice.sbm.default_mode}"
        )


# ---------------------------------------------------------------------------
# 9. Pulse Config
# ---------------------------------------------------------------------------

class TestPulseConfig:
    def test_cycle_timeout(self, lattice):
        """Pulse cycle hard timeout must be 300 seconds (Pulse_Cycle_Spec.md)."""
        assert lattice.pulse.cycle_timeout_seconds == 300, (
            f"Pulse timeout: {lattice.pulse.cycle_timeout_seconds}"
        )


# ---------------------------------------------------------------------------
# 10. validate_config() boot self-check
# ---------------------------------------------------------------------------

class TestValidateConfig:
    def test_validate_config_passes(self, cfg_module):
        """validate_config() must return True with canonical defaults."""
        result = cfg_module.validate_config()
        assert result is True, (
            "validate_config() returned falsy — boot self-check failed"
        )

    def test_validate_config_no_exception(self, cfg_module):
        """validate_config() must not raise on canonical defaults."""
        try:
            cfg_module.validate_config()
        except Exception as e:
            pytest.fail(f"validate_config() raised an exception: {e}")


# ---------------------------------------------------------------------------
# 11. Dataclass field completeness
# ---------------------------------------------------------------------------

class TestDataclassCompleteness:
    REQUIRED_TOP_LEVEL_FIELDS = [
        "operator", "vault", "sentinel", "veil",
        "vara", "stumpy", "crossroad", "sbm",
        "neuralese", "pulse",
    ]

    def test_all_required_fields_present(self, lattice):
        """All required top-level config fields must be present on LatticeConfig."""
        missing = [
            f for f in self.REQUIRED_TOP_LEVEL_FIELDS
            if not hasattr(lattice, f)
        ]
        assert not missing, f"LatticeConfig missing fields: {missing}"

    def test_lattice_config_is_dataclass(self, cfg_module):
        """LatticeConfig must be a Python dataclass."""
        assert dataclasses.is_dataclass(cfg_module.LatticeConfig), (
            "LatticeConfig is not a dataclass"
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
