from time import sleep

from governance.stumpy.stumpy_engine import StumpyEngine
from epistemic.vara.vara_interface import VaraInterface
from runtime.veil.veil_interface import VeilInterface


def test_runtime_to_stumpy_chain():
    stumpy = StumpyEngine()
    stumpy.start()

    eq = stumpy.event_queue
    vara = VaraInterface(eq)
    veil = VeilInterface(eq, vara)

    identity = {"operator_id": "op1", "role": "root", "sovereignty": "root"}
    raw_state = {"altitude": "runtime", "posture": "neutral"}

    veil.submit_runtime_update(identity, raw_state)

    sleep(0.3)

    violations = stumpy.get_violations()
    stumpy.stop()

    assert isinstance(violations, list)
    assert len(violations) == 0
