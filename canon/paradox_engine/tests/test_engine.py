"""
PARADOX_ENGINE_1.0 — Engine integration tests
Tests the full spin_up → run → decay → archive lifecycle.
"""
import pytest
from paradox_engine import (
    ParadoxEngine, Paradox, ParadoxLibrary,
    EngineConfig, ExplorationBounds, DecayPolicy,
    SimulationState,
)


@pytest.fixture
def fast_config():
    """A config with tight bounds for fast test execution."""
    cfg = EngineConfig()
    cfg.exploration.max_depth = 8
    cfg.exploration.max_iterations = 32
    cfg.exploration.max_runtime_seconds = 5.0
    cfg.decay.grace_period_seconds = 0.0
    cfg.decay.auto_archive = True
    return cfg


@pytest.fixture
def engine(fast_config):
    e = ParadoxEngine(config=fast_config)
    yield e
    e.shutdown()


# ── Spin-up ────────────────────────────────────────────────────────────────────

class TestSpinUp:
    def test_spin_up_from_string(self, engine):
        sim = engine.spin_up("This statement is false.")
        assert sim is not None
        assert sim.state == SimulationState.INIT

    def test_spin_up_from_paradox_object(self, engine):
        p = Paradox(seed_text="This statement is false.", label="liar-test")
        sim = engine.spin_up(p)
        assert sim.paradox.label == "liar-test"
        assert sim.state == SimulationState.INIT

    def test_spin_up_registers_simulation(self, engine):
        sim = engine.spin_up("This statement is false.")
        assert engine.get_simulation(sim.simulation_id) is sim

    def test_altitude_default(self, engine):
        sim = engine.spin_up("This statement is false.")
        assert sim.altitude == engine.config.altitude.default

    def test_altitude_override(self, engine):
        sim = engine.spin_up("This statement is false.", altitude=3)
        assert sim.altitude == 3

    def test_altitude_clamped_to_ceiling(self, engine):
        sim = engine.spin_up("This statement is false.", altitude=99)
        assert sim.altitude <= engine.config.altitude.ceiling


# ── Run ───────────────────────────────────────────────────────────────────────

class TestRun:
    def test_run_produces_result(self, engine):
        sim = engine.spin_up("This statement is false.")
        engine.run(sim)
        assert sim.result is not None

    def test_run_transitions_state(self, engine):
        sim = engine.spin_up("This statement is false.")
        engine.run(sim)
        assert sim.state in (SimulationState.BOUNDED, SimulationState.COMPLETED)

    def test_run_issues_containment_sig(self, engine):
        sim = engine.spin_up("This statement is false.")
        engine.run(sim)
        assert sim.containment_signature is not None
        assert sim.containment_signature.startswith("CSIG:")

    def test_run_records_transition_history(self, engine):
        sim = engine.spin_up("This statement is false.")
        engine.run(sim)
        states = [t.to_state.name for t in sim.transition_history]
        assert "RUNNING" in states

    def test_run_cannot_be_called_twice(self, engine):
        sim = engine.spin_up("This statement is false.")
        engine.run(sim)
        with pytest.raises(ValueError):
            engine.run(sim)


# ── Decay ─────────────────────────────────────────────────────────────────────

class TestDecay:
    def test_decay_archives(self, engine):
        sim = engine.spin_up("This statement is false.")
        engine.run(sim)
        engine.decay(sim)
        assert sim.state == SimulationState.ARCHIVED
        assert sim.vault_key is not None

    def test_decay_writes_to_vault(self, engine):
        sim = engine.spin_up("This statement is false.")
        engine.run(sim)
        engine.decay(sim)
        rec = engine.vault.retrieve(sim.vault_key)
        assert rec is not None
        assert rec.simulation_id == sim.simulation_id

    def test_destroy_path(self, fast_config, engine):
        fast_config.decay.auto_archive = False
        e2 = ParadoxEngine(config=fast_config)
        sim = e2.spin_up("This statement is false.")
        e2.run(sim)
        e2.decay(sim)
        assert sim.state == SimulationState.DESTROYED
        e2.shutdown()


# ── run_full ──────────────────────────────────────────────────────────────────

class TestRunFull:
    def test_run_full_returns_archived(self, engine):
        sim = engine.run_full("This statement is false.")
        assert sim.state in (SimulationState.ARCHIVED, SimulationState.DESTROYED)

    def test_run_full_library_liar(self, engine):
        sim = engine.run_full(ParadoxLibrary.get("liar"))
        assert sim.result is not None

    def test_run_full_library_russell(self, engine):
        sim = engine.run_full(ParadoxLibrary.get("russell"))
        assert sim.result is not None

    def test_run_full_all_library(self, engine):
        for p in ParadoxLibrary.all():
            sim = engine.run_full(p)
            assert sim.result is not None

    def test_audit_events_populated(self, engine):
        engine.run_full("This statement is false.")
        assert engine.audit.count() > 0

    def test_vault_populated(self, engine):
        engine.run_full("This statement is false.")
        assert engine.vault.count() > 0


# ── Shutdown ──────────────────────────────────────────────────────────────────

class TestShutdown:
    def test_shutdown_blocks_new_spinup(self, fast_config):
        from paradox_engine.core.engine import EngineShutdownError
        e = ParadoxEngine(config=fast_config)
        e.shutdown()
        with pytest.raises(EngineShutdownError):
            e.spin_up("This statement is false.")

    def test_status_shows_shutdown(self, fast_config):
        e = ParadoxEngine(config=fast_config)
        e.shutdown()
        assert e.status()["shutdown"] is True
