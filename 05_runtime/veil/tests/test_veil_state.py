from multiprocessing import Queue
from ..veil_interface import VeilInterface
from ...vara.vara_interface import VaraInterface


def test_veil_emits_runtime_state():
    eq = Queue()
    vara = VaraInterface(eq)
    veil = VeilInterface(eq, vara)

    identity = {"operator_id": "op1", "role": "root", "sovereignty": "root"}
    raw_state = {"altitude": "runtime", "posture": "focused"}

    veil.submit_runtime_update(identity, raw_state)

    assert not eq.empty()
    event = eq.get()

    assert event["type"] == "runtime_state"
    assert event["source"] == "veil"
    payload = event["payload"]

    assert payload["identity"]["operator_id"] == "op1"
    assert payload["altitude"] == "runtime"
    assert payload["posture"] == "focused"
