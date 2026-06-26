from time import sleep

from governance.stumpy.stumpy_engine import StumpyEngine
from epistemic.vara.vara_interface import VaraInterface
from runtime.veil.veil_interface import VeilInterface


def test_full_violation_flow():
    stumpy = StumpyEngine()
    stumpy.start()

    eq = stumpy.event_queue
    vara = VaraInterface(eq)
    veil = VeilInterface(eq, vara)

    identity = {"operator_id": "op1", "role": "root", "sovereignty": "root"}

    # Force a violation: invalid altitude
    raw_state = {"altitude": "nonsense", "posture": "neutral"}

    veil.submit_runtime_update(identity, raw_state)

    sleep(0.5)

    violations = stumpy.get_violations()
    stumpy.stop()

    assert len(violations) >= 1
    assert any(v["type"] in ("altitude_drift",
                             "runtime_violation",
                             "runtime_enforcement_triggered")
               for v in violations)
