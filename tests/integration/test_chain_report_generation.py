from time import sleep

from governance.stumpy.stumpy_engine import StumpyEngine
from epistemic.vara.vara_interface import VaraInterface
from runtime.veil.veil_interface import VeilInterface


def test_report_generation():
    stumpy = StumpyEngine()
    stumpy.start()

    eq = stumpy.event_queue
    vara = VaraInterface(eq)
    veil = VeilInterface(eq, vara)

    identity = {"operator_id": "op1", "role": "root", "sovereignty": "root"}

    # Trigger a violation
    raw_state = {"altitude": "invalid", "posture": "neutral"}
    veil.submit_runtime_update(identity, raw_state)

    sleep(0.5)

    report = stumpy.generate_report()
    stumpy.stop()

    assert "Total violations" in report
    assert "runtime" in report or "altitude" in report
