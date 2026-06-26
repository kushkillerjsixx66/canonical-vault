from time import sleep

from governance.stumpy.stumpy_engine import StumpyEngine
from epistemic.vara.vara_interface import VaraInterface


def test_epistemic_event_reaches_stumpy():
    stumpy = StumpyEngine()
    stumpy.start()

    eq = stumpy.event_queue
    vara = VaraInterface(eq)

    identity = {"operator_id": "op1", "role": "root", "sovereignty": "root"}
    runtime = {"altitude": "runtime"}

    vara.handle_veil_state(identity, runtime)

    sleep(0.3)

    violations = stumpy.get_violations()
    stumpy.stop()

    assert isinstance(violations, list)
    assert len(violations) == 0
